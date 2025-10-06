import logging


from .utils import execute_test_process
from job_history import append_job_history


def test_prompt_process(user_id, file_name, dataframe, description_json):
    job_title = description_json["job_title"]
    prompt = description_json["prompt"]
    placeholder_field = description_json["placeholder_field"]
    unique_id_field = description_json["unique_id_field"]
    output_field = description_json["output_field"]
    chunk_size = description_json["config"]["chunkSize"]
    credentials = description_json["credentials"]

    result = execute_test_process(
        dataframe=dataframe,
        job_title=job_title,
        prompt=prompt,
        placeholder_field=placeholder_field,
        unique_id_column=unique_id_field,
        output_field=output_field,
        chunk_size=chunk_size,
        credentials=credentials,
    )

    # Save test job summary in database (.csv)
    try:
        job_data = {
            "job_title": job_title,
            "file_name": file_name,
            "job_type": "test-job",
            "status": "completed",
            "total_rows_processed": result["total_test_rows_processed"],
            "model": credentials["deploymentName"],
            "avg_input_token": result["average_input_token"],
            "avg_completion_token": result["average_completion_token"],
            "avg_total_token": result["average_total_token"],
            "avg_cost_per_row": result["average_cost_per_row"],
            "prompt": [prompt]
        }
        append_job_history(user_id, job_data)
    except Exception as err:
        logging.info(f"Got error while appending test-job: {err}")

    return result
