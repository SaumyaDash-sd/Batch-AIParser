import pandas as pd
import os
import math
import json
from database.mysql_connection import ConnectDB


# MySQL table names
UPLOADED_FILES_TABLE = "uploaded_files_AI_Portal"
BATCH_FILES_TABLE = "batch_files_AI_Portal"
BATCH_JOBS_TABLE = "batch_jobs_AI_Portal"
DB_NAME = os.getenv("DB_DATABASE")


def read_uploaded_files():
    """Read uploaded files from MySQL database and return as DataFrame"""
    try:
        db = ConnectDB()
        query = f"SELECT * FROM {DB_NAME}.{UPLOADED_FILES_TABLE}"
        result = db.fetch(query)
        db.close_connection()
        
        if result["status_code"] == 200 and result["data"]:
            return pd.DataFrame(result["data"])
        else:
            # Return empty DataFrame with expected columns if no data
            return pd.DataFrame(columns=[
                "file_id", "user_id", "job_id", "job_type", "file_status", "batch_status",
                "chunk_no", "total_rows_processed", "created_at", "updated_at", "deleted_at"
            ])
    except Exception as e:
        print(f"Error reading uploaded files from MySQL: {e}")
        return pd.DataFrame(columns=[
            "file_id", "user_id", "job_id", "job_type", "file_status", "batch_status",
            "chunk_no", "total_rows_processed", "created_at", "updated_at", "deleted_at"
        ])


