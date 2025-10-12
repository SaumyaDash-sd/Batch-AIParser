import uuid
import pandas as pd


from datetime import datetime
from openai import AzureOpenAI


from .utils import (
    clean_nans,
    read_uploaded_files,
    write_uploaded_files,
    read_batch_files,
    write_batch_files,
    read_batch_jobs,
    write_batch_jobs,
)


def append_batch_job_history(user_id: str, job_data: dict):
    df = read_batch_jobs()

    # Create a new job entry
    new_job = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "job_title": job_data.get("job_title", None),
        "file_name": job_data.get("file_name", None),
        "job_type": job_data.get("job_type", None),
        "chunks": job_data.get("chunks", 0),
        "total_rows_processed": job_data.get("total_rows_processed", 0),
        "model": job_data.get("model", None),
        "prompt": [job_data.get("prompt", None)],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "deleted_at": None,
    }

    # Append to DataFrame
    df = pd.concat([df, pd.DataFrame([new_job])], ignore_index=True)

    # Write back
    write_batch_jobs(df)

    return {
        "status_code": 201,
        "message": "Batch job history appended successfully",
        "user_id": user_id,
        "job_id": new_job["id"],
    }


def append_uploaded_file_history(
    user_id: str, job_id: str, file_id: str, job_data: dict
):
    df = read_uploaded_files()

    # Create a new job entry
    new_job = {
        "file_id": file_id,
        "user_id": user_id,
        "job_id": job_id,
        "job_type": job_data.get("job_type", None),
        "file_status": job_data.get("file_status", "failed"),
        "batch_status": job_data.get("batch_status", "not_started"),
        "chunk_no": job_data.get("chunk_no", "chunk_1"),
        "total_rows_processed": job_data.get("total_rows_processed", 0),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "deleted_at": None,
    }

    # Append to DataFrame
    df = pd.concat([df, pd.DataFrame([new_job])], ignore_index=True)

    # Write back
    write_uploaded_files(df)

    return {
        "status_code": 201,
        "message": "Upload file history appended successfully",
        "user_id": user_id,
        "job_id": job_id,
        "file_id": new_job["id"],
    }


def append_batch_file_history(
    user_id: str, job_id: str, file_id: str, batch_id: str, job_data: dict
):
    df = read_batch_files()

    # Create a new job entry
    new_job = {
        "batch_id": batch_id,
        "user_id": user_id,
        "job_id": job_id,
        "file_id": file_id,
        "output_file_id": job_data.get("output_file_id", None),
        "job_type": job_data.get("job_type", None),
        "status": job_data.get("batch_status", "not_started"),
        "chunk_no": job_data.get("chunk_no", "chunk_1"),
        "total_rows_processed": job_data.get("total_rows_processed", 0),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "deleted_at": None,
    }

    # Append to DataFrame
    df = pd.concat([df, pd.DataFrame([new_job])], ignore_index=True)

    # Write back
    write_batch_files(df)

    return {
        "status_code": 201,
        "message": "Batch file history appended successfully",
        "user_id": user_id,
        "job_id": job_id,
        "file_id": file_id,
        "batch_id": new_job["id"],
    }


def get_batch_jobs_by_user_id(user_id: str):
    df = read_batch_jobs()

    # Filter jobs for this user_id and where deleted_at is NaN/null
    user_jobs = df[(df["user_id"] == user_id) & (df["deleted_at"].isna())]

    if user_jobs.empty:
        return {
            "status_code": 404,
            "message": f"No batch jobs found for user_id {user_id}",
        }

    # Convert each job row into dict
    jobs_list = clean_nans(user_jobs.to_dict(orient="records"))

    return {
        "status_code": 200,
        "user_id": user_id,
        "jobs": jobs_list,
        "total_jobs": len(jobs_list) if isinstance(jobs_list, list) else 0,
        "message": "Batch jobs fetched successfully",
    }


def get_uploaded_files_by_job_id(user_id: str, job_id: str):
    df = read_uploaded_files()

    # Filter jobs for this user_id and where deleted_at is NaN/null
    user_jobs = df[
        (df["user_id"] == user_id)
        & (df["job_id"] == job_id)
        & (df["deleted_at"].isna())
    ]

    if user_jobs.empty:
        return {
            "status_code": 404,
            "message": f"No uploaded files found for job_id {job_id}",
        }

    # Convert each job row into dict
    jobs_list = clean_nans(user_jobs.to_dict(orient="records"))

    return {
        "status_code": 200,
        "user_id": user_id,
        "job_id": job_id,
        "jobs": jobs_list,
        "total_jobs": len(jobs_list) if isinstance(jobs_list, list) else 0,
        "message": "Uploaded files fetched successfully",
    }


def get_batch_files_by_job_id(user_id: str, job_id: str):
    df = read_batch_files()

    # Filter jobs for this user_id and where deleted_at is NaN/null
    user_jobs = df[
        (df["user_id"] == user_id)
        & (df["job_id"] == job_id)
        & (df["deleted_at"].isna())
    ]

    if user_jobs.empty:
        return {
            "status_code": 404,
            "message": f"No batch files found for job_id {job_id}",
        }

    # Convert each job row into dict
    jobs_list = clean_nans(user_jobs.to_dict(orient="records"))

    return {
        "status_code": 200,
        "user_id": user_id,
        "job_id": job_id,
        "jobs": jobs_list,
        "total_jobs": len(jobs_list) if isinstance(jobs_list, list) else 0,
        "message": "Batch files fetched successfully",
    }


