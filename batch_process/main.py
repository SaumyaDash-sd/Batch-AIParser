import logging

from batch_history import (
    append_batch_job_history,
    append_uploaded_file_history,
    append_batch_file_history,
    get_openai_client,
)
from .utils import convert_df_to_bytes
from . import steps
from .steps.batch_status import check_batch_progress
from batch_history import (
    get_batch_status_and_output_file_id,
    update_batch_status_if_changed,
)


def batch_processing_create_and_upload_file(user_id, filename, df, description_json):
    output_df = steps.create_file.start_process(df, description_json["unique_id_field"])
    uploaded_files_list = steps.upload_file.start_process(
        output_df, filename, description_json
    )

    job_data = {
        "job_title": description_json.get("job_title", None),
        "file_name": filename,
        "job_type": "batch-job",
        "chunk_size": description_json.get("config", {}).get("chunkSize", 0),
        "chunks": len(uploaded_files_list),
        "total_rows_processed": len(output_df),
        "model": description_json.get("credentials", {}).get("deploymentName", "N/A"),
        "prompt": description_json.get("prompt", None),
    }
    batch_job_data = append_batch_job_history(user_id, job_data)

    for file_data in uploaded_files_list:
        file_id = file_data.get("file_id", None)
        job_data["file_status"] = file_data.get("status")
        job_data["batch_status"] = file_data.get("not_started")
        job_data["chunk_no"] = file_data.get("chunk_no")
        job_data["total_rows_processed"] = file_data.get("total_rows_processed")

        append_uploaded_file_history(
            user_id, batch_job_data["job_id"], file_id, job_data
        )

    output_json = convert_df_to_bytes(output_df)
    return output_json


def batch_processing_upload_file(user_id, filename, df, description_json):
    uploaded_files_list = steps.upload_file.start_process(
        df, filename, description_json
    )

    job_data = {
        "job_title": description_json.get("job_title", None),
        "file_name": filename,
        "job_type": "batch-job",
        "chunk_size": description_json.get("config", {}).get("chunkSize", 0),
        "chunks": len(uploaded_files_list),
        "total_rows_processed": len(df),
        "model": description_json.get("credentials", {}).get("deploymentName", "N/A"),
        "prompt": df["prompt"][0],
    }
    batch_job_data = append_batch_job_history(user_id, job_data)

    for file_data in uploaded_files_list:
        file_id = file_data.get("file_id", None)
        job_data["file_status"] = file_data.get("status")
        job_data["batch_status"] = file_data.get("not_started")
        job_data["chunk_no"] = file_data.get("chunk_no")
        job_data["total_rows_processed"] = file_data.get("total_rows_processed")

        append_uploaded_file_history(
            user_id, batch_job_data["job_id"], file_id, job_data
        )

    return {"message": "Hello", "file_ids": uploaded_files_list}


def start_batch_of_file_ids(user_id, job_id, list_of_file_ids):
    batch_files_list = steps.start_batch_job.start_process(
        user_id, job_id, list_of_file_ids
    )
    job_data = {"job_type": "batch-job"}
    for batch_data in batch_files_list:
        batch_id = batch_data.get("batch_id", None)
        file_id = batch_data.get("file_id", None)
        job_data["status"] = batch_data.get("status")
        job_data["chunk_no"] = batch_data.get("chunk_no")
        job_data["total_rows_processed"] = batch_data.get("total_rows_processed")
        job_data["output_file_id"] = batch_data.get("output_file_id")

        append_batch_file_history(user_id, job_id, file_id, batch_id, job_data)
    return {
        "batch_count": len(batch_files_list),
        "message": f"{len(batch_files_list)} has been started, check progress in batch status tab",
    }


def check_status_of_batch_ids_of_job(user_id, job_id, list_of_batch_ids):
    client = get_openai_client(user_id, job_id)
    if client:
        list_of_all_batch_status = []
        for batch_id in list_of_batch_ids:
            batch_status = get_batch_status_and_output_file_id(user_id, job_id, batch_id)
            if batch_status["status"] != "completed":
                current_batch_status = check_batch_progress(client, batch_id)
                batch_status["status"] = current_batch_status["status"]
                batch_status["output_file_id"] = current_batch_status["output_file_id"]
                update_batch_status_if_changed(
                    user_id,
                    job_id,
                    batch_id,
                    latest_status=current_batch_status["status"],
                    output_file_id=current_batch_status.get("output_file_id"),
                )
            list_of_all_batch_status.append(batch_status)
        return {
            "status_code": 200,
            "user_id": user_id,
            "job_id": job_id,
            "batch_status": list_of_all_batch_status,
        }
    else:
        return {
            "status_code": 200,
            "user_id": user_id,
            "job_id": job_id,
            "batch_status": [],
        }
