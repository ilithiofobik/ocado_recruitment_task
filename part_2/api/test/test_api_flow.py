import json
import pathlib
import uuid

from fastapi.testclient import TestClient

from src.main import app

test_dir_path = pathlib.Path(__file__).parent.resolve()


def test_upload_debts(debts_bucket, worker_queue) -> None:
    client = TestClient(app)

    # given a debts file
    debts_file = test_dir_path / "data/debts.csv"
    with open(debts_file, "rb") as file:
        # when the file is uploaded
        response = client.post(
            "/debts/",
            files={"file": ("debts.csv", file, "text/csv")},
        )

    # then the response should be successful
    assert response.status_code == 200
    # and the response should contain the debts id
    debts_id = response.json()
    assert uuid.UUID(debts_id).version == 4

    # and the debts file should be uploaded to the bucket
    debts_object = debts_bucket.Object(debts_id).get()
    assert debts_object["Body"].read() == debts_file.read_bytes()

    # and the message should be sent to the queue
    messages = worker_queue.receive_messages(
        MaxNumberOfMessages=1,
        WaitTimeSeconds=1,
        VisibilityTimeout=0,
    )
    assert json.loads(messages[0].body)["debts_id"] == debts_id

    # and the debts file should be available for download
    response = client.get(f"/debts/{debts_id}")
    assert response.status_code == 200
    assert response.content == debts_file.read_bytes()


def test_download_results(debts_bucket) -> None:
    client = TestClient(app)

    # given that results are stored in the bucket
    debts_id = str(uuid.uuid4())
    results_file = test_dir_path / "data/results.csv"
    with open(results_file, "rb") as file:
        debts_bucket.upload_fileobj(
            Key=f"{debts_id}_results",
            Fileobj=file,
        )

    # when the results are requested
    response = client.get(f"/debts/{debts_id}/results")

    # then the response should be successful
    assert response.status_code == 200
    # and the response should contain the results file
    assert response.content == results_file.read_bytes()
