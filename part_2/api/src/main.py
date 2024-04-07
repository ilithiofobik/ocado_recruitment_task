import pathlib

import uvicorn
from fastapi import FastAPI

from src.debts import debts_router

app = FastAPI()
app.include_router(debts_router, prefix="/debts")


def main():
    uvicorn.run(
        app=app,
        loop="uvloop",
        port=8000,
        host="0.0.0.0",
        log_level="info",
        log_config=str((pathlib.Path(__file__).parent / "logging.yml").resolve()),
    )


if __name__ == "__main__":
    main()
