import json
from distutils import util
from typing import Any, Collection, Dict, List, Optional, Tuple

from bugout.data import BugoutJournalEntry

from . import data


async def parse_entity_to_entry(
    create_entity: data.CreateEntityRequest,
) -> Tuple[str, List[str], Dict[str, Any]]:
    """
    Parse Entity create request structure to Bugout journal scheme
    """
    title = f"{create_entity.name}"
    tags: List[str] = []
    content: Dict[str, Any] = {}

    for field, val in create_entity._iter():
        if field == "address":
            title = f"{val} - {title}"
            tags.append(f"{field}:{val}")
        elif field == "blockchain":
            tags.append(f"{field}:{val}")
        elif field == "entity_type":
            tags.append(f"{field}:{val.value}")
        elif field == "extra":
            for k, v in val.items():
                content[k] = v

        # Smartcontract type
        elif field == "support_ercs":
            for v in val:
                tags.append(f"support_erc:{''.join([l for l in v if l.isnumeric()])}")
        elif field == "proxy":
            if val is not None:
                tags.append(f"proxy:{val}")

        # Smartcontract deployer type
        elif field == "deployed_contracts":
            for v in val:
                tags.append(f"deployed_contract:{v}")

    return title, tags, content


async def parse_entry_to_entity(entry: BugoutJournalEntry) -> data.EntityResponse:
    """
    Convert Bugout entry to entity response
    """
    if entry.journal_url is None:
        raise Exception(f"Journal id of entry {entry.id} not found")
    collection_id = entry.journal_url.rstrip("/").split("/")[-1]

    address: Optional[str] = None
    blockchain: Optional[str] = None
    entity_type: Optional[str] = None
    support_ercs = []
    proxy: Optional[bool] = None
    deployed_contracts = []

    for tag in entry.tags:
        if tag.startswith("address:"):
            address = tag[len("address:") :]
        elif tag.startswith("blockchain:"):
            blockchain = tag[len("blockchain:") :]
        elif tag.startswith("entity_type:"):
            entity_type = tag[len("entity_type:") :]
        elif tag.startswith("support_erc:"):
            support_ercs.append(tag[len("support_erc:") :])
        elif tag.startswith("proxy:"):
            proxy = bool(util.strtobool(tag[len("proxy:")]))
        elif tag.startswith("deployed_contract:"):
            deployed_contracts.append(tag[len("deployed_contract:") :])

    return data.EntityResponse(
        collection_id=collection_id,
        entity_id=entry.id,
        address=address,
        blockchain=blockchain,
        title=entry.title,
        entity_type=entity_type,
        content=json.loads(entry.content) if entry.content is not None else {},
        support_ercs=support_ercs,
        proxy=proxy,
        deployed_contracts=deployed_contracts,
    )