def write_uploaded_files(df):
    """Write uploaded files DataFrame to MySQL database"""
    try:
        db = ConnectDB()
        
        # First, get all existing file_ids
        existing_query = f"SELECT file_id FROM {DB_NAME}.{UPLOADED_FILES_TABLE}"
        existing_result = db.fetch(existing_query)
        existing_ids = set()
        if existing_result["status_code"] == 200 and existing_result["data"]:
            existing_ids = {row["file_id"] for row in existing_result["data"]}
        
        # Prepare insert and update queries
        insert_queries = []
        update_queries = []
        
        for _, row in df.iterrows():
            file_id = row.get("file_id")
            # Replace NaN with None for MySQL
            row_dict = {k: (None if (isinstance(v, float) and math.isnan(v)) else v) for k, v in row.to_dict().items()}
            
            if file_id in existing_ids:
                # Update existing file
                update_query = {
                    "query": f"""UPDATE {DB_NAME}.{UPLOADED_FILES_TABLE} 
                                SET user_id = %s, job_id = %s, job_type = %s, file_status = %s, 
                                    batch_status = %s, chunk_no = %s, total_rows_processed = %s,
                                    created_at = %s, updated_at = %s, deleted_at = %s 
                                WHERE file_id = %s""",
                    "data": (
                        row_dict.get("user_id"), row_dict.get("job_id"), row_dict.get("job_type"),
                        row_dict.get("file_status"), row_dict.get("batch_status"), row_dict.get("chunk_no"),
                        row_dict.get("total_rows_processed"), row_dict.get("created_at"),
                        row_dict.get("updated_at"), row_dict.get("deleted_at"), file_id
                    )
                }
                update_queries.append(update_query)
            else:
                # Insert new file
                insert_query = {
                    "query": f"""INSERT INTO {DB_NAME}.{UPLOADED_FILES_TABLE} 
                                (file_id, user_id, job_id, job_type, file_status, batch_status, 
                                 chunk_no, total_rows_processed, created_at, updated_at, deleted_at) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    "data": (
                        row_dict.get("file_id"), row_dict.get("user_id"), row_dict.get("job_id"),
                        row_dict.get("job_type"), row_dict.get("file_status"), row_dict.get("batch_status"),
                        row_dict.get("chunk_no"), row_dict.get("total_rows_processed"),
                        row_dict.get("created_at"), row_dict.get("updated_at"), row_dict.get("deleted_at")
                    )
                }
                insert_queries.append(insert_query)
        
        # Execute updates
        if update_queries:
            db.update(update_queries)
        
        # Execute inserts
        if insert_queries:
            db.insert(insert_queries)
        
        db.close_connection()
    except Exception as e:
        print(f"Error writing uploaded files to MySQL: {e}")
        raise


def read_batch_files():
    """Read batch files from MySQL database and return as DataFrame"""
    try:
        db = ConnectDB()
        query = f"SELECT * FROM {DB_NAME}.{BATCH_FILES_TABLE}"
        result = db.fetch(query)
        db.close_connection()
        
        if result["status_code"] == 200 and result["data"]:
            return pd.DataFrame(result["data"])
        else:
            # Return empty DataFrame with expected columns if no data
            return pd.DataFrame(columns=[
                "batch_id", "user_id", "job_id", "file_id", "output_file_id", "job_type",
                "status", "chunk_no", "total_rows_processed", "created_at", "updated_at", "deleted_at"
            ])
    except Exception as e:
        print(f"Error reading batch files from MySQL: {e}")
        return pd.DataFrame(columns=[
            "batch_id", "user_id", "job_id", "file_id", "output_file_id", "job_type",
            "status", "chunk_no", "total_rows_processed", "created_at", "updated_at", "deleted_at"
        ])


def write_batch_files(df):
    """Write batch files DataFrame to MySQL database"""
    try:
        db = ConnectDB()
        
        # First, get all existing batch_ids
        existing_query = f"SELECT batch_id FROM {DB_NAME}.{BATCH_FILES_TABLE}"
        existing_result = db.fetch(existing_query)
        existing_ids = set()
        if existing_result["status_code"] == 200 and existing_result["data"]:
            existing_ids = {row["batch_id"] for row in existing_result["data"]}
        
        # Prepare insert and update queries
        insert_queries = []
        update_queries = []
        
        for _, row in df.iterrows():
            batch_id = row.get("batch_id")
            # Replace NaN with None for MySQL
            row_dict = {k: (None if (isinstance(v, float) and math.isnan(v)) else v) for k, v in row.to_dict().items()}
            
            if batch_id in existing_ids:
                # Update existing batch file
                update_query = {
                    "query": f"""UPDATE {DB_NAME}.{BATCH_FILES_TABLE} 
                                SET user_id = %s, job_id = %s, file_id = %s, output_file_id = %s, 
                                    job_type = %s, status = %s, chunk_no = %s, total_rows_processed = %s,
                                    created_at = %s, updated_at = %s, deleted_at = %s 
                                WHERE batch_id = %s""",
                    "data": (
                        row_dict.get("user_id"), row_dict.get("job_id"), row_dict.get("file_id"),
                        row_dict.get("output_file_id"), row_dict.get("job_type"), row_dict.get("status"),
                        row_dict.get("chunk_no"), row_dict.get("total_rows_processed"),
                        row_dict.get("created_at"), row_dict.get("updated_at"), row_dict.get("deleted_at"), batch_id
                    )
                }
                update_queries.append(update_query)
            else:
                # Insert new batch file
                insert_query = {
                    "query": f"""INSERT INTO {DB_NAME}.{BATCH_FILES_TABLE} 
                                (batch_id, user_id, job_id, file_id, output_file_id, job_type, 
                                 status, chunk_no, total_rows_processed, created_at, updated_at, deleted_at) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    "data": (
                        row_dict.get("batch_id"), row_dict.get("user_id"), row_dict.get("job_id"),
                        row_dict.get("file_id"), row_dict.get("output_file_id"), row_dict.get("job_type"),
                        row_dict.get("status"), row_dict.get("chunk_no"), row_dict.get("total_rows_processed"),
                        row_dict.get("created_at"), row_dict.get("updated_at"), row_dict.get("deleted_at")
                    )
                }
                insert_queries.append(insert_query)
        
        # Execute updates
        if update_queries:
            db.update(update_queries)
        
        # Execute inserts
        if insert_queries:
            db.insert(insert_queries)
        
        db.close_connection()
    except Exception as e:
        print(f"Error writing batch files to MySQL: {e}")
        raise


