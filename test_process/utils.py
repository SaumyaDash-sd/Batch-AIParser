import os
import threading
import pandas as pd
import logging
import json
from tqdm import tqdm
from dotenv import load_dotenv
from openai import AzureOpenAI
import re
import time

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Global variables
output_list = []
output_lock = threading.Lock()


def genai_keyword_category_mapping(
    row,
    job_title,
    prompt,
    placeholder_field,
    unique_id_column,
    output_field,
    chunk_size,
    credentials,
):
    """
    Processes a single row:
    1. Fills placeholders in prompt using row values mapped from placeholder_field.
    2. Calls GPT with filled prompt.
    3. Parses GPT response into structured output.
    4. Appends enriched row dictionary to global results.
    """

    # ---- Step 1: Fill placeholders dynamically ----
    prompt_filled = prompt
    placeholders = re.findall(r"\{\{(.*?)\}\}", prompt)  # find {{placeholder}}

    for placeholder in placeholders:
        column_name = placeholder_field.get(placeholder)
        if column_name and column_name in row:
            value = str(row[column_name])
        else:
            value = f"<MISSING_{placeholder}>"
        prompt_filled = prompt_filled.replace(f"{{{{{placeholder}}}}}", value)

    # ---- Step 2: Call GPT ----
    try:
        gpt_response, usage = call_gpt_llm_client(
            prompt_filled,
            credentials,
            model=credentials.get("deploymentName", "gpt-4o-mini"),
            temperature=credentials.get("temperature", 0.7),
        )
        handled_output = handling_gpt_output(gpt_response)
        prompt_usage = usage.prompt_tokens if usage else "N/A"
        completion_usage = usage.completion_tokens if usage else "N/A"
        token_usage = usage.total_tokens if usage else "N/A"
    except Exception as err:
        logging.exception(f"Error in GPT processing: {err}")
        handled_output, token_usage = {"error": str(err)}, "N/A"

    # ---- Step 3: Map output to new dataframe columns ----
    result = row.to_dict()  # keep original row
    result[unique_id_column] = row[unique_id_column]

    for new_col, gpt_key in output_field.items():
        result[new_col] = handled_output.get(gpt_key, "")

    result["total_tokens"] = token_usage
    result["input_tokens"] = prompt_usage
    result["completion_tokens"] = completion_usage

    # Append to global list safely
    with output_lock:
        output_list.append(result)

    return result


def call_gpt_llm_client(prompt, credentials, model="gpt-4o", temperature=0.5, time_delay=60):
    """
    Calls Azure GPT LLM client and handles retries.
    """
    client = AzureOpenAI(
        api_key=credentials.get("apiKey"),
        azure_endpoint=credentials.get("endpoint"),  # must be just base endpoint
        api_version=credentials.get("api_version", "2024-05-01-preview"),
    )

    retries = 3
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
            )
            return response.choices[0].message.content, response.usage
        except Exception as e:
            logging.warning(f"Retry {attempt+1}/{retries} failed: {e}")
            time.sleep(time_delay)
    raise RuntimeError("Max retries exceeded in GPT call")


def handling_gpt_output(gpt_response: str):
    """
    Extracts and formats GPT response into JSON safely.
    """
    if not gpt_response:
        return {}

    try:
        parsed = json.loads(gpt_response)
        if isinstance(parsed, dict):
            return parsed
        return {"raw_output": parsed}
    except Exception:
        return {"raw_output": gpt_response.strip()}


# -------------------------
# Threaded Execution
# -------------------------
def execute_threads(
    dataframe,
    job_title,
    prompt,
    unique_id_column,
    placeholder_field,
    output_field,
    chunk_size,
    credentials,
    thread_count,
):
    """
    Multithreaded processing of rows.
    """
    threads = []
    progress = tqdm(total=len(dataframe), desc="Processing Rows")

    def worker(rows):
        for _, row in rows.iterrows():
            genai_keyword_category_mapping(
                row,
                job_title,
                prompt,
                placeholder_field,
                unique_id_column,
                output_field,
                chunk_size,
                credentials,
            )
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
    return pd.DataFrame(output_list)


def main(
    dataframe,
    job_title,
    prompt,
    unique_id_column,
    placeholder_field,
    output_field,
    chunk_size,
    credentials,
):
    output_df = execute_threads(
        dataframe,
        job_title,
        prompt,
        unique_id_column,
        placeholder_field,
        output_field,
        chunk_size,
        credentials,
        thread_count=10,  # adjust based on workload
    )

    output_df.to_csv("output1.csv", index=False)
    logging.info("✅ Content generation completed and saved to 'output.csv'")
    return output_df


# -------------------------
# Example Run
# -------------------------
if __name__ == "__main__":
    dataframe = pd.read_excel(
        r"C:\Users\10163441\Desktop\my_personal_github\Batch-AIParser\sample_file.xlsx"
    )

    job_title = "my1st_job title"
    prompt = """
    You have to return 5 keywords which user searches for this category: '{{category}}'.
    Return output in below JSON format only:
    {
      "five_keywords": ["list", "of", "five", "keywords", "searched"]
    }
    """

    placeholder_field = {"category": "category_name"}
    unique_id_column = "national_catid"

    # Mapping: output column → key from GPT JSON
    output_field = {"keywords": "five_keywords"}

    credentials = {
        "apiKey": "49399de06f4c413db072e580c470b443",
        "endpoint": "https://gpt4omini-exp.openai.azure.com/",  # FIXED
        "deploymentName": "gpt4omini-exp",
        "temperature": 0.7,
    }

    result_df = main(
        dataframe.head(5),
        job_title,
        prompt,
        unique_id_column,
        placeholder_field,
        output_field,
        chunk_size=5,
        credentials=credentials,
    )
    print(result_df.head())


    # Output CSV/Excel Download Button
    # Output file sample preview (20 rows)
    # Average of Input tokens
    # Average of Completion tokens
    # Average of Total tokens
    # Average cost per row
