import uuid
import pandas as pd


from datetime import datetime


from .utils import read_jobs, write_jobs, clean_nans


def get_jobs_by_user_id(user_id: str):
    df = read_jobs()

    # Filter jobs for this user_id and where deleted_at is NaN/null
    user_jobs = df[(df["user_id"] == user_id) & (df["deleted_at"].isna())]

    if user_jobs.empty:
        return {"status_code": 404, "message": f"No jobs found for user_id {user_id}"}

    # Convert each job row into dict
    jobs_list = clean_nans(user_jobs.to_dict(orient="records"))

    return {
        "status_code": 200,
        "user_id": user_id,
        "jobs": jobs_list,
        "total_jobs": len(jobs_list) if isinstance(jobs_list, list) else 0,
        "message": "Jobs fetched successfully",
    }


def append_job_history(user_id: str, job_data: dict):
    df = read_jobs()

    # Create a new job entry
    new_job = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "job_title": job_data.get("job_title", None),
        "file_name": job_data.get("file_name", None),
        "job_type": job_data.get("job_type", None),
        "status": job_data.get("status", "pending"),
        "total_rows_processed": job_data.get("total_rows_processed", 0),
        "model": job_data.get("model", None),
        "avg_input_token": job_data.get("avg_input_token", 0),
        "avg_completion_token": job_data.get("avg_completion_token", 0),
        "avg_total_token": job_data.get("avg_total_token", 0),
        "avg_cost_per_row": job_data.get("avg_cost_per_row", 0.0),
        "prompt": job_data.get("prompt", None),
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


def soft_delete_job(user_id: str, job_id: str):
    df = read_jobs()

    # Find the job
    mask = (df["user_id"] == user_id) & (df["id"] == job_id)

    if df[mask].empty:
        return {"status_code": 404, "message": f"No job found for user_id {user_id} with job_id {job_id}"}

    # If already deleted
    if not df.loc[mask, "deleted_at"].isna().all():
        return {"status_code": 400, "message": f"Job {job_id} is already deleted"}

    # Update deleted_at with current timestamp
    df.loc[mask, "deleted_at"] = datetime.now().isoformat()

    # Persist changes
    write_jobs(df)

    return {
        "status_code": 200,
        "message": f"Job {job_id} deleted successfully",
        "user_id": user_id,
        "job_id": job_id,
    }
