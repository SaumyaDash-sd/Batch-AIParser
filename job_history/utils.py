import pandas as pd
import os
import math
import json
from database.mysql_connection import ConnectDB


# MySQL table name
JOBS_TABLE = "job_history_AI_Portal"
DB_NAME = "team_keywords"


def read_jobs():
    """Read jobs from MySQL database and return as DataFrame"""
    try:
        db = ConnectDB()
        query = f"SELECT * FROM {DB_NAME}.{JOBS_TABLE}"
        result = db.fetch(query)
        db.close_connection()
        
        if result["status_code"] == 200 and result["data"]:
            df = pd.DataFrame(result["data"])
            # Handle prompt field - convert JSON string to list/dict if needed
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
                "id", "user_id", "job_title", "file_name", "job_type", "status",
                "total_rows_processed", "model", "avg_input_token", "avg_completion_token",
                "avg_total_token", "avg_cost_per_row", "prompt", "created_at", "updated_at", "deleted_at"
            ])
    except Exception as e:
        print(f"Error reading jobs from MySQL: {e}")
        return pd.DataFrame(columns=[
            "id", "user_id", "job_title", "file_name", "job_type", "status",
            "total_rows_processed", "model", "avg_input_token", "avg_completion_token",
            "avg_total_token", "avg_cost_per_row", "prompt", "created_at", "updated_at", "deleted_at"
        ])


def write_jobs(df):
    """Write jobs DataFrame to MySQL database"""
    try:
        db = ConnectDB()
        
        # First, get all existing job IDs
        existing_query = f"SELECT id FROM {DB_NAME}.{JOBS_TABLE}"
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
                # Update existing job
                update_query = {
                    "query": f"""UPDATE {DB_NAME}.{JOBS_TABLE} 
                                SET user_id = %s, job_title = %s, file_name = %s, job_type = %s, 
                                    status = %s, total_rows_processed = %s, model = %s, 
                                    avg_input_token = %s, avg_completion_token = %s, avg_total_token = %s,
                                    avg_cost_per_row = %s, prompt = %s, created_at = %s, 
                                    updated_at = %s, deleted_at = %s 
                                WHERE id = %s""",
                    "data": (
                        row_dict.get("user_id"), row_dict.get("job_title"), row_dict.get("file_name"),
                        row_dict.get("job_type"), row_dict.get("status"), row_dict.get("total_rows_processed"),
                        row_dict.get("model"), row_dict.get("avg_input_token"), row_dict.get("avg_completion_token"),
                        row_dict.get("avg_total_token"), row_dict.get("avg_cost_per_row"), row_dict.get("prompt"),
                        row_dict.get("created_at"), row_dict.get("updated_at"), row_dict.get("deleted_at"), job_id
                    )
                }
                update_queries.append(update_query)
            else:
                # Insert new job
                insert_query = {
                    "query": f"""INSERT INTO {DB_NAME}.{JOBS_TABLE} 
                                (id, user_id, job_title, file_name, job_type, status, total_rows_processed, 
                                 model, avg_input_token, avg_completion_token, avg_total_token, avg_cost_per_row, 
                                 prompt, created_at, updated_at, deleted_at) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    "data": (
                        row_dict.get("id"), row_dict.get("user_id"), row_dict.get("job_title"),
                        row_dict.get("file_name"), row_dict.get("job_type"), row_dict.get("status"),
                        row_dict.get("total_rows_processed"), row_dict.get("model"),
                        row_dict.get("avg_input_token"), row_dict.get("avg_completion_token"),
                        row_dict.get("avg_total_token"), row_dict.get("avg_cost_per_row"),
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
        print(f"Error writing jobs to MySQL: {e}")
        raise


def clean_nans(obj):
    if isinstance(obj, float) and math.isnan(obj):
        return None
    if isinstance(obj, dict):
        return {k: clean_nans(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_nans(i) for i in obj]
    return obj
