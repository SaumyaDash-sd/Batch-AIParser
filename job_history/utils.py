import pandas as pd
import os
import math


# jobs_csv path
JOBS_CSV = os.path.join("database", "job_history.csv")


def read_jobs():
    return pd.read_csv(JOBS_CSV)


def write_jobs(df):
    df.to_csv(JOBS_CSV, index=False)


def clean_nans(obj):
    if isinstance(obj, float) and math.isnan(obj):
        return None
    if isinstance(obj, dict):
        return {k: clean_nans(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_nans(i) for i in obj]
    return obj
