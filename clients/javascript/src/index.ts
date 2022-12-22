import {
  Collection,
  Entity,
  EntityResponse,
  createEntityRequest,
  parseEntityResponse,
} from "./entity";

export class EntityClient {
  accessToken: string;
  apiUrl: string;

  constructor(accessToken: string, apiUrl?: string) {
    this.accessToken = accessToken;
    this.apiUrl = apiUrl
      ? apiUrl.replace(/\/+$/, "")
      : "https://api.moonstream.to/entity";
  }

  authorizationValue(): string {
    return `Bearer ${this.accessToken}`;
  }

  standardHeaders(): { [key: string]: string } {
    return {
      Authorization: this.authorizationValue(),
      "Content-Type": "application/json",
    };
  }

  async createCollection(name: string): Promise<Collection> {
    const response = await fetch(`${this.apiUrl}/collections`, {
      method: "POST",
      headers: this.standardHeaders(),
      body: JSON.stringify({ name }),
    });

    const collectionRaw = await response.json();
    return {
      collectionId: collectionRaw.collection_id,
      name: collectionRaw.name,
    };
  }

  async listCollections(): Promise<Collection[]> {
    const response = await fetch(`${this.apiUrl}/collections`, {
      method: "GET",
      headers: this.standardHeaders(),
    });

    const collectionsRaw = await response.json();
    return collectionsRaw.collections.map((raw: any) => {
      return { collectionId: raw.collection_id, name: raw.name };
    });
  }

  async createEntity(
    collectionId: string,
    entity: Entity
  ): Promise<EntityResponse> {
    const response = await fetch(
      `${this.apiUrl}/collections/${collectionId}/entities`,
      {
        method: "POST",
        headers: this.standardHeaders(),
        body: JSON.stringify(createEntityRequest(entity)),
      }
    );

    const createdEntityResponseData: EntityResponse = await response.json();
    return createdEntityResponseData;
  }

  async getEntity(collectionId: string, entityId: string): Promise<Entity> {
    const response = await fetch(
      `${this.apiUrl}/collections/${collectionId}/entities/${entityId}`,
      { method: "GET", headers: this.standardHeaders() }
    );
    const entitiesRaw = await response.json();
    return entitiesRaw.map((raw: EntityResponse) => parseEntityResponse(raw));
  }

  async deleteEntity(
    collectionId: string,
    entityId: string
  ): Promise<EntityResponse> {
    const response = await fetch(
      `${this.apiUrl}/collections/${collectionId}/entities/${entityId}`,
      { method: "DELETE", headers: this.standardHeaders() }
    );
    const entityResponseData: EntityResponse = await response.json();
    return entityResponseData;
  }

  async updateEntity(
    collectionId: string,
    entityId: string,
    entity: Entity
  ): Promise<EntityResponse> {
    const response = await fetch(
      `${this.apiUrl}/collections/${collectionId}/entities/${entityId}`,
      {
        method: "PUT",
        headers: this.standardHeaders(),
        body: JSON.stringify(createEntityRequest(entity)),
      }
    );

    const updatedEntityResponseData: EntityResponse = await response.json();
    return updatedEntityResponseData;
  }

  async search(
    collectionId: string,
    requiredFields: string[],
    content: string[],
    limit?: number,
    offset?: number
  ): Promise<EntityResponse[]> {
    limit = limit || 10;
    offset = offset || 0;
    if (limit < 0) {
      throw new Error("limit must be non-negative");
    }
    if (offset < 0) {
      throw new Error("offset must be non-negative");
    }
    const requiredFieldsQueries = requiredFields.map(
      (term) => `required_field=${encodeURIComponent(term)}`
    );
    const secondaryFieldsQueries = content.map(
      (term) => `secondary_field=${encodeURIComponent(term)}`
    );
    const queryParams = requiredFieldsQueries
      .concat(secondaryFieldsQueries)
      .join("+");
    const response = await fetch(
      `${this.apiUrl}/collections/${collectionId}/search?q=${queryParams}`,
      {
        method: "GET",
        headers: this.standardHeaders(),
      }
    );

    const searchResultsResponseData: EntityResponse[] = await response.json();
    return searchResultsResponseData;
  }
}