def soft_delete_batch_job(user_id: str, job_id: str):
    df = read_batch_jobs()

    # Find the job
    mask = (df["user_id"] == user_id) & (df["id"] == job_id)

    if df[mask].empty:
        return {
            "status_code": 404,
            "message": f"No batch job found for user_id {user_id} with file_id {job_id}",
        }

    # If already deleted
    if not df.loc[mask, "deleted_at"].isna().all():
        return {"status_code": 400, "message": f"Batch job {job_id} is already deleted"}

    # Update deleted_at with current timestamp
    df.loc[mask, "deleted_at"] = datetime.now().isoformat()

    # Persist changes
    write_batch_jobs(df)

    return {
        "status_code": 200,
        "message": f"Batch job {job_id} deleted successfully",
        "user_id": user_id,
        "job_id": job_id,
    }


def soft_delete_uploaded_file(user_id: str, file_id: str):
    df = read_uploaded_files()

    # Find the job
    mask = (df["user_id"] == user_id) & (df["file_id"] == file_id)

    if df[mask].empty:
        return {
            "status_code": 404,
            "message": f"No file found for user_id {user_id} with file_id {file_id}",
        }

    # If already deleted
    if not df.loc[mask, "deleted_at"].isna().all():
        return {"status_code": 400, "message": f"File {file_id} is already deleted"}

    # Update deleted_at with current timestamp
    df.loc[mask, "deleted_at"] = datetime.now().isoformat()

    # Persist changes
    write_uploaded_files(df)

    return {
        "status_code": 200,
        "message": f"File {file_id} deleted successfully",
        "user_id": user_id,
        "file_id": file_id,
    }


def soft_delete_batch_file(user_id: str, batch_id: str):
    df = read_batch_files()

    # Find the job
    mask = (df["user_id"] == user_id) & (df["batch_id"] == batch_id)

    if df[mask].empty:
        return {
            "status_code": 404,
            "message": f"No batch file found for user_id {user_id} with batch_id {batch_id}",
        }

    # If already deleted
    if not df.loc[mask, "deleted_at"].isna().all():
        return {
            "status_code": 400,
            "message": f"Batch file {batch_id} is already deleted",
        }

    # Update deleted_at with current timestamp
    df.loc[mask, "deleted_at"] = datetime.now().isoformat()

    # Persist changes
    write_batch_files(df)

    return {
        "status_code": 200,
        "message": f"Batch file {batch_id} deleted successfully",
        "user_id": user_id,
        "batch_id": batch_id,
    }


def get_openai_client(user_id, job_id):
    df = read_batch_jobs()

    # Filter the DataFrame based on user_id and job_id
    filtered = df[
        (df["user_id"] == user_id) & (df["id"] == job_id) & (df["deleted_at"].isna())
    ]

    # Check if any row matches
    if not filtered.empty:
        first_row = filtered.iloc[0]
        return AzureOpenAI(
            api_key=first_row["api_key"],
            azure_endpoint=first_row["endpoint"],
            api_version="2025-01-01-preview",
        )
    else:
        return None


def get_chunk_no_and_row_count(user_id, job_id, file_id):
    # Step 1: Read the DataFrame
    df = read_uploaded_files()

    # Step 2: Create a boolean mask for matching rows
    mask = (
        (df["user_id"] == user_id)
        & (df["job_id"] == job_id)
        & (df["file_id"] == file_id)
        & (df["deleted_at"].isna())
    )

    # Step 3: Filter matching rows
    filtered = df[mask]

    # Step 4: If any match found, update and return details
    if not filtered.empty:
        # Update batch_status to 'started'
        df.loc[mask, "batch_status"] = "started"

        # Write updated DataFrame back
        write_uploaded_files(df)

        # Get first matching row
        first_row = filtered.iloc[0]
        return first_row["chunk_no"], first_row["total_rows_processed"]
    else:
        return None, None


def get_batch_status_and_output_file_id(user_id, job_id, batch_id):
    # Step 1: Read the DataFrame
    df = read_batch_files()

    # Step 2: Filter for the matching row
    filtered = df[
        (df["user_id"] == user_id) &
        (df["job_id"] == job_id) &
        (df["batch_id"] == batch_id) &
        (df["deleted_at"].isna())
    ]

    # Step 3: Check if any row matches
    if not filtered.empty:
        first_row = filtered.iloc[0]
        result = {
            "status": first_row["status"],
            "batch_id": batch_id,
            "output_file_id": first_row["output_file_id"]
        }
    else:
        # If no match found, return None or some default value
        result = {
            "status": None,
            "batch_id": batch_id,
            "output_file_id": None
        }

    # Step 4: Convert to JSON and return
    return result


def update_batch_status_if_changed(user_id, job_id, batch_id, latest_status, output_file_id=None):
    """
    Update the batch status and output_file_id in the CSV if the latest_status
    is different from the current status.
    
    Parameters:
        user_id (int/str)
        job_id (int/str)
        batch_id (int/str)
        latest_status (str)
        output_file_id (optional, int/str): only updated if status is 'completed'
    """
    # Step 1: Read the CSV
    df = read_batch_files()
    
    # Step 2: Create mask for the specific row
    mask = (
        (df["user_id"] == user_id) &
        (df["job_id"] == job_id) &
        (df["batch_id"] == batch_id) &
        (df["deleted_at"].isna())
    )
    
    # Step 3: Check if row exists
    if not df[mask].empty:
        current_status = df.loc[mask, "status"].iloc[0]
        
        # Step 4: Update only if status is different
        if current_status != latest_status:
            df.loc[mask, "status"] = latest_status
            
            # Update output_file_id if the status is completed and value is provided
            if latest_status == "completed" and output_file_id is not None:
                df.loc[mask, "output_file_id"] = output_file_id
            
            # Step 5: Write back to CSV
            write_batch_files(df)
