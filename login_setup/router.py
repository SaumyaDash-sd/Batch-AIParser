from fastapi import APIRouter
from .main import validate_user


login_router = APIRouter()


@login_router.get("/login/{email}/{password}")
def login(email: str, password: str):
    result, _ = validate_user(email, password)
    return result
