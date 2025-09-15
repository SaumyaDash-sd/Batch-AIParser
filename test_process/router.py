from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response

from .main import test_prompt_process
from pydantic import BaseModel
from login_setup import authenticate_user_token
import pandas as pd
import io
import json


test_process_router = APIRouter()


# class TestProcessModel(BaseModel):
#     data: str  # bytes/object from frontend
#     unique_id_column: str
#     prompt: str
#     placeholder_field: dict
#     output_field: dict
#     config: dict
#     credentials: dict


@test_process_router.post("/process/test-prompt/")
async def test_prompt(
    user_id: str,
    access_token: str,
    response: Response,
    file: UploadFile = File(...),
    description: str = Form(...),  # Will contain JSON string
):
    # access_token = "e284aabe-2e54-4b11-b1f8-ff2b4c81d9d7"
    # Validate user_id and access_token  and status active
    if not authenticate_user_token(user_id, access_token):
        response.status_code = 401
        raise HTTPException(status_code=401, detail="Unauthorized User")
    else:
        # Parse JSON string into dict
        try:
            description_json = json.loads(description)
        except json.JSONDecodeError:
            response.status_code = 400
            raise HTTPException(status_code=400, detail="Invalid JSON in description")

        contents = await file.read()

        # Decide based on file extension
        if file.filename and file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename and (
            file.filename.endswith(".xlsx") or file.filename.endswith(".xls")
        ):
            df = pd.read_excel(io.BytesIO(contents), engine="openpyxl")
        else:
            response.status_code = 400
            raise HTTPException(status_code=400, detail="Unsupported file type")
        result = test_prompt_process(df, description_json)
        response.status_code = 200
        return result


"""
{
    "job_title": "Testing prompt for Keywords",
    "prompt": "You are an assistant that returns JSON only. Task: Suggest 5 keywords that a user would search for in the category: '{{category}}'. Output requirements: - Return ONLY valid JSON. - Do not add explanations, text, or extra keys. - The JSON must have exactly one key: suggested_five_keywords. - The value of suggested_five_keywords must be a list of exactly 5 keyword strings. Correct output format: { 'suggested_five_keywords': ['keyword1', 'keyword2', 'keyword3', 'keyword4', 'keyword5'] }",
    "placeholder_field": {"category": "category_name"},
    "unique_id_field": "national_catid",
    "output_field": {"suggested_five_keywords": "list of 5 keywords"},
    "config": {
      "chunkSize": 20
    },
    "credentials": { "apiKey": "49399de06f4c413db072e580c470b443", "endpoint": "https://gpt4omini-exp.openai.azure.com/",  "deploymentName": "gpt4omini-exp", "temperature": 0.7}
}
"""
