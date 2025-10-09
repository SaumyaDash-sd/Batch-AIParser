import pandas as pd
import os
import math


# jobs_csv path
UPLOADED_FILES_CSV = os.path.join("database", "batch_jobs", "uploaded_files.csv")
BATCH_FILES_CSV = os.path.join("database", "batch_jobs", "batch_files.csv")
BATCH_JOBS_CSV = os.path.join("database", "batch_jobs", "batch_jobs.csv")


def read_uploaded_files():
    return pd.read_csv(UPLOADED_FILES_CSV)


def write_uploaded_files(df):
    df.to_csv(UPLOADED_FILES_CSV, index=False)


def read_batch_files():
    return pd.read_csv(BATCH_FILES_CSV)


def write_batch_files(df):
    df.to_csv(BATCH_FILES_CSV, index=False)


def read_batch_jobs():
    return pd.read_csv(BATCH_JOBS_CSV)


def write_batch_jobs(df):
    df.to_csv(BATCH_JOBS_CSV, index=False)

# database/batch_jobs/batch_jobs.csv

def clean_nans(obj):
    if isinstance(obj, float) and math.isnan(obj):
        return None
    if isinstance(obj, dict):
        return {k: clean_nans(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_nans(i) for i in obj]
    return obj