def read_batch_jobs():
    """Read batch jobs from MySQL database and return as DataFrame"""
    try:
        db = ConnectDB()
        query = f"SELECT * FROM {DB_NAME}.{BATCH_JOBS_TABLE}"
        result = db.fetch(query)
        db.close_connection()
        
        if result["status_code"] == 200 and result["data"]:
            df = pd.DataFrame(result["data"])
            # Handle prompt field - convert JSON string to list if needed
            if "prompt" in df.columns:
                def parse_prompt(x):
                    if x is None:
                        return x
                    if isinstance(x, str):
                        try:
                            return json.loads(x)
                        except (json.JSONDecodeError, ValueError):
                            return x
                    return x
                df["prompt"] = df["prompt"].apply(parse_prompt)
            return df
        else:
            # Return empty DataFrame with expected columns if no data
            return pd.DataFrame(columns=[
                "id", "user_id", "job_title", "file_name", "job_type", "chunks", "chunk_size",
                "total_rows_processed", "model", "endpoint", "api_key", "prompt",
                "created_at", "updated_at", "deleted_at"
            ])
    except Exception as e:
        print(f"Error reading batch jobs from MySQL: {e}")
        return pd.DataFrame(columns=[
            "id", "user_id", "job_title", "file_name", "job_type", "chunks", "chunk_size",
            "total_rows_processed", "model", "endpoint", "api_key", "prompt",
            "created_at", "updated_at", "deleted_at"
        ])


def write_batch_jobs(df):
    """Write batch jobs DataFrame to MySQL database"""
    try:
        db = ConnectDB()
        
        # First, get all existing job IDs
        existing_query = f"SELECT id FROM {DB_NAME}.{BATCH_JOBS_TABLE}"
        existing_result = db.fetch(existing_query)
        existing_ids = set()
        if existing_result["status_code"] == 200 and existing_result["data"]:
            existing_ids = {row["id"] for row in existing_result["data"]}
        
        # Prepare insert and update queries
        insert_queries = []
        update_queries = []
        
        for _, row in df.iterrows():
            job_id = row.get("id")
            # Replace NaN with None for MySQL
            row_dict = {k: (None if (isinstance(v, float) and math.isnan(v)) else v) for k, v in row.to_dict().items()}
            
            # Handle prompt field - serialize list/dict to JSON string
            prompt_value = row_dict.get("prompt")
            if prompt_value is not None and not isinstance(prompt_value, str):
                prompt_value = json.dumps(prompt_value)
            row_dict["prompt"] = prompt_value
            
            if job_id in existing_ids:
                # Update existing batch job
                update_query = {
                    "query": f"""UPDATE {DB_NAME}.{BATCH_JOBS_TABLE} 
                                SET user_id = %s, job_title = %s, file_name = %s, job_type = %s, 
                                    chunks = %s, chunk_size = %s, total_rows_processed = %s,
                                    model = %s, endpoint = %s, api_key = %s, prompt = %s,
                                    created_at = %s, updated_at = %s, deleted_at = %s 
                                WHERE id = %s""",
                    "data": (
                        row_dict.get("user_id"), row_dict.get("job_title"), row_dict.get("file_name"),
                        row_dict.get("job_type"), row_dict.get("chunks"), row_dict.get("chunk_size"),
                        row_dict.get("total_rows_processed"), row_dict.get("model"),
                        row_dict.get("endpoint"), row_dict.get("api_key"), row_dict.get("prompt"),
                        row_dict.get("created_at"), row_dict.get("updated_at"), row_dict.get("deleted_at"), job_id
                    )
                }
                update_queries.append(update_query)
            else:
                # Insert new batch job
                insert_query = {
                    "query": f"""INSERT INTO {DB_NAME}.{BATCH_JOBS_TABLE} 
                                (id, user_id, job_title, file_name, job_type, chunks, chunk_size,
                                 total_rows_processed, model, endpoint, api_key, prompt,
                                 created_at, updated_at, deleted_at) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    "data": (
                        row_dict.get("id"), row_dict.get("user_id"), row_dict.get("job_title"),
                        row_dict.get("file_name"), row_dict.get("job_type"), row_dict.get("chunks"),
                        row_dict.get("chunk_size"), row_dict.get("total_rows_processed"),
                        row_dict.get("model"), row_dict.get("endpoint"), row_dict.get("api_key"),
                        row_dict.get("prompt"), row_dict.get("created_at"),
                        row_dict.get("updated_at"), row_dict.get("deleted_at")
                    )
                }
                insert_queries.append(insert_query)
        
        # Execute updates
        if update_queries:
            db.update(update_queries)
        
        # Execute inserts
        if insert_queries:
            db.insert(insert_queries)
        
        db.close_connection()
    except Exception as e:
        print(f"Error writing batch jobs to MySQL: {e}")
        raise

def clean_nans(obj):
    if isinstance(obj, float) and math.isnan(obj):
        return None
    if isinstance(obj, dict):
        return {k: clean_nans(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_nans(i) for i in obj]
    return obj
