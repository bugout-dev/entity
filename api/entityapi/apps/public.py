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
from ..settings import DOCS_TARGET_PATH
from ..settings import bugout_client as bc
from ..version import VERSION

logger = logging.getLogger(__name__)

SUBMODULE_NAME = "public"

tags_metadata = [{"name": "public", "description": "Public entity endpoints."}]

app = FastAPI(
    title=f"Entity {SUBMODULE_NAME} HTTP API",
    description=f"Entity {SUBMODULE_NAME}  API endpoints.",
    version=VERSION,
    openapi_tags=tags_metadata,
    openapi_url="/openapi.json",
    docs_url=None,
    redoc_url=f"/{DOCS_TARGET_PATH}",
)


@app.get("/collections", tags=["public"], response_model=data.EntityCollectionsResponse)
async def public_list_entity_collections_handler(
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


@app.get(
    "/collections/{collection_id}/search",
    tags=["public"],
    response_model=data.EntitySearchResponse,
)
async def public_search_entity_handler(
    collection_id: uuid.UUID = Path(...),
    required_field: List[str] = Query(default=[]),
    secondary_field: List[str] = Query(default=[]),
    filters: Optional[List[str]] = Query(None),
    limit: int = Query(10),
    offset: int = Query(0),
    content: bool = Query(True),
) -> data.EntitySearchResponse:
    q = actions.to_journal_search_format(
        required_field=required_field,
        secondary_field=secondary_field,
    )

    try:
        response: BugoutSearchResults = bc.public_search(
            journal_id=collection_id,
            query=q,
            filters=filters,
            limit=limit,
            offset=offset,
            content=content,
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
                collection_id=collection_id,
            )
            entities_response.entities.append(entity_response)

    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return entities_response
