import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import data
from .apps.main import app as main_app
from .apps.public import app as public_app
from .settings import ORIGINS
from .version import VERSION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tags_metadata = [{"name": "time", "description": "Server timestamp endpoints."}]

app = FastAPI(
    title=f"Entity HTTP API",
    description="Entity API endpoints.",
    version=VERSION,
    openapi_tags=tags_metadata,
    openapi_url=None,
    docs_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/entity/ping", response_model=data.PingResponse)
async def ping_handler() -> data.PingResponse:
    """
    Check server status.
    """
    return data.PingResponse(status="ok")


@app.get("/entity/now", tags=["time"])
async def now_handler() -> data.NowResponse:
    """
    Get server current time.
    """
    return data.NowResponse(epoch_time=time.time())


@app.get("/entity/version", response_model=data.VersionResponse)
async def version_handler() -> data.VersionResponse:
    """
    Check server version.
    """
    return data.VersionResponse(version=VERSION)


app.mount("/entity/public", public_app)
app.mount("/entity", main_app)
