import json
import logging
import uuid
from typing import Any, Collection, Dict, List, Optional, Tuple, Union, cast

from bugout.data import (
    BugoutJournalEntry,
    BugoutJournalEntryContent,
    BugoutJournalScopeSpecs,
    HolderType,
)
from web3 import Web3

from . import data

logger = logging.getLogger(__name__)


def to_json_types(value):
    """
    Validate types from source to json types.
    """
    if isinstance(value, (str, int, tuple, list, dict)):
        return value
    elif isinstance(value, set):
        return list(value)
    else:
        return str(value)


def parse_entity_to_entry(
    create_entity: data.Entity,
) -> Tuple[str, List[str], Dict[str, Any]]:
    """
    Parse Entity create request structure to Bugout journal scheme.
    """
    title = f"{create_entity.name}"
    tags: List[str] = []
    content: Dict[str, Any] = {}

    for field, vals in create_entity._iter():
        if field == "address":
            try:
                address = Web3.toChecksumAddress(cast(str, vals))
            except Exception:
                logger.info(f"Unknown type of web3 address {vals}")
                address = vals
            title = f"{address} - {title}"
            tags.append(f"{field}:{address}")

        elif field == "blockchain":
            tags.append(f"{field}:{vals}")

        elif field == "required_fields":
            required_fields = []
            for val in vals:
                for f, v in val.items():
                    if isinstance(v, list):
                        for vl in v:
                            if len(f) >= 128 and len(vl) >= 128:
                                logger.warn(f"Too long key:value {f}:{vl}")
                                continue
                            required_fields.append(f"{str(f)}:{str(vl)}")
                    else:
                        if len(f) >= 128 and len(vl) >= 128:
                            logger.warn(f"Too long key:value {f}:{vl}")
                            continue
                        required_fields.append(f"{f}:{v}")

            tags.extend(required_fields)

        elif field == "extra":
            for k, v in vals.items():
                content[k] = v

    return title, tags, content


def parse_entry_to_entity(
    entry: Union[BugoutJournalEntry, BugoutJournalEntryContent],
    collection_id: uuid.UUID,
    entity_id: Optional[uuid.UUID] = None,
) -> data.EntityResponse:
    """
    Convert Bugout entry to entity response.
    """
    if entity_id is None:
        if type(entry) == BugoutJournalEntry:
            entity_id = entry.id
        else:
            raise Exception("Unable to parse entity_id")
    if entry.title is None:
        raise Exception(f"Unable to parse entry title")
    name = " - ".join(entry.title.split(" - ")[1:])

    address: Optional[str] = None
    blockchain: Optional[str] = None
    required_fields: List[Dict[str, Any]] = []

    for tag in entry.tags:
        if tag.startswith("address:"):
            address = tag[len("address:") :]
            continue
        elif tag.startswith("blockchain:"):
            blockchain = tag[len("blockchain:") :]
            continue
        field_and_val = tag.split(":")
        required_fields.append(
            {"".join(field_and_val[:1]): ":".join(field_and_val[1:])}
        )

    # limitation of BugoutJournalEntryContent
    created_at = entry.created_at if "created_at" in entry.__fields__ else None  # type: ignore
    updated_at = entry.updated_at if "updated_at" in entry.__fields__ else None  # type: ignore

    return data.EntityResponse(
        collection_id=collection_id,
        entity_id=entity_id,
        address=address,
        blockchain=blockchain,
        name=name,
        required_fields=required_fields,
        secondary_fields=json.loads(entry.content) if entry.content is not None else {},
        created_at=created_at,
        updated_at=updated_at,
    )


def parse_permission_naming(permission: str, to_entity: bool = True) -> str:
    """
    If to_entity is True:
    "journals.entries.read" -> "collections.entities.read"
    Else in opposite way.
    """
    if to_entity:
        return permission.replace("journals", "collections").replace(
            "entries", "entities"
        )

    return permission.replace("collections", "journals").replace("entities", "entries")


def parse_entity_permission_to_journal(permission: str) -> str:
    """
    "collections.entities.read" -> "journals.entries.read"
    """
    return permission.replace("journals", "collections").replace("entries", "entities")


def parse_scope_specs_to_permissions(
    collection_id: uuid.UUID,
    holder_type: HolderType,
    holder_id: uuid.UUID,
    journal_scopes: BugoutJournalScopeSpecs,
) -> data.EntityCollectionPermissionsResponse:
    """
    Convert Bugout journal entry scopes(permissions) to entity
    collection permissions.
    """
    new_permissions = []
    for scope in journal_scopes.scopes:
        new_permissions.append(
            parse_permission_naming(permission=scope.permission, to_entity=True)
        )
        if holder_type != scope.holder_type:
            raise Exception(f"Unable to parse scope holder_type {scope.holder_type}")
        if holder_id != uuid.UUID(scope.holder_id):
            raise Exception(f"Unable to parse scope holder_id {scope.holder_id}")
        if collection_id != scope.journal_id:
            raise Exception(f"Unable to parse scope journal_id {scope.journal_id}")

    return data.EntityCollectionPermissionsResponse(
        collection_id=collection_id,
        permissions=[
            data.EntityCollectionPermissions(
                holder_type=holder_type,
                holder_id=holder_id,
                permissions=new_permissions,
            )
        ],
    )
