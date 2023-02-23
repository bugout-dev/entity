"""
Entity public API endpoints.
"""
import json
import logging
import uuid
from typing import List, Optional

from bugout.data import BugoutJournalEntry, BugoutSearchResults
from bugout.exceptions import BugoutResponseException
from fastapi import Body, FastAPI, Form, HTTPException, Path, Query

from .. import actions, data
from ..settings import DOCS_TARGET_PATH, ETHDENVER_EVENT_CLAIMANT_PASSWORD
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
async def list_public_entity_collections_handler(
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
    "/collections/{collection_id}",
    tags=["public"],
    response_model=data.EntityCollectionResponse,
)
async def get_public_entity_collection_handler(
    collection_id: uuid.UUID = Path(...),
) -> data.EntityCollectionResponse:
    """
    Get public collections.
    """
    try:
        response = bc.get_public_journal(
            journal_id=collection_id,
        )
    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return data.EntityCollectionResponse(name=response.name, collection_id=response.id)


@app.get(
    "/collections/{collection_id}/entities",
    tags=["public"],
    response_model=data.EntitiesResponse,
)
async def get_public_entities_handler(
    collection_id: uuid.UUID = Path(...),
) -> data.EntitiesResponse:
    """
    Get public entities.
    """
    try:
        response = bc.get_public_journal_entries(journal_id=collection_id)

        entities_response = data.EntitiesResponse(entities=[])
        for entry in response.entries:
            entity_response = actions.parse_entry_to_entity(
                entry=entry, collection_id=collection_id
            )
            entities_response.entities.append(entity_response)
    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return entities_response


@app.get(
    "/collections/{collection_id}/entities/{entity_id}",
    tags=["public"],
    response_model=data.EntityResponse,
)
async def get_public_entity_handler(
    collection_id: uuid.UUID = Path(...),
    entity_id: uuid.UUID = Path(...),
) -> data.EntityResponse:
    """
    Get public entity.
    """
    try:
        response = bc.get_public_journal_entry(
            journal_id=collection_id, entry_id=entity_id
        )

        entity_response = actions.parse_entry_to_entity(
            entry=response, collection_id=collection_id
        )
    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return entity_response


@app.put(
    "/collections/{collection_id}/entities/{entity_id}",
    tags=["public"],
    response_model=List[str],
)
async def touch_public_entity_handler(
    collection_id: uuid.UUID = Path(...),
    entity_id: uuid.UUID = Path(...),
) -> List[str]:
    """
    Touch public entity.
    """
    try:
        response = bc.touch_public_journal_entry(
            journal_id=collection_id, entry_id=entity_id
        )
    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return response


@app.post(
    "/collections/{collection_id}/entities",
    tags=["public"],
    response_model=data.EntityResponse,
)
async def add_public_entity_handler(
    collection_id: uuid.UUID = Path(...),
    create_request: data.Entity = Body(...),
) -> data.EntityResponse:
    """
    Create public entity.
    """
    try:
        title, tags, content = actions.parse_entity_to_entry(
            create_entity=create_request
        )

        response = bc.create_public_journal_entry(
            journal_id=collection_id,
            title=title,
            content=json.dumps(content),
            tags=tags,
            context_type="entity",
        )

        entity_response = actions.parse_entry_to_entity(
            entry=response, collection_id=collection_id
        )
    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return entity_response


@app.post(
    "/collections/{collection_id}/entities/protected",
    tags=["public"],
    response_model=data.EntityResponse,
)
async def add_public_entity_password_protected_handler(
    collection_id: uuid.UUID = Path(...),
    address: str = Form(...),
    blockchain: str = Form(...),
    name: str = Form(...),
    password: str = Form(...),
    email: str = Form(None),
    discord: str = Form(None),
) -> data.EntityResponse:
    """
    Create public entity if password specified.
    """
    if password != ETHDENVER_EVENT_CLAIMANT_PASSWORD:
        raise HTTPException(status_code=403, detail="Provided incorrect password")

    required_fields = [{"protected": "true"}]
    if email is not None:
        required_fields.append({"email": email})
    if discord is not None:
        required_fields.append({"discord": discord})

    try:
        title, tags, content = actions.parse_entity_to_entry(
            create_entity=data.Entity(
                address=address,
                blockchain=blockchain,
                name=name,
                required_fields=required_fields,
            )
        )

        response = bc.create_public_journal_entry(
            journal_id=collection_id,
            title=title,
            content=json.dumps(content),
            tags=tags,
            context_type="entity",
        )

        entity_response = actions.parse_entry_to_entity(
            entry=response, collection_id=collection_id
        )
    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return entity_response


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
