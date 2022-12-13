import argparse
import csv
import json
import uuid
from typing import Any, Dict, List

from . import data
from .client import Entity
from .settings import ENTITY_REQUEST_TIMEOUT


def check_dict_format(fields: List[Any]) -> List[Dict[str, Any]]:
    for field in fields:
        if type(field) != dict:
            raise Exception(
                f"Provided field should dict format, incorrect field: {field}"
            )

    return fields


def version_handler(args: argparse.Namespace) -> None:
    ec = Entity()
    response = ec.version()

    print(response.json())


def collections_create_handler(args: argparse.Namespace) -> None:
    ec = Entity()
    response = ec.add_collection(
        token=args.token, name=args.name, auth_type=args.auth_type, timeout=args.timeout
    )

    print(response.json())


def collections_delete_handler(args: argparse.Namespace) -> None:
    ec = Entity()
    response = ec.delete_collection(
        token=args.token,
        collection_id=args.collection_id,
        auth_type=args.auth_type,
        timeout=args.timeout,
    )

    print(response.json())


def collections_list_handler(args: argparse.Namespace) -> None:
    ec = Entity()
    response = ec.list_collections(
        token=args.token,
        auth_type=args.auth_type,
        timeout=args.timeout,
    )

    print(response.json())


def entities_create_handler(args: argparse.Namespace) -> None:
    required_fields = check_dict_format(args.required_field)
    secondary_fields = {
        k: v for d in check_dict_format(args.secondary_field) for k, v in d.items()
    }  # Flat dictionary [{}, {}] -> {}

    ec = Entity()
    response = ec.add_entity(
        token=args.token,
        collection_id=args.collection_id,
        address=args.address,
        blockchain=args.blockchain,
        name=args.name,
        required_fields=required_fields,
        secondary_fields=secondary_fields,
        auth_type=args.auth_type,
        timeout=args.timeout,
    )

    print(response.json())


def entities_create_bulk_handler(args: argparse.Namespace) -> None:
    required_fields = check_dict_format(args.required_field)
    secondary_fields = {
        k: v for d in check_dict_format(args.secondary_field) for k, v in d.items()
    }  # Flat dictionary [{}, {}] -> {}

    entities: List[Dict[str, Any]] = []
    with open(args.input, "r", encoding="utf-8") as ifp:
        csv_reader = csv.reader(ifp, delimiter=",")

        headers = []
        for i, row in enumerate(csv_reader):
            if i == 0:
                headers = row
            else:
                data_row: Dict[str, Any] = {}
                for i, elem in enumerate(row):
                    data_row[headers[i]] = elem
                data_row["blockchain"] = args.blockchain
                data_row["required_fields"] = required_fields
                for k, v in secondary_fields.items():
                    data_row[k] = v

                entities.append(data_row)

    ec = Entity()
    response = ec.add_entities_bulk(
        token=args.token,
        collection_id=args.collection_id,
        entities=entities,
        auth_type=args.auth_type,
        timeout=args.timeout,
    )

    print(response.json())


def entities_list_handler(args: argparse.Namespace) -> None:
    ec = Entity()
    response = ec.list_entities(
        token=args.token,
        collection_id=args.collection_id,
        auth_type=args.auth_type,
        timeout=args.timeout,
    )

    print(response.json())


def entities_delete_handler(args: argparse.Namespace) -> None:
    ec = Entity()
    response = ec.delete_entity(
        token=args.token,
        collection_id=args.collection_id,
        entity_id=args.entity_id,
        auth_type=args.auth_type,
        timeout=args.timeout,
    )

    print(response.json())


