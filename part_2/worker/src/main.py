import time

from config import get_config
from aws import get_sqs_client

def  get_debts_id(sqs_client):
    msg = sqs_client.receive_message(
                QueueUrl=config.worker_queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=1,
            )

    return msg["Messages"][0]["Body"]["debts_id"]

def get_debts(debts_id):
    pass

if __name__ == "__main__":
    config = get_config()

    while True:
        sqs_client = get_sqs_client()
        
        try:
            debts_id = get_debts_id(sqs_client)
            print(f"Got debts_id: {debts_id}")




        except Exception as e:
            print("Got an error: ", e)    
            time.sleep(1)