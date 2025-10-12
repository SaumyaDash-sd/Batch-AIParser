import io
import ast
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


def handling_gpt_output(gpt_response: str) -> dict:
    """
    Attempts to parse the provided GPT response as a list or dictionary.
    If that fails, extracts the content between the first and last curly braces
    and parses it using ast.literal_eval.

    Args:
        gpt_response (str): The GPT response to be parsed.

    Returns:
        dict: The parsed GPT response as a dictionary, or an empty dictionary if parsing fails.
    """
    try:
        # Attempt to parse the entire response
        parsed = ast.literal_eval(gpt_response)
        if isinstance(parsed, (dict, list)):
            return parsed
        else:
            pass
    except Exception as e:
        pass
    # Fallback: extract content between the first and last curly braces
    try:
        start_index = gpt_response.find("{")
        end_index = gpt_response.rfind("}")
        if start_index != -1 and end_index != -1:
            extracted_content = gpt_response[start_index : end_index + 1]
            parsed = ast.literal_eval(extracted_content)
            return parsed
    except Exception as inner_e:
        pass
    return {}


def convert_df_to_bytes(
    output_df: pd.DataFrame,
    max_preview: int = 20,
) -> dict:
    buffer = io.StringIO()
    output_df.to_csv(buffer, index=False)
    csv_bytes = buffer.getvalue().encode("utf-8")
    encoded_file = base64.b64encode(csv_bytes).decode("utf-8")

    total_rows = len(output_df)

    # Fill NaN values for JSON serialization compatibility
    row_preview = output_df.head(max_preview).fillna("N/A").to_dict(orient="records")

    summary = {
        "total_test_rows_processed": total_rows,
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
