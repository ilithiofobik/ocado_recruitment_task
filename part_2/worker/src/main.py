import time
import json
import csv

from config import get_config
from aws import get_sqs_client, get_s3_client
from algorithm import calc_debts, optimize_transactions
from io import StringIO, BytesIO

# Function getting the next debts_id from the queue
def get_debts_id(sqs_client) -> str:
    response = sqs_client.receive_message(
                QueueUrl=config.worker_queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=1,
            )
    
    body = response["Messages"][0]["Body"]
    json_body = json.loads(body)
    debts_id = json_body["debts_id"]

    return debts_id

# Function getting the debts from the S3 bucket
def get_debts(debts_id, s3_client) -> dict:
    input_file = BytesIO()

    s3_client.download_fileobj(
        config.debts_bucket_name,
        debts_id,
        input_file
    )

    input_file.seek(0)
    file_content = input_file.getvalue().decode('utf-8')

    # Converting to StringIO to be able to use csv.reader
    return calc_debts(StringIO(file_content))

# Function saving the repays to the S3 bucket
def save_repays(repays, debts_id, s3_client):
    repays_file = StringIO()
    writer = csv.writer(repays_file)

    for debtor, creditor, amount in repays:
        writer.writerow([debtor, creditor, amount])
    
    repays_file.seek(0)
    bytes_buffer = BytesIO(repays_file.getvalue().encode('utf-8'))

    s3_client.upload_fileobj(
        Bucket=config.debts_bucket_name,
        Key=f"{debts_id}_results",
        Fileobj=bytes_buffer
    )

if __name__ == "__main__":
    # Get the config and the clients before main loop
    config = get_config()
    sqs_client = get_sqs_client()
    s3_client = get_s3_client()

    while True:
        # The errors can occur when the queue is empty
        try:
            # First check if there are any messages in the queue
            # If not fail, the exception will be caught
            debts_id = get_debts_id(sqs_client)
            # Download the debts from the S3 bucket
            debts = get_debts(debts_id, s3_client)
            # Optimize the transactions
            repays = optimize_transactions(debts)
            # Save the repays to the S3 bucket
            save_repays(repays, debts_id, s3_client)

        except Exception as e:
            # If an error occurs, wait for one second
            time.sleep(1)