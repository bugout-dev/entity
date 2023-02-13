"""
Entity main API endpoints.
"""
import json
import logging
import uuid
from typing import Dict, List, Optional

from bugout.data import (
    BugoutJournalEntries,
    BugoutJournalEntry,
    BugoutJournalEntryContent,
    BugoutSearchResults,
)
from bugout.exceptions import BugoutResponseException
from bugout.journal import TagsAction
from fastapi import Body, FastAPI, HTTPException, Path, Query, Request
from web3login.middlewares.fastapi import AuthorizationCheckMiddleware

from .. import actions, data
from ..reporter import humbug_reporter
from ..settings import (
    BUGOUT_APPLICATION_ID_HEADER,
    DOCS_TARGET_PATH,
    MOONSTREAM_APPLICATION_ID,
)
from ..settings import bugout_client as bc
from ..version import VERSION

logger = logging.getLogger(__name__)

tags_metadata = [
    {"name": "main", "description": "Main entity endpoints."},
    {"name": "bulk", "description": "Bulk entity operations."},
]

whitelist_paths: Dict[str, str] = {}
whitelist_paths.update(
    {
        "/entity/docs": "GET",
        "/entity/openapi.json": "GET",
    }
)

app = FastAPI(
    title=f"Entity HTTP API",
    description="Entity API endpoints.",
    version=VERSION,
    openapi_tags=tags_metadata,
    openapi_url="/openapi.json",
    docs_url=None,
    redoc_url=f"/{DOCS_TARGET_PATH}",
)

app.add_middleware(
    AuthorizationCheckMiddleware,
    whitelist=whitelist_paths,
    application=MOONSTREAM_APPLICATION_ID,
    auth_types=["bearer", "web3"],
)


@app.post("/collections", tags=["main"], response_model=data.EntityCollectionResponse)
async def add_entity_collection_handler(
    request: Request,
    create_request: data.CreateEntityCollectionAPIRequest = Body(...),
) -> data.EntityCollectionResponse:
    token = request.state.token
    auth_type = request.state.auth_type

    try:
        response = bc.create_journal(
            token=token,
            name=create_request.name,
            auth_type=auth_type,
            headers={BUGOUT_APPLICATION_ID_HEADER: MOONSTREAM_APPLICATION_ID},
        )
    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return data.EntityCollectionResponse(name=response.name, collection_id=response.id)


