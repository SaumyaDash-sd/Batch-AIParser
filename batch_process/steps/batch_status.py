def check_batch_progress(client, batch_id):
    try:
        # Monitor the batch status
        status = "validating"
        batch_response = client.batches.retrieve(batch_id)  # Fetch updated batch info
        status = batch_response.status

        if batch_response.status == "failed":
            return {"status": "failed", "output_file_id": None, "error": None}
        if batch_response.status == "completed":
            output_file_id = batch_response.output_file_id
            return {"status": "completed", "output_file_id": output_file_id, "error": None}

        return {"status": status, "output_file_id": None, "error": None}
    except Exception as err:
        return {"status": "invalid-batch-id", "output_file_id": None, "error": err}
