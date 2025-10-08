import io
import base64
import threading
import pandas as pd
import logging
import json
import re
import time


from tqdm import tqdm
from dotenv import load_dotenv
from openai import AzureOpenAI


# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def genai_keyword_category_mapping(
    row,
    job_title,
    prompt,
    placeholder_field,
    unique_id_column,
    output_field,
    credentials,
):
    """
    Processes a single row.
    - NEW: Includes comprehensive try-except block to catch any error during a row's processing.
    - On error, it returns the original row data with an 'error' column.
    - On success, it returns the original data plus the AI-generated output.
    """
    try:
        # ---- Step 1: Fill placeholders dynamically ----
        prompt_filled = prompt
        placeholders = re.findall(r"\{\{(.*?)\}\}", prompt)

        for placeholder in placeholders:
            column_name = placeholder_field.get(placeholder)
            if column_name and column_name in row and pd.notna(row[column_name]):
                value = str(row[column_name])
            else:
                value = f"<MISSING_{placeholder}>"
            prompt_filled = prompt_filled.replace(f"{{{{{placeholder}}}}}", value)

        # ---- Step 2: Call GPT ----
        gpt_response, usage = call_gpt_llm_client(
            prompt_filled,
            credentials,
            model=credentials.get("deploymentName", "gpt-4o-mini"),
            temperature=credentials.get("temperature", 0.7),
        )
        handled_output = handling_gpt_output(gpt_response)

        # Prepare successful result
        result = row.to_dict()
        result[unique_id_column] = row[unique_id_column]

        # ---- Step 3: Map output to new dataframe columns ----
        for new_col, gpt_key in handled_output.items():
            result[new_col] = gpt_key
        # for new_col in output_field.values():
        #     # Get the corresponding key from the handled_output, default to None if not found
        #     result[new_col] = handled_output.get(new_col, None)

        # Add token usage and error column (as None for success)
        result["total_tokens"] = usage.total_tokens if usage else None
        result["input_tokens"] = usage.prompt_tokens if usage else None
        result["completion_tokens"] = usage.completion_tokens if usage else None
        result["error"] = None  # No error on success

    except Exception as err:
        logging.error(
            f"Error processing row with ID '{row.get(unique_id_column, 'N/A')}': {err}"
        )

        # ---- Error Handling Step: Prepare error result ----
        result = row.to_dict()
        result[unique_id_column] = row[unique_id_column]

        result["total_tokens"] = None
        result["input_tokens"] = None
        result["completion_tokens"] = None
        result["error"] = str(err)  # Add the error message to the 'error' column

    return result


def call_gpt_llm_client(
    prompt, credentials, model="gpt-4o-mini", temperature=0.3, time_delay=60
):
    """
    Calls Azure GPT LLM client and handles retries.
    """
    client = AzureOpenAI(
        api_key=credentials.get("apiKey"),
        azure_endpoint=credentials.get("endpoint"),
        api_version=credentials.get("api_version", "2024-05-01-preview"),
    )

    retries = 3
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": prompt}],
                temperature=temperature,
            )
            return response.choices[0].message.content, response.usage
        except Exception as e:
            logging.warning(f"Retry {attempt + 1}/{retries} failed: {e}")
            if attempt < retries - 1:
                time.sleep(time_delay)
            else:
                # If this is the last retry, re-raise the exception
                raise e
    # This line is technically unreachable due to the raise in the loop but is good practice
    raise RuntimeError("Max retries exceeded in GPT call")


def handling_gpt_output(gpt_response):
    """
    Extracts and formats GPT response into JSON safely.
    - Finds content between the first '{' and last '}'.
    - Parses it into a dict if valid JSON.
    - If no braces exist, returns the raw output.
    """
    if not gpt_response:
        return {}

    # Find JSON substring between first '{' and last '}'
    match = re.search(r"\{.*\}", gpt_response, re.DOTALL)
    if match:
        json_str = match.group(0).strip()
        try:
            parsed = json.loads(json_str)
            if isinstance(parsed, dict):
                return parsed
            return {"raw_output": parsed}
        except Exception:
            return {
                "raw_output": json_str
            }  # Return extracted string if JSON parsing fails

    # No curly braces found → return raw response
    return {"raw_output": gpt_response.strip()}


def execute_threads(
    dataframe,
    job_title,
    prompt,
    unique_id_column,
    placeholder_field,
    output_field,
    credentials,
    thread_count,
):
    """
    Multithreaded processing of rows.
    Manages its own local list for results.
    """
    local_output_list = []
    output_lock = threading.Lock()

    threads = []
    progress = tqdm(total=len(dataframe), desc="Processing Rows")

    def worker(rows):
        for _, row in rows.iterrows():
            result = genai_keyword_category_mapping(
                row,
                job_title,
                prompt,
                placeholder_field,
                unique_id_column,
                output_field,
                credentials,
            )
            with output_lock:
                local_output_list.append(result)

            progress.update(1)

    thread_chunk_size = len(dataframe) // thread_count
    for i in range(thread_count):
        start = i * thread_chunk_size
        end = None if i == thread_count - 1 else (i + 1) * thread_chunk_size
        thread = threading.Thread(target=worker, args=(dataframe.iloc[start:end],))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    progress.close()

    return pd.DataFrame(local_output_list)


