import logging
import uuid
from http import HTTPStatus
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.aws import get_s3_client, get_sqs_client
from src.config import get_config

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client
    from mypy_boto3_sqs import SQSClient

logger = logging.getLogger(__name__)

debts_router = APIRouter()


class Task(BaseModel):
    debts_id: str


@debts_router.post("/")
async def upload_debts(
    file: UploadFile,
    sqs_client: "SQSClient" = Depends(get_sqs_client),
    s3_client: "S3Client" = Depends(get_s3_client),
) -> str:
    config = get_config()

    debts_id = str(uuid.uuid4())

    logger.info(f"Uploading debts {debts_id} file to S3")

    s3_client.upload_fileobj(
        Bucket=config.debts_bucket_name,
        Key=debts_id,
        Fileobj=file.file,
    )

    logger.info(f"Sending debts {debts_id} to the worker queue")

    sqs_client.send_message(
        QueueUrl=config.worker_queue_url,
        MessageBody=Task(debts_id=debts_id).model_dump_json(),
    )

    return debts_id


@debts_router.get("/{debts_id}")
async def download_debts(
    debts_id: str,
    s3_client: "S3Client" = Depends(get_s3_client),
) -> StreamingResponse:
    config = get_config()

    try:
        response = s3_client.get_object(
            Bucket=config.debts_bucket_name,
            Key=debts_id,
        )
    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Debts with id {debts_id} not found",
        ) from None

    return StreamingResponse(
        content=response["Body"].iter_chunks(),
        media_type="text/csv",
    )


@debts_router.get("/{debts_id}/results")
async def download_results(
    debts_id: str,
    s3_client: "S3Client" = Depends(get_s3_client),
) -> StreamingResponse:
    config = get_config()

    try:
        response = s3_client.get_object(
            Bucket=config.debts_bucket_name,
            Key=f"{debts_id}_results",
        )
    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Results for debts with id {debts_id} not found",
        ) from None

    return StreamingResponse(
        content=response["Body"].iter_chunks(),
        media_type="text/csv",
    )
