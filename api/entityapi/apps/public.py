"""
Entity public API endpoints.
"""
import json
import logging
import time
import uuid
from typing import Any, Collection, Dict, List, Optional, Union

from bugout.data import (
    BugoutJournalEntries,
    BugoutJournalEntry,
    BugoutJournalEntryContent,
    BugoutSearchResults,
)
from bugout.exceptions import BugoutResponseException
from bugout.journal import TagsAction
from fastapi import (
    BackgroundTasks,
    Body,
    Depends,
    FastAPI,
    Form,
    HTTPException,
    Path,
    Query,
    Request,
    Response,
    status,
)

from .. import actions, data
from ..settings import bugout_client as bc
from ..version import VERSION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUBMODULE_NAME = "public"

tags_metadata = [{"name": "public", "description": "Public endpoints."}]

app = FastAPI(
    title=f"Entity {SUBMODULE_NAME} HTTP API",
    description=f"Entity {SUBMODULE_NAME}  API endpoints.",
    version=VERSION,
    openapi_tags=tags_metadata,
    openapi_url="/entity/public/openapi.json",
    docs_url=None,
)


@app.get("/collections", response_model=data.EntityCollectionsResponse)
async def version_handler(
    user_id: uuid.UUID = Query(...),
) -> data.EntityCollectionsResponse:
    """
    List all public collections.
    """
    try:
        response = bc.list_public_journals(
            user_id=user_id,
        )
    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return data.EntityCollectionsResponse(
        collections=[
            data.EntityCollectionResponse(name=journal.name, collection_id=journal.id)
            for journal in response.journals
        ]
    )
