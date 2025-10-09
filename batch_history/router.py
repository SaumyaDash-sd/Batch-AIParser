from fastapi import APIRouter, Response, HTTPException


from .main import (
    append_batch_job_history,
    append_uploaded_file_history,
    append_batch_file_history,
    get_batch_jobs_by_user_id,
    get_uploaded_files_by_job_id,
    get_batch_files_by_job_id,
    soft_delete_batch_job,
    soft_delete_uploaded_file,
    soft_delete_batch_file,
)
from login_setup.main import authenticate_user_token


batch_job_history_router = APIRouter()


@batch_job_history_router.get("/history/batch-job/")
def get_batch_jobs(user_id: str, access_token: str, response: Response):
    # Validate user_id and access_token  and status active
    if not authenticate_user_token(user_id, access_token):
        response.status_code = 401
        raise HTTPException(status_code=401, detail="Unauthorized User")
    else:
        result = get_batch_jobs_by_user_id(user_id)
        response.status_code = result["status_code"]
        return result


@batch_job_history_router.get("/history/uploaded-file/")
def get_uploaded_files(user_id: str, access_token: str, job_id: str, response: Response):
    # Validate user_id and access_token  and status active
    if not authenticate_user_token(user_id, access_token):
        response.status_code = 401
        raise HTTPException(status_code=401, detail="Unauthorized User")
    else:
        result = get_uploaded_files_by_job_id(user_id, job_id)
        response.status_code = result["status_code"]
        return result


@batch_job_history_router.get("/history/batch-file/")
def get_created_batch(user_id: str, access_token: str, job_id: str, response: Response):
    # Validate user_id and access_token  and status active
    if not authenticate_user_token(user_id, access_token):
        response.status_code = 401
        raise HTTPException(status_code=401, detail="Unauthorized User")
    else:
        result = get_batch_files_by_job_id(user_id, job_id)
        response.status_code = result["status_code"]
        return result


@batch_job_history_router.delete("/delete/batch-job/")
def soft_delete_batch_jobs_by_job_id(user_id: str, job_id: str, access_token: str, response: Response):
    # Validate user_id and access_token  and status active
    if not authenticate_user_token(user_id, access_token):
        response.status_code = 401
        raise HTTPException(status_code=401, detail="Unauthorized User")
    else:
        result = soft_delete_batch_job(user_id, job_id)
        response.status_code = result["status_code"]
        return result


@batch_job_history_router.delete("/delete/uploaded-file/")
def soft_delete_uploaded_files_by_file_id(user_id: str, file_id: str, access_token: str, response: Response):
    # Validate user_id and access_token  and status active
    if not authenticate_user_token(user_id, access_token):
        response.status_code = 401
        raise HTTPException(status_code=401, detail="Unauthorized User")
    else:
        result = soft_delete_uploaded_file(user_id, file_id)
        response.status_code = result["status_code"]
        return result


@batch_job_history_router.delete("/delete/batch-file/")
def soft_delete_batch_file_by_job_id(user_id: str, batch_id: str, access_token: str, response: Response):
    # Validate user_id and access_token  and status active
    if not authenticate_user_token(user_id, access_token):
        response.status_code = 401
        raise HTTPException(status_code=401, detail="Unauthorized User")
    else:
        result = soft_delete_batch_file(user_id, batch_id)
        response.status_code = result["status_code"]
        return result


# @batch_job_history_router.get("/history/download/uploaded-file/")
# def download_uploaded_files(user_id: str, access_token: str, response: Response):
#     # Validate user_id and access_token  and status active
#     if not authenticate_user_token(user_id, access_token):
#         response.status_code = 401
#         raise HTTPException(status_code=401, detail="Unauthorized User")
#     else:
#         result = get_jobs_by_user_id(user_id)
#         response.status_code = result["status_code"]
#         return result


# @batch_job_history_router.get("/history/download/batch-input-file/")
# def download_batch_input_file(user_id: str, access_token: str, response: Response):
#     # Validate user_id and access_token  and status active
#     if not authenticate_user_token(user_id, access_token):
#         response.status_code = 401
#         raise HTTPException(status_code=401, detail="Unauthorized User")
#     else:
#         result = get_jobs_by_user_id(user_id)
#         response.status_code = result["status_code"]
#         return result


# @batch_job_history_router.get("/history/download/batch-output-file/")
# def download_batch_output_file(user_id: str, access_token: str, response: Response):
#     # Validate user_id and access_token  and status active
#     if not authenticate_user_token(user_id, access_token):
#         response.status_code = 401
#         raise HTTPException(status_code=401, detail="Unauthorized User")
#     else:
#         result = get_jobs_by_user_id(user_id)
#         response.status_code = result["status_code"]
#         return result
