import time, os, sys, json, io, csv

from config import get_config
from aws import get_sqs_client, get_s3_client
from algorithm import calc_debts, optimize_transactions

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
    input_file = io.BytesIO()

    s3_client.download_fileobj(
        config.debts_bucket_name,
        debts_id,
        input_file
    )

    input_file.seek(0)
    file_content = input_file.getvalue().decode('utf-8')

    return calc_debts(io.StringIO(file_content))

def save_repays(repays, debts_id, s3_client):
    repays_file = io.StringIO()
    writer = csv.writer(repays_file, delimiter=',')

    print("Repays: ")
    print(repays)
    print("num of repays: ", len(repays))

    for debtor, creditor, amount in repays:
        writer.writerow([debtor, creditor, amount])
    
    repays_file.seek(0)
    bytes_buffer = io.BytesIO(repays_file.getvalue().encode('utf-8'))
    print(repays_file.getvalue())

    s3_client.upload_fileobj(
        Bucket=config.debts_bucket_name,
        Key=f"{debts_id}_results",
        Fileobj=bytes_buffer
    )

if __name__ == "__main__":
    config = get_config()

    while True:
        sqs_client = get_sqs_client()
        s3_client = get_s3_client()
        
        try:
            debts_id = get_debts_id(sqs_client)
            print("Got debts_id!!!")

            debts = get_debts(debts_id, s3_client)
            print("Got debts_info!!!")

            repays = optimize_transactions(debts)
            print("Got repays!!!")

            save_repays(repays, debts_id, s3_client)
            print("Saved repays!!!")
            # print(debts_info)



        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)

            time.sleep(1)