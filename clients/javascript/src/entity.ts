export interface Collection {
  collectionId?: string;
  name: string;
}

type EntityFieldValue = string | number | boolean | EntityFieldValue[];

type EntityField = { [key: string]: EntityFieldValue };

export interface Entity {
  address: string;
  blockchain: string;
  name: string;
  requiredFields: EntityField[];
  content: EntityField;
}

export interface EntityResponse {
  entity_id: string;
  collection_id: string;
  address: string;
  blockchain: string;
  name: string;
  required_fields: EntityField[];
  secondary_fields: EntityField;
}

export function createEntityRequest(entity: Entity): any {
  let requestData = {
    address: entity.address,
    blockchain: entity.blockchain,
    name: entity.name,
    required_fields: entity.requiredFields,
    ...entity.content,
  };
  return requestData;
}

export function parseEntityResponse(responseData: EntityResponse): Entity {
  let entity: Entity = {
    address: responseData.address,
    blockchain: responseData.blockchain,
    name: responseData.name,
    requiredFields: responseData.required_fields,
    content: responseData.secondary_fields,
  };
  return entity;
}
