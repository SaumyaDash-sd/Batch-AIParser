import pandas as pd
import os
import math


# users_csv path
USERS_CSV = os.path.join("database", "users.csv")


def read_users():
    return pd.read_csv(USERS_CSV)


def write_users(df):
    df.to_csv(USERS_CSV, index=False)


def clean_nans(obj):
    if isinstance(obj, float) and math.isnan(obj):
        return None
    if isinstance(obj, dict):
        return {k: clean_nans(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_nans(i) for i in obj]
    return obj
