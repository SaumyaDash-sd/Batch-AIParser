from fastapi import APIRouter, Response, HTTPException
from .main import get_jobs_by_user_id
from login_setup.main import authenticate_user_token


job_history_router = APIRouter()


@job_history_router.post("/history/test-job/")
def get_test_jobs(user_id: str, access_token: str, response: Response):
    # Validate user_id and access_token  and status active
    if not authenticate_user_token(user_id, access_token):
        response.status_code = 401
        raise HTTPException(status_code=401, detail="Unauthorized User")
    else:
        result = get_jobs_by_user_id(user_id)
        return result


