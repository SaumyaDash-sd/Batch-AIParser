import pandas as pd
import os

#jobs_csv path
JOBS_CSV = os.path.join("database", "job_history.csv")

def read_jobs():
    return pd.read_csv(JOBS_CSV)


def write_jobs(df):
    df.to_csv(JOBS_CSV, index=False)


def append_job_history_(job_data):
    ...
