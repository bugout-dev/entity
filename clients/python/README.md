## Moonstream Entity Python Client and CLI

In order to use this client, you will need a Moonstream access token. You can generate one at https://moonstream.to/account/tokens.

Detailed documentation you can find at https://docs.moonstream.to/engine/entity

The client library reads this token from the `MOONSTREAM_ACCESS_TOKEN` environment variable. To set it:

```bash
export MOONSTREAM_ACCESS_TOKEN="<your_access_token>"
```

Install package from PyPI:

```bash
pip install moonstream-entity
```

Import and initialize client in your code:

```python
import os

from entity.client import Entity

MOONSTREAM_ACCESS_TOKEN = os.environ.get("MOONSTREAM_ACCESS_TOKEN")

ec = Entity()
response = ec.list_collections(
    token=MOONSTREAM_ACCESS_TOKEN,
    timeout=10,
)

print(response.json())
```

### Work with collections via CLI

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
export MOONSTREAM_ENTITY_COLLECTION_ID="<your_collection_id>"

entity --token "$MOONSTREAM_ACCESS_TOKEN" collections delete --collection_id "$MOONSTREAM_ENTITY_COLLECTION_ID"
```

### Work with entities via CLI

```bash
export MOONSTREAM_ENTITY_COLLECTION_ID="<your_collection_id>"
```

Create entity:

```bash
entity --token "$MOONSTREAM_ACCESS_TOKEN" entities create --collection_id "$MOONSTREAM_ENTITY_COLLECTION_ID" --address "0x000000000000000000000000000000000000dEaD" --blockchain ethereum --name "Dead address" --required_field '{"dead": true}' --required_field '{"owner": "unknown"}' --secondary_field '{"description": "Dangerous address for tokens burning mechanism."}'
```

Create entity bulk from csv:

Input file `addresses.csv` contains list of addresses:

```csv
address,name
0xe1991fFb1f2271Bc645293cCDf4e38a3f1b7a13c,Address 1
0x37309157eC7863b04c66B6fB2bf7b21EE8B03bA1,Address 2
```

```bash
entity --token "$MOONSTREAM_ACCESS_TOKEN" entities bulk --blockchain ethereum --collection_id "$MOONSTREAM_ENTITY_COLLECTION_ID" --input addresses.csv --required_field '{"owner": "me"}' --secondary_field '{"description": "My bot address"}'
```

List entities in collection:

```bash
entity --token "$MOONSTREAM_ACCESS_TOKEN" entities list --collection_id "$MOONSTREAM_ENTITY_COLLECTION_ID"
```

Delete entity:

```bash
export MOONSTREAM_ENTITY_ID="<your_entity_id>"

entity --token "$MOONSTREAM_ACCESS_TOKEN" entities delete --collection_id "$MOONSTREAM_ENTITY_COLLECTION_ID" --entity_id "$MOONSTREAM_ENTITY_ID"
```
