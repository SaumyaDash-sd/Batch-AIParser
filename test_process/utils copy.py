import os
import threading
import pandas as pd
import time
import logging
import json
from tqdm import tqdm
from dotenv import load_dotenv
from openai import AzureOpenAI
import re

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Global variable for storing results
output_list = []
output_lock = threading.Lock()


# -------------------------
# GPT Client
def call_gpt_llm_client(prompt, credentials, model: str = "gpt-4o", temperature=0.5, time_delay=65):
    """
    Calls Azure GPT LLM client and handles retries.
    """
    client = AzureOpenAI(
        api_key=credentials.get("azure_openai_api_key"),
        azure_endpoint=credentials.get("azure_endpoint"),
        api_version=credentials.get("azure_openai_api_version"),
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return response.choices[0].message.content, response.usage
    except Exception as e:
        logging.exception(f"Error calling GPT client: {e}")
        return None, None


# ---------------- Output Handling ---------------- #
def handling_gpt_output(gpt_response: str):
    """
    Extracts and formats the GPT response.
    """
    try:
        return {"new_content": gpt_response.strip()}
    except Exception as e:
        logging.exception(f"Error handling GPT output: {e}")
        return {"new_content": ""}



# -------------------------
# def call_gpt_llm_client(prompt, model: str = "gpt-4o", temperature=0.5, time_delay=65):
#     """
#     Calls Azure GPT LLM client and handles retries.
#     """
#     client = AzureOpenAI(
#         api_key=os.getenv("azure_openai_api_key"),
#         azure_endpoint=os.getenv("azure_endpoint"),
#         api_version=os.getenv("azure_openai_api_version"),
#     )

#     conversations = [
#         {"role": "system", "content": prompt},
#         {
#             "role": "user",
#             "content": "Please return only the JSON object. No additional text, no explanations.",
#         },
#     ]

#     try:
#         response = client.chat.completions.create(
#             model=model,
#             messages=conversations,
#             temperature=temperature,
#         )
#         gpt_response = response.choices[0].message.content
#         return gpt_response, response.usage
#     except Exception as err:
#         logging.exception(
#             f"Error calling GPT LLM client: {err}. Retrying in {time_delay} seconds..."
#         )
#         time.sleep(time_delay)
#         # Retry once
#         response = client.chat.completions.create(
#             model=model, messages=conversations, temperature=0.5
#         )
#         gpt_response = response.choices[0].message.content
#         return gpt_response, response.usage


# # -------------------------
# # GPT Output Parser
# # -------------------------
# def handling_gpt_output(gpt_response):
#     """
#     Parses the GPT response, ensuring strict JSON handling.
#     """
#     try:
#         parsed_output = json.loads(gpt_response.strip())
#         if not isinstance(parsed_output, dict):
#             raise ValueError("Parsed output is not a dictionary.")
#         return parsed_output
#     except json.JSONDecodeError as e:
#         logging.error(f"Failed to parse GPT response as JSON: {e}")
#         logging.debug(f"Received response: {gpt_response}")
#         return {}


# # -------------------------
# # Row Processor
# # -------------------------
# def genai_keyword_category_mapping(
#     row, job_title, prompt, placeholder_field, unique_id_column, output_field, chunk_size, credentials
# ):
#     """
#     Processes a single row - calls GPT for content generation and handles the response.
#     """
#     input_col1_name = unique_id_column
#     input_col2_name = placeholder_field
#     new_col1 = "new_content"
#     id_val = row[input_col1_name]
#     cat = row[input_col2_name]
#     prompt = prompt
#     f"""Write informative content for the category = '{cat}'. Create engaging and relevant content. Using keyword research related to '{cat}' to identify high-impact keywords and incorporate them strategically into our content. Write in-depth in 1000 words that provides valuable insights into '{cat}' in <area>,<city> and its relevance to our target audience. Do not use the word keyword anywhere within the content. Avoid using brand names and include topic-related LSI keywords and synonyms. Do not use word keywords, topics, trends and LSI anywhere within the content. do not write anything about brand, manufacturer, importer, and exporters and company in the content. Organize content by including bullet pointers for important information. Enclose each paragraphs by <p> and </p> tags. Enclose each list by <li> and </li> tags. Write SEO-rich content with <area>, <city> after category name in headings and subheadings, with only one <h2> tag at the beginning and the rest as <h3> tags. Ensure the entire content is presented in 3rd person language without using 'we,' 'our,' 'I,' etc. Add <area>, <city> in main heading after category.
#     "output": {{
#         "new_content": "",
#     }}
#     """

#     gpt_response = None
#     token_usage = None

#     try:
#         gpt_response, usage = call_gpt_llm_client(prompt)
#         handled_output = handling_gpt_output(gpt_response)
#         token_usage = usage.total_tokens if usage else "N/A"
#     except Exception as err:
#         logging.exception(f"Error in GPT processing: {err}")
#         handled_output = {}

#     Term = handled_output.get("new_content", "N/A")

#     with output_lock:
#         output_list.append(
#             {
#                 input_col1_name: id_val,
#                 input_col2_name: cat,
#                 new_col1: Term,
#                 "token_usage": token_usage,
#             }
#         )

# ---------------- Dynamic Function ---------------- #
def genai_keyword_category_mapping(
    row, job_title, prompt, placeholder_field, unique_id_column, output_field, chunk_size, credentials
):
    """
    Processes a single row - dynamically replaces placeholders in the prompt 
    with values from the dataframe row and calls GPT.
    """

    # Get dynamic placeholders from the prompt (e.g. {cat}, {name})
    placeholders = re.findall(r"\{(.*?)\}", prompt)

    # Replace placeholders with row values
    prompt_filled = prompt
    for placeholder in placeholders:
        if placeholder in row:
            prompt_filled = prompt_filled.replace(f"{{{placeholder}}}", str(row[placeholder]))
        else:
            prompt_filled = prompt_filled.replace(f"{{{placeholder}}}", f"<MISSING_{placeholder}>")

    # Unique id value for tracking
    id_val = row[unique_id_column]

    # Call GPT
    gpt_response, usage = None, None
    try:
        gpt_response, usage = call_gpt_llm_client(prompt_filled, credentials)
        handled_output = handling_gpt_output(gpt_response)
        token_usage = usage.total_tokens if usage else "N/A"
    except Exception as err:
        logging.exception(f"Error in GPT processing: {err}")
        handled_output = {"new_content": ""}

    Term = handled_output.get("new_content", "N/A")

    # Prepare output dictionary
    result = {
        unique_id_column: id_val,
        output_field: Term,
        "token_usage": token_usage,
    }

    return result



# 👉 Next, in your router, after converting description to JSON and loading the dataframe, you can run like this:

# results = []
# for _, row in dataframe.iterrows():
#     result = genai_keyword_category_mapping(row, description_json)
#     results.append(result)



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
                unique_id_column,
                placeholder_field,
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


"""
{
    "job_title": "Testing prompt for Keywords",
    "prompt": "Hey GPT, can you check the Department name: {{department_name}} and suggest me whether it is meaningful or not in True or False.\nIf it is not meanignful then suggest a department name related to it.\nAnd can you check the user name: {{users_name}} is it a real name of user or not in True or False, if not real then suggest name also.\nYou have to return your output in below JSON format only, not in any other format:\n{\n\"department_name\": \"Original name of the department\",\n\"meaningful_department_name\": True or False,\n\"suggested_department_name\": \"Suggest related department name\",\n\"original_name\": \"Original name of the user\",\n\"meaningful_user_name\": True or False,\n\"suggested_user_name\": \"Suggest related user name\"\n}\n",
    "placeholder_field": {
      "department_name": "department",
      "users_name": "name"
    },
    "unique_id_field": null,
    "output_field": {
      "department_name": "Original name of the department",
      "meaningful_department_name": "True or False",
      "suggested_department_name": "Suggest related department name",
      "original_name": "Original name of the user",
      "meaningful_user_name": "True or False",
      "suggested_user_name": "Suggest related user name"
    },
    "config": {
      "chunkSize": 20
    },
    "credentials": {
      "endpoint": "https://hari-pulse-abg.openai.azure.com/",
      "apiKey": "openai_api_key_askdsdnsdkadnkas",
      "deploymentName": "gpt-4o-mini",
      "temperature": 0.7
    }
  }

"""


def main_1(
    dataframe,
    job_title,
    prompt,
    unique_id_column,
    placeholder_field,
    output_field,
    chunk_size,
    credentials,
):
    
    # Process with threading
    output_df = execute_threads(
        dataframe,
        job_title,
        prompt,
        unique_id_column,
        placeholder_field,
        output_field,
        chunk_size,
        credentials,
        thread_count=20,
    )

    # Save results
    output_df.to_csv("output.csv", index=False)
    print(
        "✅ Content generation completed and saved to 'remainining_338_aug_attribute_footer_file.xlsx'"
    )
    

prompt = """
You have to return 5 keywords which user searches for this category: '{{category}}'.
Return output in below JSON format only:
{
"five_keywords": "[list of five_keywords_that_user_searches]"
}
"""

if __name__ == "__main__":
    dataframe = pd.read_excel(r"C:\Users\10163441\Desktop\my_personal_github\Batch-AIParser\sample_file.xlsx")
    job_title = "my1st_job title"
    prompt = prompt
    unique_id_column = "national_catid"
    placeholder_field = {"category": "category_name"}
    output_field = {"five_keywords": "[five_keywords_that_user_searches]"}
    chunk_size = 5
    credentials = {"apiKey" : "49399de06f4c413db072e580c470b443",
        "endpoint" : "https://gpt4omini-exp.openai.azure.com/openai/deployments/gpt4omini-exp/chat/completions?",
        "deploymentName" : "gpt4omini-exp",
        "temperature": 0.7}


    result = main_1(
    dataframe,
    job_title,
    prompt,
    unique_id_column,
    placeholder_field,
    output_field,
    chunk_size,
    credentials,    
    )

#column names: 
# national_catid:10042247

# category_name: Beauty Parlours

