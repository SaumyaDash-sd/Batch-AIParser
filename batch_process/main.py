import logging

from . import steps


def batch_processing_create_file(user_id, filename, df, description_json):
    output_df = steps.create_file.start_process(df, description_json["unique_id_field"])
    # steps.upload_file()
    # steps.start_batch()
    # steps.download_file()

    return {"message": "Hello", "length": len(output_df)}


def batch_processing_upload_file(user_id, filename, df, description_json):
    file_ids_list = steps.upload_file.start_process(df, filename, description_json)

    return {"message": "Hello", "file_ids": file_ids_list}
