# Import necessary libraries
import io
import os
import re
import pandas as pd
import json
import time
import threading
from tqdm import tqdm
from openai import AzureOpenAI
from datetime import datetime


# def split_dataframe_into_chunks(dataframe, chunk_size):
#     """
#     Splits a DataFrame into smaller DataFrames of a given chunk size.

#     Parameters:
#         dataframe (pd.DataFrame): Input DataFrame.
#         chunk_size (int): Number of rows per chunk.

#     Returns:
#         List[pd.DataFrame]: List of DataFrames, each of size chunk_size (last chunk may be smaller).
#     """
#     chunks = [
#         dataframe.iloc[i : i + chunk_size] for i in range(0, len(dataframe), chunk_size)
#     ]
#     return chunks

def split_dataframe_into_chunks(dataframe, number_of_chunks):
    """
    Split dataframe into a fixed number of chunks.
    Each chunk will have roughly len(df) / number_of_chunks rows.
    """
    total_rows = len(dataframe)
    rows_per_chunk = total_rows // number_of_chunks
    chunks = []
    
    start = 0
    for i in range(number_of_chunks):
        # Last chunk takes all remaining rows
        if i == number_of_chunks - 1:
            chunks.append(dataframe.iloc[start : ])
        else:
            end = start + rows_per_chunk
            chunks.append(dataframe.iloc[start : end])
            start = end
    
    return chunks



def upload_dataframe_as_jsonl(
    df,
    prompt_col_name,
    unique_id_col_name,
    file_name,
    client,
    model_name,
    temperature=0.5,
):
    """
    Converts a DataFrame into JSONL format suitable for batch upload and uploads it to the client.

    Parameters:
        df (pd.DataFrame): Input DataFrame containing prompts and unique IDs.
        prompt_col_name (str): Name of the column containing prompts.
        unique_id_col_name (str): Name of the column containing unique IDs.
        client: The client object to upload the file (e.g., OpenAI client).
        model_name (str): Model name for completion.
        temperature (float): Temperature setting for model responses.

    Returns:
        str: Uploaded file ID.
    """

    # Create a bytes buffer
    jsonl_bytes = io.BytesIO()

    # Write each row as a JSON object to the buffer
    for _, row in df.iterrows():
        json_object = {
            "custom_id": row[unique_id_col_name],
            "method": "POST",
            "url": "/chat/completions",
            "body": {
                "model": model_name,
                "temperature": temperature,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": row[prompt_col_name]},
                ],
            },
        }
        jsonl_bytes.write((json.dumps(json_object) + "\n").encode("utf-8"))

    # Move buffer cursor to the beginning
    jsonl_bytes.seek(0)

    # Add a name attribute so OpenAI client knows the filename
    jsonl_bytes.name = f"{file_name}.jsonl"

    # Upload to client
    uploaded_file = client.files.create(file=jsonl_bytes, purpose="batch")

    # Return the file ID
    file_id = uploaded_file.id

    file_info = client.files.retrieve(file_id)
    status = file_info.status.lower()

    if status == "processed":
        return file_id, status
    else:
        return None, status


def start_process(dataframe, file_name, description_json):
    prompt_column_name = "prompt"
    unique_id_column_name = description_json["unique_id_field"] if description_json["unique_id_field"] else "unique_id"
    credentials = description_json["credentials"]
    config = description_json["config"]
    client = AzureOpenAI(
        api_key=credentials["apiKey"],
        azure_endpoint=credentials["endpoint"],
        api_version="2025-01-01-preview",
    )
    model_name = credentials["deploymentName"]
    temperature = credentials["temperature"]
    chunk_size = config["chunkSize"]

    dataframe_chunks_list = split_dataframe_into_chunks(dataframe, chunk_size)
    final_output = []
    for index, chunk in enumerate(dataframe_chunks_list, start=1):
        file_id, status = upload_dataframe_as_jsonl(
            chunk,
            prompt_column_name,
            unique_id_column_name,
            file_name,
            client,
            model_name,
            temperature,
        )
        final_output.append(
            {
                "file_id": file_id,
                "status": status,
                "chunk_no": f"chunk_{index}",
                "total_rows_processed": len(chunk),
            }
        )

    return final_output


if __name__ == "__main__":
    dataframe = pd.read_excel("test output.xlsx")
    unique_id_column_name = "UNIQUE_ID"  # Column to be used as custom_id
    prompt_column_name = "prompt"
    file_name = "test output.jsonl"
    credentials = {
        "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "apiKey": os.getenv("AZURE_OPENAI_API_KEY"),
        "deploymentName": "gpt-4o-batch",
        "temperature": 0.3,
    }

    client = AzureOpenAI(
        api_key=credentials["apiKey"],
        azure_endpoint=credentials["endpoint"],
        api_version="2025-01-01-preview",
    )
    model_name = credentials["deploymentName"]
    temperature = credentials["temperature"]

    dataframe_chunks_list = split_dataframe_into_chunks(dataframe, 20)

    final_output = []
    for chunk in dataframe_chunks_list:
        output = upload_dataframe_as_jsonl(
            chunk,
            prompt_column_name,
            unique_id_column_name,
            file_name,
            client,
            model_name,
            temperature,
        )
        final_output.append(output)

    print(final_output)
