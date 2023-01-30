"""
Parsing extra attrs: https://github.com/pydantic/pydantic/issues/2285#issuecomment-770100339
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union

from bugout.data import HolderType
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


class VersionResponse(BaseModel):
    """
    Schema for version response
    """

    version: str


class NowResponse(BaseModel):
    """
    Schema for responses on /now endpoint
    """

    epoch_time: float


class CreateEntityCollectionAPIRequest(BaseModel):
    name: str


class EntityCollectionResponse(BaseModel):
    collection_id: uuid.UUID
    name: str


class EntityCollectionsResponse(BaseModel):
    collections: List[EntityCollectionResponse] = Field(default_factory=list)


class EntityCollectionPermissionResponse(BaseModel):
    holder_type: HolderType
    holder_id: uuid.UUID
    permissions: List[str] = Field(default_factory=list)


class EntityCollectionPermissionsResponse(BaseModel):
    collection_id: uuid.UUID
    permissions: List[EntityCollectionPermissionResponse] = Field(default_factory=list)


class Entity(BaseModel, extra=Extra.allow):
    address: str
    blockchain: str
    name: str

    required_fields: List[Dict[str, Union[str, bool, int, list]]] = Field(
        default_factory=list
    )

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
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class EntitiesResponse(BaseModel):
    entities: List[EntityResponse] = Field(default_factory=list)


class EntityFields(BaseModel):
    required_fields: List[Dict[str, Union[str, bool, int, list]]] = Field(
        default_factory=list
    )
    secondary_fields: List[Dict[str, Union[str, bool, int, list]]] = Field(
        default_factory=list
    )


class EntitySearchResponse(BaseModel):
    total_results: int
    offset: int
    next_offset: Optional[int] = None
    max_score: float
    entities: List[EntityResponse] = Field(default_factory=list)
