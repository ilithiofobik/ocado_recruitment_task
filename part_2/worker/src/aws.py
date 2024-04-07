from typing import TYPE_CHECKING, Any, Literal, overload

import boto3

from src.config import get_config

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client
    from mypy_boto3_sqs import SQSClient


def get_s3_client() -> "S3Client":
    return boto3.client("s3")


def get_sqs_client() -> "SQSClient":
    return boto3.client("sqs")
