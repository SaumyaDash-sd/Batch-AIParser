import uuid
from .utils import read_users, write_users 


def validate_user(email: str, password: str):
    df = read_users()

    # Find user by email
    user_idx = df.index[df["email"] == email].tolist()
    if not user_idx:
        return {
        "status_code": 401,
        "message": "unauthorized"
    }, df

    idx = user_idx[0]
    user = df.loc[idx]

    # Success case
    if user["password"] == password and str(user["status"]).lower() == "active":
        new_token = str(uuid.uuid4())
        df.at[idx, "access_token"] = new_token
        write_users(df)
        
        return {
            "status_code": 200,
            "user_id": user["id"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"],
            "role": user["role"],
            "access_token": new_token,#user["access_token"],
            "message": "Login Successful"
        }, df

    return {
        "status_code": 401,
        "message": "unauthorized"
    }, df
    
    
def authenticate_user_token(user_id: str, access_token: str) -> bool:
    """Check if a user exists with given user_id, access_token 
            and status = active.
            Returns True if valid, otherwise False.
            """
    try:
        df = read_users()
        user = df[
            (df["id"] == user_id) &
            (df["access_token"] == access_token) &
            (df["status"].str.lower() == "active")
        ]

        return not user.empty  # True if user exists
    except Exception:
        return False
    

def get_user_by_id(user_id: str):
    df = read_users()

    # Find user by id
    user_idx = df.index[df["id"] == user_id].tolist()
    if not user_idx:
        return {
            "status_code": 404,
            "message": "User not found"
        }

    idx = user_idx[0]
    user = df.loc[idx]

    # Check if user is active
    if str(user["status"]).lower() != "active":
        return {
            "status_code": 403,
            "message": "User is not active"
        }

    # # Generate new access token
    # new_token = str(uuid.uuid4())
    # df.at[idx, "access_token"] = new_token
    # write_users(df)

    return {
        "status_code": 200,
        "user_id": user["id"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "role": user["role"],
        "access_token": user["access_token"],
        "message": "User details fetched successfully"
    }
