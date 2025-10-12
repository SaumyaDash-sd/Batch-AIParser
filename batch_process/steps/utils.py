import re
import json
import pandas as pd
from io import BytesIO


def handling_gpt_output(gpt_response):
    """
    Extracts and formats GPT response into JSON safely.
    - Finds content between the first '{' and last '}'.
    - Parses it into a dict if valid JSON.
    - If no braces exist, returns the raw output.
    """
    if not gpt_response:
        return {}

    # Find JSON substring between first '{' and last '}'
    match = re.search(r"\{.*\}", gpt_response, re.DOTALL)
    if match:
        json_str = match.group(0).strip()
        try:
            parsed = json.loads(json_str)
            if isinstance(parsed, dict):
                return parsed
            return {"raw_output": parsed}
        except Exception:
            return {
                "raw_output": json_str
            }  # Return extracted string if JSON parsing fails

    # No curly braces found → return raw response
    return {"raw_output": gpt_response.strip()}


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
