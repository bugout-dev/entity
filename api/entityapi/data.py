"""
Parsing extra attrs: https://github.com/pydantic/pydantic/issues/2285#issuecomment-770100339
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union

from pydantic import BaseModel, Extra, Field, root_validator


class EntityTypes(Enum):
    SMARTCONTRACT = "smartcontract"
    SMARTCONTRACT_DEPLOYER = "smartcontract_deployer"
    PERSON = "person"


class PingResponse(BaseModel):
    """
    Schema for ping response
    """

    status: str


class NowResponse(BaseModel):
    """
    Schema for responses on /now endpoint
    """

    epoch_time: float


class CreateEntityCollectionAPIRequest(BaseModel):
    collection_id: uuid.UUID
    name: str


class EntityCollectionResponse(BaseModel):
    collection_id: uuid.UUID
    name: str


class EntityCollectionsResponse(BaseModel):
    collections: List[EntityCollectionResponse] = Field(default_factory=list)


class Entity(BaseModel, extra=Extra.allow):
    address: str
    blockchain: str
    name: str

    required_fields: Optional[Dict[str, Union[str, bool, int, list]]] = None

    extra: Dict[str, Any]

    @root_validator(pre=True)
    def build_extra(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        all_required_field_names = {
            field.alias for field in cls.__fields__.values() if field.alias != "extra"
        }

        extra: Dict[str, Any] = {}
        for field_name in list(values):
            if field_name not in all_required_field_names:
                extra[field_name] = values.pop(field_name)
        values["extra"] = extra
        return values


class EntityResponse(BaseModel):
    entity_id: uuid.UUID
    collection_id: uuid.UUID
    address: Optional[str] = None
    blockchain: Optional[str] = None
    name: Optional[str] = None

    required_fields: Optional[List[Dict[str, Any]]] = None
    secondary_fields: Optional[Dict[str, Any]] = None


class EntitiesResponse(BaseModel):
    entities: List[EntityResponse] = Field(default_factory=list)
