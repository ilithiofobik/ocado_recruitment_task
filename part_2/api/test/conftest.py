import os

import boto3
import pytest
from moto import mock_aws

from src.aws import get_s3_client, get_sqs_client
from src.main import app

TEST_BUCKET_NAME = "test-debts-bucket"
TEST_WORKER_QUEUE_NAME = "test-worker-queue"


@pytest.fixture(scope="session", autouse=True)
def worker_config():
    os.environ["REGION"] = "us-east-1"
    os.environ["ENDPOINT_URL"] = "http://moto:1234"
    os.environ["DEBTS_BUCKET_NAME"] = TEST_BUCKET_NAME
    os.environ["WORKER_QUEUE_URL"] = f"http://moto:1234/{TEST_WORKER_QUEUE_NAME}"


@pytest.fixture(scope="session", autouse=True)
def test_setup():
    with mock_aws():
        # mock clients
        s3_client = boto3.client("s3")
        sqs_client = boto3.client("sqs")
        app.dependency_overrides[get_sqs_client] = lambda: sqs_client
        app.dependency_overrides[get_s3_client] = lambda: s3_client

        # setup bucket
        s3_client.create_bucket(Bucket=TEST_BUCKET_NAME)

        # setup queue
        sqs_client.create_queue(QueueName=TEST_WORKER_QUEUE_NAME)

        yield


@pytest.fixture(scope="session")
def debts_bucket():
    s3 = boto3.resource("s3")
    return s3.Bucket(TEST_BUCKET_NAME)


@pytest.fixture(scope="session")
def worker_queue():
    sqs = boto3.resource("sqs")
    return sqs.get_queue_by_name(QueueName=TEST_WORKER_QUEUE_NAME)
