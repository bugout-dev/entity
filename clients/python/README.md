# client

Generate Moonstream access token at https://moonstream.to/account/tokens and add to environment variable:

```bash
export MOONSTREAM_ACCESS_TOKEN="<your_generate_moonstream_access_token_id>"
```

## Collections

Create collection:

```bash
entity --token "$MOONSTREAM_ACCESS_TOKEN" collections create --name "My Ethereum addresses"
```

List collections:

```bash
entity --token "$MOONSTREAM_ACCESS_TOKEN" collections list
```

Delete collection:

```bash
export ENTITY_COLLECTION_ID="<your_collection_id>"

entity --token "$MOONSTREAM_ACCESS_TOKEN" collections delete --collection_id "$ENTITY_COLLECTION_ID"
```

## Entities

```bash
export ENTITY_COLLECTION_ID="<your_collection_id>"
```

Create entity:

```bash
entity --token "$MOONSTREAM_ACCESS_TOKEN" entities create --collection_id "$ENTITY_COLLECTION_ID" --address "0x000000000000000000000000000000000000dEaD" --blockchain ethereum --name "Dead address" --required_field '{"dead": true}' --required_field '{"owner": "unknown"}' --secondary_field '{"description": "Dangerous address for tokens burning mechanism."}'
```

Delete entity:

```bash
export ENTITY_ID="<your_entity_id>"

entity --token "$MOONSTREAM_ACCESS_TOKEN" entities delete --collection_id "$ENTITY_COLLECTION_ID" --entity_id "$ENTITY_ID"
```