def generate_summary_json(
    output_df: pd.DataFrame,
    input_token_cost: float,
    completion_token_cost: float,
    max_preview: int = 20,
) -> dict:
    """
    Generate summary statistics and preview JSON for frontend.
    - NEW: Handles potential None/NaN values in token columns for robust calculations.
    """
    buffer = io.StringIO()
    output_df.to_csv(buffer, index=False)
    csv_bytes = buffer.getvalue().encode("utf-8")
    encoded_file = base64.b64encode(csv_bytes).decode("utf-8")

    total_rows = len(output_df)

    # Use pd.to_numeric to safely convert, coercing errors to NaN, then fill with 0
    input_tokens = pd.to_numeric(output_df["input_tokens"], errors="coerce").fillna(0)
    completion_tokens = pd.to_numeric(
        output_df["completion_tokens"], errors="coerce"
    ).fillna(0)
    total_tokens = pd.to_numeric(output_df["total_tokens"], errors="coerce").fillna(0)

    avg_input_tokens = input_tokens.mean()
    avg_completion_tokens = completion_tokens.mean()
    avg_total_tokens = total_tokens.mean()

    avg_cost_per_row = (avg_input_tokens * input_token_cost) + (
        avg_completion_tokens * completion_token_cost
    )
    # Fill NaN values for JSON serialization compatibility
    row_preview = output_df.head(max_preview).fillna("N/A").to_dict(orient="records")

    summary = {
        "total_test_rows_processed": total_rows,
        "average_input_token": round(avg_input_tokens, 2),
        "average_completion_token": round(avg_completion_tokens, 2),
        "average_total_token": round(avg_total_tokens, 2),
        "average_cost_per_row": float(f"{avg_cost_per_row:.20f}"),
        "row_preview_data": row_preview,
        "file_data": encoded_file,
    }
    return summary


def execute_test_process(
    dataframe,
    job_title,
    prompt,
    unique_id_column,
    placeholder_field,
    output_field,
    chunk_size,
    credentials,
):
    """
    Main function to execute the process.
    - NEW: Checks if unique_id_column is provided. If not, it creates a default one.
    """

    # ---- NEW: Handle null unique_id_column ----
    if not unique_id_column:
        unique_id_column = "unique_id"
        logging.info(
            f"No unique_id_column provided. Creating new column '{unique_id_column}'."
        )
        # Ensure the new column name doesn't already exist
        if unique_id_column in dataframe.columns:
            raise ValueError(
                f"Default ID column '{unique_id_column}' already exists in the dataframe. Please provide a unique column name."
            )
        # Assign incrementing integers as the unique ID
        dataframe[unique_id_column] = range(1, len(dataframe) + 1)

    test_df = dataframe.head(chunk_size)

    output_df = execute_threads(
        test_df,
        job_title,
        prompt,
        unique_id_column,
        placeholder_field,
        output_field,
        credentials,
        thread_count=10,
    )

    output_df.to_csv("test-output.csv", index=False)
    logging.info("✅ Content generation completed and saved to 'test-output.csv'")

    cost_per_input_token = 0.00000015
    cost_per_completion_token = 0.0000006

    final_output = generate_summary_json(
        output_df,
        input_token_cost=cost_per_input_token,
        completion_token_cost=cost_per_completion_token,
        max_preview=20,
    )
    final_output["job_title"] = job_title
    
    return final_output


# -------------------------
# Example Run
# -------------------------

# if __name__ == "__main__":
#     dataframe = pd.read_excel(
#         "/Users/harishankarvashishtha/Learning/PERSONAL-WORK-GITHUB/Batch-AIParser/sample_file.xlsx"
#     )

#     job_title = "my1st_job title"
#     prompt = """
#     You have to return 5 keywords which user searches for this category: '{{category}}'.
#     Return output in below JSON format only:
#     {
#       'five_keywords': [list of 5 keywords]
#     }
#     """

#     placeholder_field = {"category": "category_name"}
#     unique_id_column = "national_catid"

#     # Mapping: output column → key from GPT JSON
#     output_field = {"keywords": "five_keywords"}

#     credentials = {
#         "apiKey": "49399de06f4c413db072e580c470b443",
#         "endpoint": "https://gpt4omini-exp.openai.azure.com/",  # FIXED
#         "deploymentName": "gpt4omini-exp",
#         "temperature": 0.7,
#     }

#     result_df = execute_test_process(
#         dataframe.head(5),
#         job_title,
#         prompt,
#         unique_id_column,
#         placeholder_field,
#         output_field,
#         chunk_size=5,
#         credentials=credentials,
#     )
#     print(result_df)
