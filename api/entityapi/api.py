"""
Entity API.
"""
import json
import logging
import time
import uuid
from typing import Any, Collection, Dict, List, Optional

from bugout.data import BugoutJournalEntry
from bugout.exceptions import BugoutResponseException
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
from fastapi.middleware.cors import CORSMiddleware
from web3login.middlewares.fastapi import Web3AuthorizationMiddleware

from . import actions, data
from .settings import BUGOUT_APPLICATION_ID_HEADER, ENTITY_APPLICATION_ID, ORIGINS
from .settings import bugout_client as bc
from .version import VERSION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tags_metadata = [{"name": "time", "description": "Server timestamp endpoints."}]

whitelist_paths: Dict[str, str] = {}
whitelist_paths.update(
    {
        "/ping": "GET",
        "/now": "GET",
        "/docs": "GET",
        "/openapi.json": "GET",
    }
)


app = FastAPI(
    title=f"Entity HTTP API",
    description="Entity API endpoints.",
    version=VERSION,
    openapi_tags=tags_metadata,
    openapi_url="/openapi.json",
    docs_url=None,
)

app.add_middleware(
    Web3AuthorizationMiddleware,
    whitelist=whitelist_paths,
    application=ENTITY_APPLICATION_ID,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping", response_model=data.PingResponse)
async def ping_handler() -> data.PingResponse:
    """
    Check server status.
    """
    return data.PingResponse(status="ok")


@app.get("/now", tags=["time"])
async def now_handler() -> data.NowResponse:
    """
    Get server current time.
    """
    return data.NowResponse(epoch_time=time.time())


@app.post("/collections", response_model=data.EntityCollectionResponse)
async def add_entity_collection_handler(
    request: Request,
    create_request: data.CreateEntityCollectionAPIRequest = Body(...),
) -> data.EntityCollectionResponse:
    web3_signature = request.state.signature

    try:
        response = bc.create_journal(
            token=web3_signature,
            name=create_request.name,
            auth_type="web3",
            headers={BUGOUT_APPLICATION_ID_HEADER: ENTITY_APPLICATION_ID},
        )
    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return data.EntityCollectionResponse(name=response.name, collection_id=response.id)


@app.get("/collections", response_model=data.EntityCollectionsResponse)
async def list_entity_collections_handler(
    request: Request,
) -> data.EntityCollectionsResponse:
    web3_signature = request.state.signature

    try:
        response = bc.list_journals(
            token=web3_signature,
            auth_type="web3",
            headers={BUGOUT_APPLICATION_ID_HEADER: ENTITY_APPLICATION_ID},
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


@app.post("/collections/{collection_id}/entities", response_model=data.EntityResponse)
async def add_entity_handler(
    request: Request,
    collection_id: uuid.UUID = Path(...),
    create_request: data.CreateEntityRequest = Body(...),
) -> data.EntityResponse:
    web3_signature = request.state.signature
    try:
        create_entity = data.Entity.parse_obj(create_request)
        title, tags, content = await actions.parse_entity_to_entry(
            create_entity=create_entity
        )

        response: BugoutJournalEntry = bc.create_entry(
            token=web3_signature,
            journal_id=collection_id,
            title=title,
            content=json.dumps(content),
            tags=tags,
            context_type="entity",
            auth_type="web3",
            headers={BUGOUT_APPLICATION_ID_HEADER: ENTITY_APPLICATION_ID},
        )
    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    entity_response = await actions.parse_entry_to_entity(entry=response)

    return entity_response


@app.delete(
    "/collections/{collection_id}/entities/{entity_id}",
    response_model=data.EntityResponse,
)
async def delete_entity_handler(
    request: Request,
    collection_id: uuid.UUID = Path(...),
    entity_id: uuid.UUID = Path(...),
) -> data.EntityResponse:
    web3_signature = request.state.signature
    try:
        response: BugoutJournalEntry = bc.delete_entry(
            token=web3_signature,
            journal_id=collection_id,
            entry_id=entity_id,
            auth_type="web3",
            headers={BUGOUT_APPLICATION_ID_HEADER: ENTITY_APPLICATION_ID},
        )
    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    entity_response = await actions.parse_entry_to_entity(entry=response)

    return entity_response
