import pandas as pd
from datetime import datetime


import uuid
from .utils import read_jobs, write_jobs


def get_jobs_by_user_id(user_id: str):
    df = read_jobs()

    # Filter jobs for this user_id
    user_jobs = df[df["user_id"] == user_id]

    if user_jobs.empty:
        return {
            "status_code": 404,
            "message": f"No jobs found for user_id {user_id}"
        }

    # Convert each job row into dict
    jobs_list = user_jobs.to_dict(orient="records")

    return {
        "status_code": 200,
        "user_id": user_id,
        "jobs": jobs_list,
        "total_jobs": len(jobs_list),
        "message": "Jobs fetched successfully"
    }


def append_job_history(user_id: str, job_data: dict):
    df = read_jobs()

    # Create a new job entry
    new_job = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "job_title": job_data.get("job_title"),
        "file_name": job_data.get("file_name"),
        "job_type": job_data.get("job_type"),
        "status": job_data.get("status", "pending"),
        "total_rows_processed": job_data.get("total_rows_processed", 0),
        "model": job_data.get("model"),
        "avg_input_token": job_data.get("avg_input_token", 0),
        "avg_completion_token": job_data.get("avg_completion_token", 0),
        "avg_total_token": job_data.get("avg_total_token", 0),
        "avg_cost_per_row": job_data.get("avg_cost_per_row", 0.0),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "deleted_at": None,
    }

    # Append to DataFrame
    df = pd.concat([df, pd.DataFrame([new_job])], ignore_index=True)

    # Write back
    write_jobs(df)

    return {
        "status_code": 201,
        "message": "Job history appended successfully",
        "user_id": user_id,
        "job_id": new_job["id"],
    }
