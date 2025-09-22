from fastapi import APIRouter, Response, HTTPException


from .main import get_jobs_by_user_id, soft_delete_job
from login_setup.main import authenticate_user_token


job_history_router = APIRouter()


@job_history_router.get("/history/test-job/")
def get_test_jobs(user_id: str, access_token: str, response: Response):
    # Validate user_id and access_token  and status active
    if not authenticate_user_token(user_id, access_token):
        response.status_code = 401
        raise HTTPException(status_code=401, detail="Unauthorized User")
    else:
        result = get_jobs_by_user_id(user_id)
        response.status_code = result["status_code"]
        return result


@job_history_router.delete("/delete/test-job/")
def soft_delete_test_jobs(user_id: str, job_id: str, access_token: str, response: Response):
    # Validate user_id and access_token  and status active
    if not authenticate_user_token(user_id, access_token):
        response.status_code = 401
        raise HTTPException(status_code=401, detail="Unauthorized User")
    else:
        result = soft_delete_job(user_id, job_id)
        response.status_code = result["status_code"]
        return result
