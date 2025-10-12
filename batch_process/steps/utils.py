import re
import ast
import json
import pandas as pd
from io import BytesIO


def handling_gpt_output(gpt_response: str) -> dict:
    """
    Attempts to parse the provided GPT response as a list or dictionary.
    If that fails, extracts the content between the first and last curly braces
    and parses it using ast.literal_eval.

    Args:
        gpt_response (str): The GPT response to be parsed.

    Returns:
        dict: The parsed GPT response as a dictionary, or an empty dictionary if parsing fails.
    """
    try:
        # Attempt to parse the entire response
        parsed = ast.literal_eval(gpt_response)
        if isinstance(parsed, (dict, list)):
            return parsed
        else:
            pass
    except Exception as e:
        pass
    # Fallback: extract content between the first and last curly braces
    try:
        start_index = gpt_response.find("{")
        end_index = gpt_response.rfind("}")
        if start_index != -1 and end_index != -1:
            extracted_content = gpt_response[start_index : end_index + 1]
            parsed = ast.literal_eval(extracted_content)
            return parsed
    except Exception as inner_e:
        pass
    return {}


def output_jsonl_to_dataframe(jsonl_bytes: bytes) -> pd.DataFrame:
    """
    Convert a .jsonl byte stream (with GPT responses) into a structured pandas DataFrame.

    Args:
        jsonl_bytes (bytes): Byte content of a .jsonl file.
        parse_gpt_output (callable): Function that takes the GPT 'content' string and
                                     returns a valid Python dict.

    Returns:
        pd.DataFrame: Structured dataframe with expanded GPT content fields.
    """
    records = []
    buffer = BytesIO(jsonl_bytes)

    for raw_line in buffer:
        line = raw_line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
            resp = row.get("response", {}).get("body", {})
            model_name = resp.get("model")
            choices = resp.get("choices", [])
            message = choices[0]["message"] if choices else {}
            content = message.get("content", "")

            # Parse GPT JSON output
            parsed_content = {}
            try:
                parsed_content = handling_gpt_output(content) or {}
                print(parsed_content)
            except Exception:
                pass  # fallback to empty dict if malformed

            usage = resp.get("usage", {})
            record = {
                "unique_id": row.get("custom_id"),
                "model_name": model_name,
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
                **parsed_content,  # flatten parsed GPT JSON keys
            }
            records.append(record)

        except Exception:
            # skip malformed line gracefully
            continue

    # Create DataFrame
    df = pd.DataFrame(records)

    # Sort by unique_id (if present)
    if "unique_id" in df.columns:
        df = df.sort_values(by="unique_id", ascending=True, ignore_index=True)

    return df


def input_jsonl_to_dataframe(jsonl_bytes: bytes) -> pd.DataFrame:
    """
    Convert a .jsonl byte stream (with GPT request data) into a structured pandas DataFrame.

    Args:
        jsonl_bytes (bytes): Byte content of a .jsonl file.

    Returns:
        pd.DataFrame: Structured dataframe with columns:
                      unique_id, model_name, temperature, message_prompt
    """
    records = []
    buffer = BytesIO(jsonl_bytes)

    for raw_line in buffer:
        line = raw_line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
            body = row.get("body", {})

            record = {
                "unique_id": row.get("custom_id"),
                "model_name": body.get("model"),
                "temperature": body.get("temperature"),
                "message_prompt": body.get("messages", []),
            }

            records.append(record)

        except Exception:
            continue  # skip malformed rows safely

    df = pd.DataFrame(records)

    # Sort by unique_id if available
    if "unique_id" in df.columns:
        df = df.sort_values(by="unique_id", ascending=True, ignore_index=True)

    return df
