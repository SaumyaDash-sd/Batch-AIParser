from fastapi import APIRouter, Response, HTTPException
from .main import validate_user, authenticate_user_token, get_user_by_id


login_router = APIRouter()


@login_router.get("/login/{email}/{password}")
def login(email: str, password: str, response: Response):
    result, _ = validate_user(email, password)
    response.status_code = result.get("status_code", 200)
    return result


@login_router.get("/validate-access-token/")
def validate_token(user_id: str, access_token: str, response: Response):
    if not authenticate_user_token(user_id, access_token):
        response.status_code = 401
        raise HTTPException(status_code=401, detail="invalid token")
    else:
        result = get_user_by_id(user_id)
        response.status_code = result.get("status_code", 200)
        return result
