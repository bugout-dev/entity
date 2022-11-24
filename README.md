# entity

Entity API is used to store any Ethereum address (including smart contract addresses and even addresses that may not have been used) and identifying information/notes.

It supports different use cases:

-   User web3 addresses
-   Maintaining a list of deployed smart contracts (by address)
-   Maintaining a list of smart contract deployers
-   Blacklisting or whitelisting accounts by Discord id, Twitter id, email, etc.
-   Other..

For each entity there are 3 permanently required fields:

-   name
-   address
-   blockchain

Depending on the use case, you can specify additional fields that will be required for your entities in certain collection. Then, you will be able to search across these fields with high precision compared to other fields.

Detailed API documentation you can find at https://docs.moonstream.to/entity/entity-api/

## Different use cases and schemes

### Smartcontract

Required keys: `name`, `address`, `blockchain`, `contract_deployer`, `support_erc`, `proxy`. Other fields could be added as additional.

name: `Terminus`

required fields:

```json
{
	"blockchain": "polygon",
	"address": "0x062BEc5e84289Da2CD6147E0e4DA402B33B8f796",
	"contract_deployer": "0xEba757cEac281D9de85b768Ef4B9E1992C41EA7F",
	"support_erc": [1155, 721],
	"proxy": true
}
```

additional fields:

```json
{
	"description": "Terminus Moonstream.to smartcontract.",
	"discord": "https://discord.com/invite/K56VNUQGvA"
}
```

## Smartcontract deployer

Required keys: `address`, `name`, `blockchain`, `deployed_contract`. Other fields could be added as additional.

title: `Moonstream dropper contract deployer`

required fields:

```json
{
	"blockchain": "polygon",
	"address": "0xEba757cEac281D9de85b768Ef4B9E1992C41EA7F",
	"deployed_contract": "0x7bbf900Ded826D5A16a27dF028018673E521B35d",
	"deployed_contract": "0xEba757cEac281D9de85b768Ef4B9E1992C41EA7F"
}
```

additional fields:

```json
{
	"description": "Moonstream.to deployer.",
	"discord": "https://discord.com/invite/K56VNUQGvA"
}
```
