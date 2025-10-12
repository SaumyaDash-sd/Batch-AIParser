import pandas as pd
import io
import json


from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response
from pydantic import BaseModel


from .main import (
    batch_processing_create_and_upload_file,
    batch_processing_upload_file,
    start_batch_of_file_ids,
    start_batch_of_job_id,
    check_status_of_batch_ids_of_job,
    download_input_csv_file_of_file_ids,
    download_output_csv_file_of_batch_ids,
)
from login_setup import authenticate_user_token


batch_process_router = APIRouter()


@batch_process_router.post("/process/create-upload-file/")
async def create_and_upload_file(
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
        result = batch_processing_create_and_upload_file(
            user_id, file.filename, df, description_json
        )
        response.status_code = 200
        result["message"] = "Data pre-processing and upload done"
        return result


class StartBatchModel(BaseModel):
    file_ids: list


@batch_process_router.post("/process/create-start-batch/")
async def create_and_start_batch(
    user_id: str,
    access_token: str,
    job_id: str,
    response: Response,
    list_of_file_ids: StartBatchModel,  # Will contain JSON string
):
    # access_token = "e284aabe-2e54-4b11-b1f8-ff2b4c81d9d7"
    # Validate user_id and access_token  and status active
    if not authenticate_user_token(user_id, access_token):
        response.status_code = 401
        raise HTTPException(status_code=401, detail="Unauthorized User")
    else:  
        result = start_batch_of_file_ids(
            user_id, job_id, list_of_file_ids.file_ids
        )
        response.status_code = 200
        result["message"] = f"Batch started sucessfully of job_id: {job_id}"
        return result


@batch_process_router.post("/process/start-batch-of-job/")
async def start_all_batch_of_job_id(
    user_id: str,
    access_token: str,
    job_id: str,
    response: Response,
):
    # access_token = "e284aabe-2e54-4b11-b1f8-ff2b4c81d9d7"
    # Validate user_id and access_token  and status active
    if not authenticate_user_token(user_id, access_token):
        response.status_code = 401
        raise HTTPException(status_code=401, detail="Unauthorized User")
    else:  
        result = start_batch_of_job_id(
            user_id, job_id
        )
        response.status_code = 200
        result["message"] = f"Batch started sucessfully of job_id: {job_id}"
        return result


@batch_process_router.post("/process/upload-file/", deprecated=True)
async def upload_file_for_batch(
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
        result = batch_processing_upload_file(
            user_id, file.filename, df, description_json
        )
        response.status_code = 200
        return result


class CheckBatchStatusModel(BaseModel):
    batch_ids: list[str]


@batch_process_router.post("/process/check-batch-status/")
async def check_batch_status(
    user_id: str,
    access_token: str,
    job_id: str,
    response: Response,
    list_of_batch_ids: CheckBatchStatusModel,  # Will contain JSON string
):
    # access_token = "e284aabe-2e54-4b11-b1f8-ff2b4c81d9d7"
    # Validate user_id and access_token  and status active
    if not authenticate_user_token(user_id, access_token):
        response.status_code = 401
        raise HTTPException(status_code=401, detail="Unauthorized User")
    else:
        result = check_status_of_batch_ids_of_job(
            user_id, job_id, list_of_batch_ids.batch_ids
        )
        response.status_code = 200
        result["message"] = "Batch status fetched successfully"
        return result


class DownloadInputFileModel(BaseModel):
    file_ids: list[str]


@batch_process_router.post("/download/input-file/")
async def download_input_csv_file(
    user_id: str,
    access_token: str,
    job_id: str,
    response: Response,
    list_of_file_ids: DownloadInputFileModel,  # Will contain JSON string
):
    # access_token = "e284aabe-2e54-4b11-b1f8-ff2b4c81d9d7"
    # Validate user_id and access_token  and status active
    if not authenticate_user_token(user_id, access_token):
        response.status_code = 401
        raise HTTPException(status_code=401, detail="Unauthorized User")
    else:
        result = download_input_csv_file_of_file_ids(
            user_id, job_id, list_of_file_ids.file_ids
        )
        response.status_code = 200
        result["message"] = "Input file data fetched successfully"
        return result


class DownloadOutputFileModel(BaseModel):
    batch_ids: list[str]


@batch_process_router.post("/download/output-file/")
async def download_output_csv_file(
    user_id: str,
    access_token: str,
    job_id: str,
    response: Response,
    list_of_batch_ids: DownloadOutputFileModel,  # Will contain JSON string
):
    # access_token = "e284aabe-2e54-4b11-b1f8-ff2b4c81d9d7"
    # Validate user_id and access_token  and status active
    if not authenticate_user_token(user_id, access_token):
        response.status_code = 401
        raise HTTPException(status_code=401, detail="Unauthorized User")
    else:
        result = download_output_csv_file_of_batch_ids(
            user_id, job_id, list_of_batch_ids.batch_ids
        )
        response.status_code = 200
        result["message"] = "Output file data fetched successfully"
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
