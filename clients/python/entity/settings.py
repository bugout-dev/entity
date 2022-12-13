import os

ENTITY_API_URL = os.environ.get("ENTITY_API_URL", "https://api.moonstream.to/entity")

ENTITY_REQUEST_TIMEOUT = 10
ENTITY_REQUEST_TIMEOUT_RAW = os.environ.get("ENTITY_REQUEST_TIMEOUT")
try:
    if ENTITY_REQUEST_TIMEOUT_RAW is not None:
        ENTITY_REQUEST_TIMEOUT = int(ENTITY_REQUEST_TIMEOUT_RAW)
except:
    raise Exception(
        f"Could not parse ENTITY_REQUEST_TIMEOUT environment variable as int: {ENTITY_REQUEST_TIMEOUT_RAW}"
    )
