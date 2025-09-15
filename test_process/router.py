from fastapi import APIRouter, UploadFile, File, Form, HTTPException

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
    file: UploadFile = File(...),
    description: str = Form(...),  # Will contain JSON string
):
    # Validate user_id and access_token  and status active
    if not authenticate_user_token(user_id, access_token):
        return {"error": "Unauthorized User", "status_code": 401}
    else:
        # Parse JSON string into dict
        try:
            description_json = json.loads(description)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in description")

        contents = await file.read()

        # Decide based on file extension
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(".xlsx") or file.filename.endswith(".xls"):
            df = pd.read_excel(io.BytesIO(contents), engine="openpyxl")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        ####################
        """
        Call you function here and pass df and description_json and store the result and return"""
        
        result = test_prompt_process(df, description_json)
        return result
        
        ####################
        
        #delete below code when above code is setup

        print(
            {
                "user_id": user_id,
                "access_token": access_token,
                "filename": file.filename,
                "columns": df.columns.tolist(),
                "rows": len(df),
                "description": description_json,
            }
        )
        
        return {
                "user_id": user_id,
                "access_token": access_token,
                "filename": file.filename,
                "columns": df.columns.tolist(),
                "rows": len(df),
                "description": description_json,
            }


# @test_process_router.post("/process")
# def test_process(user_id: str, access_token: str, payload: TestProcessModel):
#     # Validate user_id and access_token  and status active
#     if not authenticate_user_token(user_id, access_token):
#         return {"error": "Unauthorized User", "status_code": 401}
#     else:
#         result = test_prompt_process(
#             data=payload.data,
#             unique_id_column=payload.unique_id_column,
#             prompt=payload.prompt,
#             placeholder_field=payload.placeholder_field,
#             output_field=payload.output_field,
#             config=payload.config,
#             credentials=payload.credentials,
#         )
#         return result


{
    "job_title": "Testing prompt for Keywords",
    "prompt": "Hey GPT, can you check the Department name: {{department_name}} and suggest me whether it is meaningful or not in True or False.\nIf it is not meanignful then suggest a department name related to it.\nAnd can you check the user name: {{users_name}} is it a real name of user or not in True or False, if not real then suggest name also.\nYou have to return your output in below JSON format only, not in any other format:\n{\n\"department_name\": \"Original name of the department\",\n\"meaningful_department_name\": True or False,\n\"suggested_department_name\": \"Suggest related department name\",\n\"original_name\": \"Original name of the user\",\n\"meaningful_user_name\": True or False,\n\"suggested_user_name\": \"Suggest related user name\"\n}\n",
    "placeholder_field": {
      "department_name": "department",
      "users_name": "name"
    },
    "unique_id_field": null,
    "output_field": {
      "department_name": "Original name of the department",
      "meaningful_department_name": "True or False",
      "suggested_department_name": "Suggest related department name",
      "original_name": "Original name of the user",
      "meaningful_user_name": "True or False",
      "suggested_user_name": "Suggest related user name"
    },
    "config": {
      "chunkSize": 20
    },
    "credentials": {
      "endpoint": "https://hari-pulse-abg.openai.azure.com/",
      "apiKey": "openai_api_key_askdsdnsdkadnkas",
      "deploymentName": "gpt-4o-mini",
      "temperature": 0.7
    }
  }