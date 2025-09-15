from .utils import execute_test_process


def test_prompt_process(dataframe, description_json):
    job_title = description_json["job_title"]
    prompt = description_json["prompt"]
    placeholder_field = description_json["placeholder_field"]
    unique_id_field = description_json["unique_id_field"]
    output_field = description_json["output_field"]
    chunk_size = description_json["config"]["chunkSize"]
    credentials = description_json["credentials"]


    result = execute_test_process(
        dataframe=dataframe,
        job_title=job_title,
        prompt=prompt,
        placeholder_field=placeholder_field,
        unique_id_column=unique_id_field,
        output_field=output_field,
        chunk_size = chunk_size,
        credentials = credentials,
    )

    return result
