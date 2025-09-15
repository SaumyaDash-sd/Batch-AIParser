import pandas as pd
from .utils import execute_threads

from .utils import main_1


def test_prompt_process(dataframe, description_json):
    job_title = description_json["job_title"]
    prompt = description_json["prompt"]
    placeholder_field = description_json["placeholder_field"]
    unique_id_field = description_json["unique_id_field"]
    output_field = description_json["output_field"]
    chunk_size = description_json["config"]["chunkSize"]
    credentials = description_json["credentials"]

    result = main_1(
        dataframe=dataframe,
        job_title=job_title,
        prompt=prompt,
        placeholder_field=placeholder_field,
        unique_id_column=unique_id_field,
        output_field=output_field,
        chunk_size = chunk_size,
        credentials = credentials

    )

    return result
    # Load CSV (sample 10 rows for testing)
    # dataframe = pd.read_csv("remaining_lot2_attribute_338_inoutfile.csv").sample(config["sample_size"])
    # # dataframe = data.read_csv("remaining_lot2_attribute_338_inoutfile.csv").sample(10)

    # # Process with threading
    # output_df = execute_threads(dataframe, prompt, unique_id_column, placeholder_field, output_field, config, credentials, thread_count=20)

    # # Save results
    # output_df.to_excel("remainining_338_aug_attribute_footer_file.xlsx", index=False)
    # print("✅ Content generation completed and saved to 'remainining_338_aug_attribute_footer_file.xlsx'")

    # return {"message": "Function `test_prompt_process` executed successfully"}


if __name__ == "__main__":
    test_prompt_process()
