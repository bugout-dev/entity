import uuid
from typing import Any, Dict, List, Union, Optional
import requests  # type: ignore

from . import data, exceptions
from .settings import ENTITY_API_URL, ENTITY_REQUEST_TIMEOUT

ENDPOINT_PING = "/ping"
ENDPOINT_VERSION = "/version"
ENDPOINT_NOW = "/now"
ENDPOINT_COLLECTIONS = "/collections"
ENDPOINT_SEARCH = "/search"

ENDPOINTS = [
    ENDPOINT_PING,
    ENDPOINT_VERSION,
    ENDPOINT_NOW,
    ENDPOINT_COLLECTIONS,
    ENDPOINT_SEARCH,
]


def entity_endpoints(url: str) -> Dict[str, str]:
    """
    Creates a dictionary of Entity API endpoints at the given Entity API URL.
    """
    if not (url.startswith("http://") or url.startswith("https://")):
        url = f"http://{url}"

    normalized_url = url.rstrip("/")

    return {endpoint: f"{normalized_url}{endpoint}" for endpoint in ENDPOINTS}


class Entity:
    """
    An Entity client configured to communicate with a given Entity API server.
    """

    def __init__(self, entity_api_url: str = ENTITY_API_URL):
        """
        Initializes a Entity API client.

            Arguments:
            url - Entity API URL. By default this points to the production Entity API at https://api.moonstream.to/entity,
            but you can replace it with the URL of any other Entity API instance.
        """
        endpoints = entity_endpoints(entity_api_url)
        self.api = data.APISpec(url=entity_api_url, endpoints=endpoints)

    def _call(
        self,
        method: data.Method,
        url: str,
        timeout: float = ENTITY_REQUEST_TIMEOUT,
        **kwargs,
    ):
        try:
            response = requests.request(
                method.value, url=url, timeout=timeout, **kwargs
            )
            response.raise_for_status()
        except Exception as e:
            raise exceptions.EntityUnexpectedResponse(str(e))
        return response.json()

    def ping(self) -> data.PingResponse:
        """
        Checks that you have a connection to the Entity API.
        """
        result = self._call(
            method=data.Method.GET, url=self.api.endpoints[ENDPOINT_PING]
        )
        return data.PingResponse(**result)

    def version(self) -> data.VersionResponse:
        """
        Gets the Entity API version information from the server.
        """
        result = self._call(
            method=data.Method.GET, url=self.api.endpoints[ENDPOINT_VERSION]
        )
        return data.VersionResponse(**result)

    def add_collection(
        self,
        token: Union[str, uuid.UUID],
        name: str,
        auth_type: data.AuthType = data.AuthType.bearer,
        timeout: float = ENTITY_REQUEST_TIMEOUT,
    ) -> data.EntityCollectionResponse:
        headers = {
            "Authorization": f"{auth_type.value} {token}",
        }
        payload = {"name": name}
        result = self._call(
            method=data.Method.POST,
            url=f"{self.api.endpoints[ENDPOINT_COLLECTIONS]}",
            headers=headers,
            json=payload,
            timeout=timeout,
        )
        return data.EntityCollectionResponse(**result)

    def list_collections(
        self,
        token: Union[str, uuid.UUID],
        auth_type: data.AuthType = data.AuthType.bearer,
        timeout: float = ENTITY_REQUEST_TIMEOUT,
    ) -> data.EntityCollectionsResponse:
        headers = {
            "Authorization": f"{auth_type.value} {token}",
        }
        result = self._call(
            method=data.Method.GET,
            url=f"{self.api.endpoints[ENDPOINT_COLLECTIONS]}",
            headers=headers,
            timeout=timeout,
        )
        return data.EntityCollectionsResponse(**result)

    def delete_collection(
        self,
        token: Union[str, uuid.UUID],
        collection_id: Union[str, uuid.UUID],
        auth_type: data.AuthType = data.AuthType.bearer,
        timeout: float = ENTITY_REQUEST_TIMEOUT,
    ) -> data.EntityCollectionResponse:
        headers = {
            "Authorization": f"{auth_type.value} {token}",
        }
        result = self._call(
            method=data.Method.DELETE,
            url=f"{self.api.endpoints[ENDPOINT_COLLECTIONS]}/{str(collection_id)}",
            headers=headers,
            timeout=timeout,
        )
        return data.EntityCollectionResponse(**result)

    def add_entity(
        self,
        token: Union[str, uuid.UUID],
        collection_id: Union[str, uuid.UUID],
        address: str,
        blockchain: str,
        name: str,
        required_fields: List[Dict[str, Union[str, bool, int, list]]] = [],
        secondary_fields: Dict[str, Any] = {},
        auth_type: data.AuthType = data.AuthType.bearer,
        timeout: float = ENTITY_REQUEST_TIMEOUT,
    ) -> data.EntityResponse:
        headers = {
            "Authorization": f"{auth_type.value} {token}",
        }
        payload = {
            "address": address,
            "blockchain": blockchain,
            "name": name,
            "required_fields": required_fields,
            **secondary_fields,
        }
        result = self._call(
            method=data.Method.POST,
            url=f"{self.api.endpoints[ENDPOINT_COLLECTIONS]}/{str(collection_id)}/entities",
            headers=headers,
            json=payload,
            timeout=timeout,
        )

        return data.EntityResponse(**result)

    def get_entity(
        self,
        token: Union[str, uuid.UUID],
        collection_id: Union[str, uuid.UUID],
        entity_id: Union[str, uuid.UUID],
        auth_type: data.AuthType = data.AuthType.bearer,
        timeout: float = ENTITY_REQUEST_TIMEOUT,
    ) -> data.EntityResponse:
        headers = {
            "Authorization": f"{auth_type.value} {token}",
        }
        result = self._call(
            method=data.Method.GET,
            url=f"{self.api.endpoints[ENDPOINT_COLLECTIONS]}/{str(collection_id)}/entities/{str(entity_id)}",
            headers=headers,
            timeout=timeout,
        )

        return data.EntityResponse(**result)

    def add_entities_bulk(
        self,
        token: Union[str, uuid.UUID],
        collection_id: Union[str, uuid.UUID],
        entities: List[Dict[str, Any]],
        auth_type: data.AuthType = data.AuthType.bearer,
        timeout: float = ENTITY_REQUEST_TIMEOUT,
    ) -> data.EntitiesResponse:
        headers = {
            "Authorization": f"{auth_type.value} {token}",
        }
        result = self._call(
            method=data.Method.POST,
            url=f"{self.api.endpoints[ENDPOINT_COLLECTIONS]}/{str(collection_id)}/bulk",
            headers=headers,
            json=entities,
            timeout=timeout,
        )
        return data.EntitiesResponse(**result)

    def list_entities(
        self,
        token: Union[str, uuid.UUID],
        collection_id: Union[str, uuid.UUID],
        auth_type: data.AuthType = data.AuthType.bearer,
        timeout: float = ENTITY_REQUEST_TIMEOUT,
    ) -> data.EntitiesResponse:
        headers = {
            "Authorization": f"{auth_type.value} {token}",
        }
        result = self._call(
            method=data.Method.GET,
            url=f"{self.api.endpoints[ENDPOINT_COLLECTIONS]}/{str(collection_id)}/entities",
            headers=headers,
            timeout=timeout,
        )
        return data.EntitiesResponse(**result)

    def update_entity(
        self,
        token: Union[str, uuid.UUID],
        collection_id: Union[str, uuid.UUID],
        entity_id: Union[str, uuid.UUID],
        address: str,
        blockchain: str,
        name: str,
        required_fields: List[Dict[str, Union[str, bool, int, list]]] = [],
        secondary_fields: Dict[str, Any] = {},
        auth_type: data.AuthType = data.AuthType.bearer,
        timeout: float = ENTITY_REQUEST_TIMEOUT,
    ) -> data.EntityResponse:
        headers = {
            "Authorization": f"{auth_type.value} {token}",
        }
        payload = {
            "address": address,
            "blockchain": blockchain,
            "name": name,
            "required_fields": required_fields,
            **secondary_fields,
        }
        result = self._call(
            method=data.Method.PUT,
            url=f"{self.api.endpoints[ENDPOINT_COLLECTIONS]}/{str(collection_id)}/entities/{str(entity_id)}",
            headers=headers,
            json=payload,
            timeout=timeout,
        )

        return data.EntityResponse(**result)

    def delete_entity(
        self,
        token: Union[str, uuid.UUID],
        collection_id: Union[str, uuid.UUID],
        entity_id: Union[str, uuid.UUID],
        auth_type: data.AuthType = data.AuthType.bearer,
        timeout: float = ENTITY_REQUEST_TIMEOUT,
    ) -> data.EntityResponse:
        headers = {
            "Authorization": f"{auth_type.value} {token}",
        }
        result = self._call(
            method=data.Method.DELETE,
            url=f"{self.api.endpoints[ENDPOINT_COLLECTIONS]}/{str(collection_id)}/entities/{str(entity_id)}",
            headers=headers,
            timeout=timeout,
        )

        return data.EntityResponse(**result)

    def search_entities(
        self,
        token: Union[str, uuid.UUID],
        collection_id: Union[str, uuid.UUID],
        required_field: List[str] = [],
        secondary_field: List[str] = [],
        filters: Optional[List[str]] = None,
        limit: int = 10,
        offset: int = 0,
        content: bool = True,
        timeout: float = ENTITY_REQUEST_TIMEOUT,
    ) -> data.EntitySearchResponse:

        headers = {
            "Authorization": f"{data.AuthType.bearer.value} {token}",
        }

        params = {
            "required_field": required_field,
            "secondary_field": secondary_field,
            "limit": limit,
            "offset": offset,
            "content": content,
        }

        if filters:
            params["filters"] = filters

        result = self._call(
            method=data.Method.GET,
            url=f"{self.api.endpoints[ENDPOINT_COLLECTIONS]}/{str(collection_id)}{ENDPOINT_SEARCH}",
            headers=headers,
            timeout=timeout,
            params=params,
        )

        return data.EntitySearchResponse(**result)
