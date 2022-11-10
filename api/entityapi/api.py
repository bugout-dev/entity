"""
Entity API.
"""
import json
import logging
import time
import uuid
from typing import Any, Collection, Dict, List, Optional

from bugout.data import BugoutJournalEntry, BugoutJournalEntries, BugoutSearchResults
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
from .settings import BUGOUT_APPLICATION_ID_HEADER, MOONSTREAM_APPLICATION_ID, ORIGINS
from .settings import bugout_client as bc
from .version import VERSION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tags_metadata = [{"name": "time", "description": "Server timestamp endpoints."}]

whitelist_paths: Dict[str, str] = {}
whitelist_paths.update(
    {
        "/entity/ping": "GET",
        "/entity/now": "GET",
        "/entity/docs": "GET",
        "/entity/openapi.json": "GET",
    }
)


app = FastAPI(
    title=f"Entity HTTP API",
    description="Entity API endpoints.",
    version=VERSION,
    openapi_tags=tags_metadata,
    openapi_url="/entity/openapi.json",
    docs_url=None,
)

app.add_middleware(
    Web3AuthorizationMiddleware,
    whitelist=whitelist_paths,
    application=MOONSTREAM_APPLICATION_ID,
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


@app.post("/entity/collections", response_model=data.EntityCollectionResponse)
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
            headers={BUGOUT_APPLICATION_ID_HEADER: MOONSTREAM_APPLICATION_ID},
        )
    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return data.EntityCollectionResponse(name=response.name, collection_id=response.id)


@app.get("/entity/collections", response_model=data.EntityCollectionsResponse)
async def list_entity_collections_handler(
    request: Request,
) -> data.EntityCollectionsResponse:
    web3_signature = request.state.signature

    try:
        response = bc.list_journals(
            token=web3_signature,
            auth_type="web3",
            headers={BUGOUT_APPLICATION_ID_HEADER: MOONSTREAM_APPLICATION_ID},
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


@app.post(
    "/entity/collections/{collection_id}/entities", response_model=data.EntityResponse
)
async def add_entity_handler(
    request: Request,
    collection_id: uuid.UUID = Path(...),
    create_request: data.Entity = Body(...),
) -> data.EntityResponse:
    web3_signature = request.state.signature
    try:
        title, tags, content = actions.parse_entity_to_entry(
            create_entity=create_request
        )

        response: BugoutJournalEntry = bc.create_entry(
            token=web3_signature,
            journal_id=collection_id,
            title=title,
            content=json.dumps(content),
            tags=tags,
            context_type="entity",
            auth_type="web3",
            headers={BUGOUT_APPLICATION_ID_HEADER: MOONSTREAM_APPLICATION_ID},
        )

        entity_response = actions.parse_entry_to_entity(
            entry=response, collection_id=str(collection_id)
        )

    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return entity_response


@app.post(
    "/entity/collections/{collection_id}/bulk", response_model=data.EntitiesResponse
)
async def add_entity_bulk_handler(
    request: Request,
    collection_id: uuid.UUID = Path(...),
    create_request: List[data.Entity] = Body(...),
) -> data.EntitiesResponse:
    web3_signature = request.state.signature
    try:
        create_entries = []
        for entity in create_request:
            title, tags, content = actions.parse_entity_to_entry(create_entity=entity)
            create_entries.append(
                {
                    "title": title,
                    "tags": tags,
                    "content": json.dumps(content),
                    "context_type": "entity",
                }
            )

        response: BugoutJournalEntries = bc.create_entries_pack(
            token=web3_signature,
            journal_id=collection_id,
            entries=create_entries,
            auth_type="web3",
            headers={BUGOUT_APPLICATION_ID_HEADER: MOONSTREAM_APPLICATION_ID},
        )

        entities_response = data.EntitiesResponse(entities=[])
        for entry in response.entries:
            entity_response = actions.parse_entry_to_entity(
                entry=entry, collection_id=str(collection_id)
            )
            entities_response.entities.append(entity_response)

    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return entities_response


@app.get(
    "/entity/collections/{collection_id}/entities", response_model=data.EntitiesResponse
)
async def get_entities_handler(
    request: Request,
    collection_id: uuid.UUID = Path(...),
) -> data.EntitiesResponse:
    web3_signature = request.state.signature
    try:
        response = bc.get_entries(
            token=web3_signature,
            journal_id=collection_id,
            auth_type="web3",
            headers={BUGOUT_APPLICATION_ID_HEADER: MOONSTREAM_APPLICATION_ID},
        )

        entities_response = data.EntitiesResponse(entities=[])
        for entry in response.entries:
            entity_response = actions.parse_entry_to_entity(
                entry=entry, collection_id=str(collection_id)
            )
            entities_response.entities.append(entity_response)

    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return entities_response


@app.delete(
    "/entity/collections/{collection_id}/entities/{entity_id}",
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
            headers={BUGOUT_APPLICATION_ID_HEADER: MOONSTREAM_APPLICATION_ID},
        )
    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return data.EntityResponse(entity_id=response.id, collection_id=collection_id)


@app.get(
    "/entity/collections/{collection_id}/search",
    response_model=data.EntitySearchResponse,
)
async def search_entity_handler(
    request: Request,
    collection_id: uuid.UUID = Path(...),
    q: str = Query(""),
    filters: Optional[List[str]] = Query(None),
    limit: int = Query(10),
    offset: int = Query(0),
    content: Optional[bool] = Query(True),
) -> data.EntitySearchResponse:
    web3_signature = request.state.signature
    try:
        response: BugoutSearchResults = bc.search(
            token=web3_signature,
            journal_id=collection_id,
            query=q,
            filters=filters,
            limit=limit,
            offset=offset,
            content=content,
            auth_type="web3",
            headers={BUGOUT_APPLICATION_ID_HEADER: MOONSTREAM_APPLICATION_ID},
        )

        entities_response = data.EntitySearchResponse(
            total_results=response.total_results,
            offset=response.offset,
            next_offset=response.next_offset,
            max_score=response.max_score,
            entities=[],
        )
        for entry in response.results:
            entity_response = actions.parse_entry_to_entity(
                entry=BugoutJournalEntry(
                    id=entry.entry_url.rstrip("/").split("/")[-1],
                    title=entry.title,
                    content=entry.content,
                    tags=entry.tags,
                    created_at=entry.created_at,
                    updated_at=entry.updated_at,
                ),
                collection_id=str(collection_id),
            )
            entities_response.entities.append(entity_response)

    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return entities_response
