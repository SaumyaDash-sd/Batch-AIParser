import pandas as pd
import os

#users_csv path
USERS_CSV = os.path.join("database", "users.csv")

def read_users():
    return pd.read_csv(USERS_CSV)

def write_users(df):
    df.to_csv(USERS_CSV, index=False)


