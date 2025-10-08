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
