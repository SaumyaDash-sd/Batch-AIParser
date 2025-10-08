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


def check_batch_status(batch_id, client):
    # Monitor the batch status
    status = "validating"
    batch_response = client.batches.retrieve(batch_id)  # Fetch updated batch info
    status = batch_response.status

    if batch_response.status == "completed":
        output_file_id = batch_response.output_file_id
        return output_file_id, status
    else:
        return None, status


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
        input_file_id=file_id,
        endpoint=endpoint,
        completion_window=completion_window
    )
    
    # Return the batch ID
    return batch_response.id


if __name__ == "__main__":
    file_id = "file-fcfdc94ffba640fbae5625edcdad2d89" # previously uploaded file ID
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

    print("Batch started with ID:", batch_id)

    # batch_id = "batch_654dfadb-dd45-428d-adf7-1dba29731427"
    output = check_batch_status(batch_id, client)

    print(output)
