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


def download_file(client, file_id: str, save_path: str | Path | None = None) -> bytes:
    """
    Downloads a file from OpenAI given a file_id.

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


def download_batch_file(client, batch_id, output_file_path):
    file_response = client.files.content(batch_id)
    raw_responses = file_response.text.strip().split(
        "\n"
    )  # Split JSONL content into lines

    # Process each response and save to a new output file
    output_df = []
    for raw_response in tqdm(
        raw_responses, desc="Processing lines in chunk for batch", unit="line"
    ):
        try:
            json_response = json.loads(raw_response)
            output_df.append(json_response)  # Add response to list
        except json.JSONDecodeError as e:
            print(
                f"Error decoding JSON in chunk of batch no: {raw_response}\nError: {e}"
            )

    # Convert to DataFrame and save to CSV
    output_df = pd.DataFrame(output_df)
    output_df.to_csv(output_file_path, index=False)
    print(f"Output for batch no: saved to {output_file_path} \n")

    return f"Output for batch no: saved to {output_file_path}"


if __name__ == "__main__":
    file_id = "file-fcfdc94ffba640fbae5625edcdad2d89"
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
    download_file(client, file_id, "downloaded_test_output.jsonl")

    # Or just get bytes without saving
    file_bytes = download_file(client, file_id)
    print(f"Downloaded {len(file_bytes)} bytes")
