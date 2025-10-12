# Import necessary libraries
import os
import logging
import re
import pandas as pd
import json
import time
import threading
from tqdm import tqdm
from openai import AzureOpenAI
from datetime import datetime


def clean_dataframe(dataframe, unique_id_column_name):
    """
    Cleans a DataFrame by:
    1. Removing rows where the unique ID is NaN or 0.
    2. Keeping only unique IDs (drop duplicates).
    3. Dropping fully duplicated rows across all other columns.

    Parameters:
        dataframe (pd.DataFrame): Input DataFrame.
        unique_id_column_name (str): Name of the unique ID column.

    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """

    df = dataframe.copy()  # avoid modifying original

    # ---- NEW: Handle null unique_id_column ----
    if not unique_id_column_name:
        unique_id_column_name = "unique_id"
        logging.info(
            f"No unique_id_column provided. Creating new column '{unique_id_column_name}'."
        )
        # Ensure the new column name doesn't already exist
        if unique_id_column_name in df.columns:
            raise ValueError(
                f"Default ID column '{unique_id_column_name}' already exists in the dataframe. Please provide a unique column name."
            )
        # Assign incrementing integers as the unique ID
        df[unique_id_column_name] = range(1, len(df) + 1)

    # 1️⃣ Drop rows where the unique ID is NaN
    df.dropna(subset=[unique_id_column_name], inplace=True)

    # 2️⃣ Drop rows where the unique ID is 0
    df = df[df[unique_id_column_name] != 0]

    # 3️⃣ Drop duplicate IDs, keep first occurrence
    df.drop_duplicates(subset=[unique_id_column_name], keep="first", inplace=True)

    # 4️⃣ Drop fully duplicated rows across all columns except unique ID
    other_columns = df.columns.difference([unique_id_column_name])
    df.drop_duplicates(subset=other_columns, inplace=True)

    # Reset index
    df.reset_index(drop=True, inplace=True)

    return df


def add_prompt_column(dataframe, prompt, prompt_column_name="prompt"):
    """
    Adds a new column to the DataFrame, filling all rows with the same prompt text.

    Parameters:
        df (pd.DataFrame): The input DataFrame.
        prompt (str): The text to fill in the new column.
        prompt_column_name (str): Name of the new column (default: 'prompt').

    Returns:
        pd.DataFrame: DataFrame with the new column added.
    """
    dataframe[prompt_column_name] = prompt
    return dataframe


def replace_placeholders_with_col_values(
    dataframe, placeholder_fields, prompt_column_name="prompt"
):
    """
    Replaces placeholders in the 'prompt' column of a DataFrame with values from other columns.

    Parameters:
        df (pd.DataFrame): Input DataFrame, must have a 'prompt' column.
        placeholder_fields (dict): Dictionary mapping placeholders (without braces) to column names.
            Example: {'input_url': 'url_column'}
        prompt_column_name (str): Name of the new column (default: 'prompt').

    Returns:
        pd.DataFrame: DataFrame with the 'prompt' column updated with placeholders replaced.
    """

    df = dataframe.copy()  # avoid modifying original

    def replace_placeholders(prompt, row):
        # For each placeholder, replace {{placeholder}} with corresponding row value
        for placeholder, col_name in placeholder_fields.items():
            prompt = re.sub(
                r"\{\{\s*" + re.escape(placeholder) + r"\s*\}\}",
                str(row[col_name]),
                prompt,
            )
        return prompt

    # Apply row-wise replacement
    df[prompt_column_name] = df.apply(
        lambda row: replace_placeholders(row[prompt_column_name], row), axis=1
    )

    # Reset index
    df.reset_index(drop=True, inplace=True)

    return df


def start_process(dataframe, unique_id_column_name):
    df1 = clean_dataframe(dataframe, unique_id_column_name)
    df2 = add_prompt_column(df1, prompt)
    df3 = replace_placeholders_with_col_values(df2, placeholder_field)

    return df3


if __name__ == "__main__":
    dataframe = pd.read_excel("URLs for AI Testing .xlsx")
    unique_id_column_name = "UNIQUE_ID"  # Column to be used as custom_id
    prompt = """
    Return the category of the provided url, in a json format.
    
    URL is: {{input_url}}
    
    
    your output should be in this json format only:
    {
    "category": "your suggested category for input url"
    }
    """
    placeholder_field = {"input_url": "URL"}

    df1 = clean_dataframe(dataframe, unique_id_column_name)
    df2 = add_prompt_column(df1, prompt)
    df3 = replace_placeholders_with_col_values(df2, placeholder_field)
    df3.to_excel("test output.xlsx", index=False)
