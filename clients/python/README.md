# Moonstream Entity Python Client

In order to use this client, you will need a Moonstream access token. You can generate one at https://moonstream.to/account/tokens.

The client library reads this token from the `MOONSTREAM_ACCESS_TOKEN` environment variable. To set it:

```bash
export MOONSTREAM_ACCESS_TOKEN="<your_access_token>"
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

Create entity bulk from csv:

Input file `addresses.csv` contains list of addresses:

```csv
address,name
0xe1991fFb1f2271Bc645293cCDf4e38a3f1b7a13c,Address 1
0x37309157eC7863b04c66B6fB2bf7b21EE8B03bA1,Address 2
```

```bash
entity --token "$MOONSTREAM_ACCESS_TOKEN" entities bulk --blockchain ethereum --collection_id "$ENTITY_COLLECTION_ID" --input addresses.csv --required_field '{"owner": "me"}' --secondary_field '{"description": "My bot address"}'
```

List entities in collection:

```bash
entity --token "$MOONSTREAM_ACCESS_TOKEN" entities list --collection_id "$ENTITY_COLLECTION_ID"
```

Delete entity:

```bash
export ENTITY_ID="<your_entity_id>"

entity --token "$MOONSTREAM_ACCESS_TOKEN" entities delete --collection_id "$ENTITY_COLLECTION_ID" --entity_id "$ENTITY_ID"
```
