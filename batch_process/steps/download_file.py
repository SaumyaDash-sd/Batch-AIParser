# Import necessary libraries
import os
import re
import pandas as pd
import json
import time
import threading
from tqdm import tqdm
from openai import AzureOpenAI
from datetime import datetime
from pathlib import Path


from .utils import output_jsonl_to_dataframe, input_jsonl_to_dataframe
from .batch_status import check_batch_progress


def download_jsonl_file(
    client, file_id: str, save_path: str | Path | None = None
) -> bytes:
    """
    Downloads a josnl file from OpenAI given a file_id.

    Args:
        client: An instance of OpenAI client.
        file_id: The ID of the file to download.
        save_path: Optional path to save the file locally.

    Returns:
        The file content as bytes.
    """
    # Fetch the file content object
    file_content_obj = client.files.content(file_id)

    # Extract actual bytes
    file_bytes = file_content_obj.read()

    # Save if a path is provided
    if save_path:
        save_path = Path(save_path)
        save_path.write_bytes(file_bytes)

    return file_bytes


def download_jsonl_of_batch_id(
    client, batch_id: str, save_path: str | Path | None = None
) -> dict:
    """
    Downloads a jsonl file from OpenAI given a batch_id.

    Args:
        client: An instance of OpenAI client.
        batch_id: The ID of the batch to download.
        save_path: Optional path to save the file locally.

    Returns:
        The batch status json along with file content as bytes.
    """

    # Monitor the batch status
    response = check_batch_progress(client, batch_id)
    if response["status"] == "completed":
        # Fetch the file content object
        file_content_obj = client.files.content(response["output_file_id"])

        # Extract actual bytes
        file_bytes = file_content_obj.read()

        # Save if a path is provided
        if save_path:
            save_path = Path(save_path)
            save_path.write_bytes(file_bytes)
        response["file_bytes"] = file_bytes
        return response
    return response


def download_csv_of_batch_output_file(
    client, file_id: str, save_path: str | Path | None = None
) -> pd.DataFrame:
    output_jsonl_file_bytes = download_jsonl_file(client, file_id)
    dataframe = output_jsonl_to_dataframe(output_jsonl_file_bytes)
    # Save if a path is provided
    if save_path:
        dataframe.to_excel(save_path, index=False)
    return dataframe


def download_csv_of_batch_input_file(
    client, file_id: str, save_path: str | Path | None = None
) -> pd.DataFrame:
    input_jsonl_file_bytes = download_jsonl_file(client, file_id)
    dataframe = input_jsonl_to_dataframe(input_jsonl_file_bytes)
    # Save if a path is provided
    if save_path:
        dataframe.to_excel(save_path, index=False)
    return dataframe


def download_csv_of_batch_id(
    client, batch_id: str, save_path: str | Path | None = None
) -> dict:
    """
    Downloads a csv file from OpenAI given a batch_id.

    Args:
        client: An instance of OpenAI client.
        batch_id: The ID of the batch to download.
        save_path: Optional path to save the file locally.

    Returns:
        The file status along with jsonl bytes and dataframe.
    """

    # Monitor the batch status
    response = download_jsonl_of_batch_id(client, batch_id)
    if response["status"] == "completed":
        # Fetch the file content object
        dataframe = output_jsonl_to_dataframe(response["file_bytes"])
        # Save if a path is provided
        if save_path:
            dataframe.to_excel(save_path, index=False)
        response["file_dataframe"] = dataframe
        return response
    return response


if __name__ == "__main__":
    input_jsonl_file_id = "file-fcfdc94ffba640fbae5625edcdad2d89"
    output_jsonl_file_id = "file-11450e4e-c75a-4d81-bd7c-3efa9113124a"
    batch_id = "batch_654dfadb-dd45-428d-adf7-1dba29731427"
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

    # Download and save locally
    # file_bytes = download_jsonl_file(client, file_id, "downloaded_test_output.jsonl")
    # print(f"Downloaded {len(file_bytes)} bytes")

    # Or just get bytes without saving
    # dataframe = download_csv_of_batch_input_file(
    #     client, input_jsonl_file_id, "downloaded_test_input.xlsx"
    # )
    # print(f"Downloaded {len(dataframe)} rows")

    # Or just get bytes without saving
    dataframe = download_csv_of_batch_output_file(
        client, output_jsonl_file_id, "downloaded_test_output.xlsx"
    )
    print(f"Downloaded {len(dataframe)} rows")

    # Or just get bytes without saving
    # dataframe = download_jsonl_of_batch_id(
    #     client, batch_id, "batch_id_downloaded_test_output.jsonl"
    # )
    # print(f"Downloaded {len(dataframe['file_bytes'])} bytes")

    # Or just get bytes without saving
    dataframe = download_csv_of_batch_id(
        client, batch_id, "batch_id_downloaded_test_output.xlsx"
    )
    print(f"Downloaded {len(dataframe['file_dataframe'])} rows")
