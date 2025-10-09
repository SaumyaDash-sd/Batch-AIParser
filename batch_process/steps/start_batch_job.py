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


from batch_history import get_openai_client, get_chunk_no_and_row_count


def check_batch_status(client, batch_id):
    # Monitor the batch status
    status = "validating"
    batch_response = client.batches.retrieve(batch_id)  # Fetch updated batch info
    status = batch_response.status

    if batch_response.status == "completed":
        output_file_id = batch_response.output_file_id
        return batch_id, output_file_id, status
    else:
        return batch_id, None, status


def start_batch(client, file_id, endpoint="/chat/completions", completion_window="24h"):
    """
    Starts a batch request for a given uploaded file on the client.

    Parameters:
        client: The API client object (e.g., OpenAI client).
        file_id (str): The ID of the uploaded JSONL file.
        endpoint (str): The endpoint for the batch request (default: "/chat/completions").
        completion_window (str): Time window for batch completion (default: "24h").

    Returns:
        str: The batch ID of the submitted batch.
    """
    # Create the batch
    batch_response = client.batches.create(
        input_file_id=file_id, endpoint=endpoint, completion_window=completion_window
    )

    # Return the batch ID
    return batch_response.id


def start_process(user_id, job_id, list_of_file_ids):
    client = get_openai_client(user_id, job_id)
    batch_jobs_data = []
    for index, file_id in enumerate(list_of_file_ids, start=1):
        chunk_no, total_rows_processed = get_chunk_no_and_row_count(
            user_id, job_id, file_id
        )
        batch_id = start_batch(client, file_id)
        batch_jobs_data.append(
            {
                "batch_id": batch_id,
                "file_id": file_id,
                "output_file_id": None,
                "status": "validating",
                "chunk_no": chunk_no,
                "total_rows_processed": total_rows_processed,
            }
        )
    final_batch_job_data = []
    for index, batch in enumerate(batch_jobs_data, start=1):
        batch_id, output_file_id, status = check_batch_status(client, batch["batch_id"])
        batch["status"] = status
        batch["output_file_id"] = output_file_id
        final_batch_job_data.append(batch)

    return final_batch_job_data


if __name__ == "__main__":
    file_id = "file-fcfdc94ffba640fbae5625edcdad2d89"  # previously uploaded file ID
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

    batch_id = start_batch(client, file_id)

    # batch_id = "batch_654dfadb-dd45-428d-adf7-1dba29731427"
    output = check_batch_status(client, batch_id)

    print(output)
