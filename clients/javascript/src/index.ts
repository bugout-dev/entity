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

  async createEntity(collectionId: string, entity: Entity): Promise<Entity> {
    const response = await fetch(
      `${this.apiUrl}/collections/${collectionId}/entities`,
      {
        method: "POST",
        headers: this.standardHeaders(),
        body: JSON.stringify(createEntityRequest(entity)),
      }
    );

    const createdEntityRaw = await response.json();
    return parseEntityResponse(createdEntityRaw);
  }

  async getEntity(collectionId: string, entityId: string): Promise<Entity> {
    const response = await fetch(
      `${this.apiUrl}/collections/${collectionId}/entities/${entityId}`,
      { method: "GET", headers: this.standardHeaders() }
    );
    const entitiesRaw = await response.json();
    return entitiesRaw.map((raw: EntityResponse) => parseEntityResponse(raw));
  }
}
