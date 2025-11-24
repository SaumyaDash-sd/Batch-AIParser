import pandas as pd
import os
import math
from database.mysql_connection import ConnectDB


# MySQL table name
USERS_TABLE = "users_AI_Portal"
DB_NAME = "GOJD"


def read_users():
    """Read users from MySQL database and return as DataFrame"""
    try:
        db = ConnectDB()
        query = f"SELECT * FROM {DB_NAME}.{USERS_TABLE}"
        result = db.fetch(query)
        db.close_connection()
        
        if result["status_code"] == 200 and result["data"]:
            return pd.DataFrame(result["data"])
        else:
            # Return empty DataFrame with expected columns if no data
            return pd.DataFrame(columns=[
                "id", "first_name", "last_name", "email", "password", 
                "role", "status", "access_token", "created_at", "updated_at", "deleted_at"
            ])
    except Exception as e:
        print(f"Error reading users from MySQL: {e}")
        return pd.DataFrame(columns=[
            "id", "first_name", "last_name", "email", "password", 
            "role", "status", "access_token", "created_at", "updated_at", "deleted_at"
        ])


def write_users(df):
    """Write users DataFrame to MySQL database"""
    try:
        db = ConnectDB()
        
        # First, get all existing user IDs
        existing_query = f"SELECT id FROM {DB_NAME}.{USERS_TABLE}"
        existing_result = db.fetch(existing_query)
        existing_ids = set()
        if existing_result["status_code"] == 200 and existing_result["data"]:
            existing_ids = {row["id"] for row in existing_result["data"]}
        
        # Prepare insert and update queries
        insert_queries = []
        update_queries = []
        
        for _, row in df.iterrows():
            user_id = row.get("id")
            # Replace NaN with None for MySQL
            row_dict = {k: (None if (isinstance(v, float) and math.isnan(v)) else v) for k, v in row.to_dict().items()}
            
            if user_id in existing_ids:
                # Update existing user
                update_query = {
                    "query": f"""UPDATE {DB_NAME}.{USERS_TABLE} 
                                SET first_name = %s, last_name = %s, email = %s, password = %s, 
                                    role = %s, status = %s, access_token = %s, 
                                    created_at = %s, updated_at = %s, deleted_at = %s 
                                WHERE id = %s""",
                    "data": (
                        row_dict.get("first_name"), row_dict.get("last_name"), row_dict.get("email"),
                        row_dict.get("password"), row_dict.get("role"), row_dict.get("status"),
                        row_dict.get("access_token"), row_dict.get("created_at"),
                        row_dict.get("updated_at"), row_dict.get("deleted_at"), user_id
                    )
                }
                update_queries.append(update_query)
            else:
                # Insert new user
                insert_query = {
                    "query": f"""INSERT INTO {DB_NAME}.{USERS_TABLE} 
                                (id, first_name, last_name, email, password, role, status, access_token, created_at, updated_at, deleted_at) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    "data": (
                        row_dict.get("id"), row_dict.get("first_name"), row_dict.get("last_name"),
                        row_dict.get("email"), row_dict.get("password"), row_dict.get("role"),
                        row_dict.get("status"), row_dict.get("access_token"),
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
        print(f"Error writing users to MySQL: {e}")
        raise


def clean_nans(obj):
    if isinstance(obj, float) and math.isnan(obj):
        return None
    if isinstance(obj, dict):
        return {k: clean_nans(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_nans(i) for i in obj]
    return obj