@app.get("/collections", tags=["main"], response_model=data.EntityCollectionsResponse)
async def list_entity_collections_handler(
    request: Request,
) -> data.EntityCollectionsResponse:
    token = request.state.token
    auth_type = request.state.auth_type

    try:
        response = bc.list_journals(
            token=token,
            auth_type=auth_type,
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


@app.delete(
    "/collections/{collection_id}",
    tags=["main"],
    response_model=data.EntityCollectionResponse,
)
async def delete_entity_collection_handler(
    request: Request,
    collection_id: uuid.UUID = Path(...),
) -> data.EntityCollectionResponse:
    token = request.state.token
    auth_type = request.state.auth_type

    try:
        response = bc.delete_journal(
            token=token,
            journal_id=collection_id,
            auth_type=auth_type,
            headers={BUGOUT_APPLICATION_ID_HEADER: MOONSTREAM_APPLICATION_ID},
        )
    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return data.EntityCollectionResponse(name=response.name, collection_id=response.id)


@app.post(
    "/collections/{collection_id}/entities",
    tags=["main"],
    response_model=data.EntityResponse,
)
async def add_entity_handler(
    request: Request,
    collection_id: uuid.UUID = Path(...),
    create_request: data.Entity = Body(...),
) -> data.EntityResponse:
    token = request.state.token
    auth_type = request.state.auth_type

    unknown_blockchain_address = ""
    try:
        (
            title,
            tags,
            content,
            unknown_blockchain_address,
        ) = actions.parse_entity_to_entry(create_entity=create_request)

        response: BugoutJournalEntry = bc.create_entry(
            token=token,
            journal_id=collection_id,
            title=title,
            content=json.dumps(content),
            tags=tags,
            context_type="entity",
            auth_type=auth_type,
            headers={BUGOUT_APPLICATION_ID_HEADER: MOONSTREAM_APPLICATION_ID},
        )

        entity_response = actions.parse_entry_to_entity(
            entry=response, collection_id=collection_id
        )

    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except actions.UnparsableJournalEntry:
        raise HTTPException(status_code=500, detail="Unable to form entity")
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    if unknown_blockchain_address != "":
        humbug_reporter.custom_report(
            title="Unknown type of blockchain address",
            content=f"Added entity with unknown blockchain addresses "
            f"`{unknown_blockchain_address}` to collection `{collection_id}` entity `{response.id}`",
            tags=[
                f"collection_id:{collection_id}",
                f"unknown_blockchain_address:{unknown_blockchain_address}",
            ],
        )

    return entity_response


@app.post(
    "/collections/{collection_id}/bulk",
    tags=["main", "bulk"],
    response_model=data.EntitiesResponse,
)
async def add_entity_bulk_handler(
    request: Request,
    collection_id: uuid.UUID = Path(...),
    create_request: List[data.Entity] = Body(...),
) -> data.EntitiesResponse:
    token = request.state.token
    auth_type = request.state.auth_type

    unknown_blockchain_address = ""
    try:
        create_entries = []
        for entity in create_request:
            (
                title,
                tags,
                content,
                unknown_blockchain_address,
            ) = actions.parse_entity_to_entry(create_entity=entity)
            create_entries.append(
                {
                    "title": title,
                    "tags": tags,
                    "content": json.dumps(content),
                    "context_type": "entity",
                }
            )

        response: BugoutJournalEntries = bc.create_entries_pack(
            token=token,
            journal_id=collection_id,
            entries=create_entries,
            auth_type=auth_type,
            headers={BUGOUT_APPLICATION_ID_HEADER: MOONSTREAM_APPLICATION_ID},
        )

        entities_response = data.EntitiesResponse(entities=[])
        for entry in response.entries:
            entity_response = actions.parse_entry_to_entity(
                entry=entry, collection_id=collection_id
            )
            entities_response.entities.append(entity_response)

    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except actions.UnparsableJournalEntry:
        raise HTTPException(status_code=500, detail="Unable to form entity")
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    if unknown_blockchain_address != "":
        humbug_reporter.custom_report(
            title="Unknown type of blockchain address - pack",
            content=f"Added pack of entities with unknown blockchain addresses to collection `{collection_id}`",
            tags=[
                f"collection_id:{collection_id}",
                f"unknown_blockchain_address:pack",
            ],
        )

    return entities_response


@app.get(
    "/collections/{collection_id}/entities/{entity_id}",
    tags=["main"],
    response_model=data.EntityResponse,
)
async def get_entity_handler(
    request: Request,
    collection_id: uuid.UUID = Path(...),
    entity_id: uuid.UUID = Path(...),
) -> data.EntityResponse:
    """
    Get entity by id
    """
    token = request.state.token
    auth_type = request.state.auth_type

    try:
        response: BugoutJournalEntry = bc.get_entry(
            token=token,
            journal_id=collection_id,
            entry_id=entity_id,
            auth_type=auth_type,
            headers={BUGOUT_APPLICATION_ID_HEADER: MOONSTREAM_APPLICATION_ID},
        )

        entity_response = actions.parse_entry_to_entity(
            entry=response, collection_id=collection_id
        )

    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except actions.UnparsableJournalEntry:
        raise HTTPException(status_code=500, detail="Unable to form entity")
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return entity_response


@app.put(
    "/collections/{collection_id}/entities/{entity_id}",
    tags=["main"],
    response_model=data.EntityResponse,
)
async def update_entity_handler(
    request: Request,
    collection_id: uuid.UUID = Path(...),
    entity_id: uuid.UUID = Path(...),
    update_request: data.Entity = Body(...),
) -> data.EntityResponse:
    token = request.state.token
    auth_type = request.state.auth_type

    try:
        title, tags, content, _ = actions.parse_entity_to_entry(
            create_entity=update_request
        )
        response: BugoutJournalEntryContent = bc.update_entry_content(
            token=token,
            journal_id=collection_id,
            entry_id=entity_id,
            title=title,
            content=json.dumps(content),
            tags=tags,
            tags_action=TagsAction.replace,
            auth_type=auth_type,
            headers={BUGOUT_APPLICATION_ID_HEADER: MOONSTREAM_APPLICATION_ID},
        )

        entity_response = actions.parse_entry_to_entity(
            entry=response, collection_id=collection_id, entity_id=entity_id
        )

    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except actions.UnparsableJournalEntry:
        raise HTTPException(status_code=500, detail="Unable to form entity")
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return entity_response


@app.get(
    "/collections/{collection_id}/entities",
    tags=["main"],
    response_model=data.EntitiesResponse,
)
async def get_entities_handler(
    request: Request,
    collection_id: uuid.UUID = Path(...),
) -> data.EntitiesResponse:
    token = request.state.token
    auth_type = request.state.auth_type

    try:
        response = bc.get_entries(
            token=token,
            journal_id=collection_id,
            auth_type=auth_type,
            headers={BUGOUT_APPLICATION_ID_HEADER: MOONSTREAM_APPLICATION_ID},
        )

        entities_response = data.EntitiesResponse(entities=[])
        for entry in response.entries:
            entity_response = actions.parse_entry_to_entity(
                entry=entry, collection_id=collection_id
            )
            entities_response.entities.append(entity_response)

    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except actions.UnparsableJournalEntry:
        raise HTTPException(status_code=500, detail="Unable to form entity")
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return entities_response


@app.delete(
    "/collections/{collection_id}/entities/{entity_id}",
    tags=["main"],
    response_model=data.EntityResponse,
)
async def delete_entity_handler(
    request: Request,
    collection_id: uuid.UUID = Path(...),
    entity_id: uuid.UUID = Path(...),
) -> data.EntityResponse:
    token = request.state.token
    auth_type = request.state.auth_type

    try:
        response: BugoutJournalEntry = bc.delete_entry(
            token=token,
            journal_id=collection_id,
            entry_id=entity_id,
            auth_type=auth_type,
            headers={BUGOUT_APPLICATION_ID_HEADER: MOONSTREAM_APPLICATION_ID},
        )
    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return data.EntityResponse(entity_id=response.id, collection_id=collection_id)


@app.get(
    "/collections/{collection_id}/permissions",
    tags=["main"],
    response_model=data.EntityCollectionPermissionsResponse,
)
async def get_entity_collection_permissions_handler(
    request: Request,
    collection_id: uuid.UUID = Path(...),
) -> data.EntityCollectionPermissionsResponse:
    token = request.state.token
    auth_type = request.state.auth_type

    try:
        response = bc.get_journal_permissions(
            token=token,
            journal_id=collection_id,
            auth_type=auth_type,
            headers={BUGOUT_APPLICATION_ID_HEADER: MOONSTREAM_APPLICATION_ID},
        )
    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return data.EntityCollectionPermissionsResponse(
        collection_id=response.journal_id,
        permissions=[
            data.EntityCollectionPermissions(
                holder_type=permission.holder_type,
                holder_id=permission.holder_id,
                permissions=[
                    actions.parse_permission_naming(permission=p, to_entity=True)
                    for p in permission.permissions
                ],
            )
            for permission in response.permissions
        ],
    )


@app.put(
    "/collections/{collection_id}/permissions",
    tags=["main"],
    response_model=data.EntityCollectionPermissionsResponse,
)
async def update_entity_collection_permissions_handler(
    request: Request,
    collection_id: uuid.UUID = Path(...),
    update_request: data.EntityCollectionPermissions = Body(...),
) -> data.EntityCollectionPermissionsResponse:
    token = request.state.token
    auth_type = request.state.auth_type

    try:
        response = bc.update_journal_scopes(
            token=token,
            journal_id=collection_id,
            holder_type=update_request.holder_type,
            holder_id=update_request.holder_id,
            permission_list=[
                actions.parse_permission_naming(permission=p, to_entity=False)
                for p in update_request.permissions
            ],
            auth_type=auth_type,
            headers={BUGOUT_APPLICATION_ID_HEADER: MOONSTREAM_APPLICATION_ID},
        )

        new_entity_collection_permissions = actions.parse_scope_specs_to_permissions(
            collection_id=collection_id,
            holder_type=update_request.holder_type,
            holder_id=update_request.holder_id,
            journal_scopes=response,
        )
    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return new_entity_collection_permissions


@app.delete(
    "/collections/{collection_id}/permissions",
    tags=["main"],
    response_model=data.EntityCollectionPermissionsResponse,
)
async def delete_entity_collection_permissions_handler(
    request: Request,
    collection_id: uuid.UUID = Path(...),
    delete_request: data.EntityCollectionPermissions = Body(...),
) -> data.EntityCollectionPermissionsResponse:
    token = request.state.token
    auth_type = request.state.auth_type

    try:
        response = bc.delete_journal_scopes(
            token=token,
            journal_id=collection_id,
            holder_type=delete_request.holder_type,
            holder_id=delete_request.holder_id,
            permission_list=[
                actions.parse_permission_naming(permission=p, to_entity=False)
                for p in delete_request.permissions
            ],
            auth_type=auth_type,
            headers={BUGOUT_APPLICATION_ID_HEADER: MOONSTREAM_APPLICATION_ID},
        )

        removed_entity_collection_permissions = (
            actions.parse_scope_specs_to_permissions(
                collection_id=collection_id,
                holder_type=delete_request.holder_type,
                holder_id=delete_request.holder_id,
                journal_scopes=response,
            )
        )
    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return removed_entity_collection_permissions


@app.get(
    "/collections/{collection_id}/search",
    tags=["main"],
    response_model=data.EntitySearchResponse,
)
async def search_entity_handler(
    request: Request,
    collection_id: uuid.UUID = Path(...),
    required_field: List[str] = Query(default=[]),
    secondary_field: List[str] = Query(default=[]),
    filters: Optional[List[str]] = Query(None),
    limit: int = Query(10),
    offset: int = Query(0),
    content: bool = Query(True),
) -> data.EntitySearchResponse:
    token = request.state.token
    auth_type = request.state.auth_type

    q = actions.to_journal_search_format(
        required_field=required_field,
        secondary_field=secondary_field,
    )

    try:
        response: BugoutSearchResults = bc.search(
            token=token,
            journal_id=collection_id,
            query=q,
            filters=filters,
            limit=limit,
            offset=offset,
            content=content,
            auth_type=auth_type,
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
                collection_id=collection_id,
            )
            entities_response.entities.append(entity_response)

    except BugoutResponseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except actions.UnparsableJournalEntry:
        raise HTTPException(status_code=500, detail="Unable to form entity")
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500)

    return entities_response
