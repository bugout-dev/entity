from distutils import util
from typing import Any, Collection, Dict, List, Optional, Tuple, cast

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


async def parse_tags_to_entity_fields(
    tags: List[str],
) -> Tuple[List[str], Optional[bool], List[str]]:
    support_ercs = []
    proxy: Optional[bool] = None
    deployed_contracts = []

    for tag in tags:
        if tag.startswith("support_erc:"):
            support_ercs.append(tag[len("support_erc:") :])
        elif tag.startswith("proxy:"):
            proxy = bool(util.strtobool(tag[len("proxy:")]))
        elif tag.startswith("deployed_contract:"):
            deployed_contracts.append(tag[len("deployed_contract:") :])

    return support_ercs, proxy, deployed_contracts
