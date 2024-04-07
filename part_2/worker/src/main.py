import time, os, sys, json

from config import get_config
from aws import get_sqs_client, get_s3_client

def get_debts_id(sqs_client) -> str:
    response = sqs_client.receive_message(
                QueueUrl=config.worker_queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=1,
            )
    
    msgs = response["Messages"]
    msg = msgs[0]
    body = msg["Body"]
    json_body = json.loads(body)
    debts_id = json_body["debts_id"]

    return debts_id

def get_debts(debts_id, s3_client):
    return s3_client.get_object(
        Bucket=config.debts_bucket_name,
        Key=debts_id
    )

if __name__ == "__main__":
    config = get_config()

    while True:
        sqs_client = get_sqs_client()
        s3_client = get_s3_client()
        
        try:
            debts_id = get_debts_id(sqs_client)
            print("Got debts_id!!!")

            debts_info = get_debts(debts_id, s3_client)
            print("Got debts_info!!!")

            print(debts_info)



        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)

            time.sleep(1)