def main() -> None:
    parser = argparse.ArgumentParser(description="Moonstream entity CLI")
    parser.set_defaults(func=lambda _: parser.print_help())
    subcommands = parser.add_subparsers(description="Moonstream entity commands")

    parser.add_argument("-t", "--token", type=str, help="Moonstream access token")
    parser.add_argument(
        "--auth_type",
        type=str,
        default=data.AuthType.bearer,
        help=f"Available contracts: {[member.name for member in data.AuthType]}",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=ENTITY_REQUEST_TIMEOUT,
        help=f"Request timeout, default: {ENTITY_REQUEST_TIMEOUT}",
    )

    parser_version = subcommands.add_parser(
        "version", description="Get Entity API server version"
    )
    parser_version.set_defaults(func=version_handler)

    # Collections subcommands
    parser_collections = subcommands.add_parser(
        "collections", description="Collections commands"
    )
    parser_collections.set_defaults(func=lambda _: parser_collections.print_help())
    subcommands_collections = parser_collections.add_subparsers(
        description="Collections subcommands"
    )

    parser_collections_create = subcommands_collections.add_parser(
        "create", description="Create collection for entities"
    )
    parser_collections_create.add_argument(
        "-n",
        "--name",
        type=str,
        required=True,
        help="Name of collection",
    )
    parser_collections_create.set_defaults(func=collections_create_handler)

    parser_collections_list = subcommands_collections.add_parser(
        "list", description="List all collections"
    )
    parser_collections_list.set_defaults(func=collections_list_handler)

    parser_collections_delete = subcommands_collections.add_parser(
        "delete", description="Delete entity collection"
    )
    parser_collections_delete.add_argument(
        "-c",
        "--collection_id",
        type=uuid.UUID,
        required=True,
        help="Id of collection",
    )
    parser_collections_delete.set_defaults(func=collections_delete_handler)

    # Entities subcommands
    parser_entities = subcommands.add_parser(
        "entities", description="Entities commands"
    )
    parser_entities.set_defaults(func=lambda _: parser_entities.print_help())
    subcommands_entities = parser_entities.add_subparsers(
        description="Entities subcommands"
    )

    parser_entities_create = subcommands_entities.add_parser(
        "create", description="Create entity"
    )
    parser_entities_create.add_argument(
        "-c",
        "--collection_id",
        type=uuid.UUID,
        required=True,
        help="Id of collection",
    )
    parser_entities_create.add_argument(
        "-a",
        "--address",
        type=str,
        required=True,
        help="Blockchain address",
    )
    parser_entities_create.add_argument(
        "-b",
        "--blockchain",
        type=str,
        required=True,
        help="Blockchain",
    )
    parser_entities_create.add_argument(
        "-n",
        "--name",
        type=str,
        required=True,
        help="Name of entity",
    )
    parser_entities_create.add_argument(
        "-r",
        "--required_field",
        type=json.loads,
        default=[],
        action="append",
        help="Required fields, could be set multiple times",
    )
    parser_entities_create.add_argument(
        "-s",
        "--secondary_field",
        type=json.loads,
        default=[],
        action="append",
        help="Secondary fields, could be set multiple times",
    )
    parser_entities_create.set_defaults(func=entities_create_handler)

    parser_entities_bulk = subcommands_entities.add_parser(
        "bulk", description="Create pack of entities"
    )
    parser_entities_bulk.add_argument(
        "-b",
        "--blockchain",
        type=str,
        required=True,
        help="Blockchain",
    )
    parser_entities_bulk.add_argument(
        "-c",
        "--collection_id",
        type=uuid.UUID,
        required=True,
        help="Collection id to search for",
    )
    parser_entities_bulk.add_argument(
        "-r",
        "--required_field",
        type=json.loads,
        default=[],
        action="append",
        help="Required fields, could be set multiple times",
    )
    parser_entities_bulk.add_argument(
        "-s",
        "--secondary_field",
        type=json.loads,
        default=[],
        action="append",
        help="Secondary fields, could be set multiple times",
    )
    parser_entities_bulk.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input CSV file path to load data from",
    )
    parser_entities_bulk.set_defaults(func=entities_create_bulk_handler)

    parser_entities_list = subcommands_entities.add_parser(
        "list", description="List all entities in collection"
    )
    parser_entities_list.add_argument(
        "-c",
        "--collection_id",
        type=uuid.UUID,
        required=True,
        help="Collection id to search for",
    )
    parser_entities_list.set_defaults(func=entities_list_handler)

    parser_entities_delete = subcommands_entities.add_parser(
        "delete", description="Delete entity"
    )
    parser_entities_delete.add_argument(
        "-c",
        "--collection_id",
        type=uuid.UUID,
        required=True,
        help="Id of collection",
    )
    parser_entities_delete.add_argument(
        "-e",
        "--entity_id",
        type=uuid.UUID,
        required=True,
        help="Id of entity",
    )
    parser_entities_delete.set_defaults(func=entities_delete_handler)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
