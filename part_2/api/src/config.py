from pydantic_settings import BaseSettings


class Config(BaseSettings):
    debts_bucket_name: str
    worker_queue_url: str


def get_config() -> Config:
    return Config()  # type: ignore
