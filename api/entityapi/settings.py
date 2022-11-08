import os

from bugout.app import Bugout

# Origin
RAW_ORIGINS = os.environ.get("ENTITY_CORS_ALLOWED_ORIGINS")
if RAW_ORIGINS is None:
    raise ValueError(
        "ENTITY_CORS_ALLOWED_ORIGINS environment variable must be set (comma-separated list of CORS allowed origins)"
    )
ORIGINS = RAW_ORIGINS.split(",")

# Bugout
BUGOUT_BROOD_URL = os.environ.get("BUGOUT_BROOD_URL", "https://auth.bugout.dev")
BUGOUT_SPIRE_URL = os.environ.get("BUGOUT_SPIRE_URL", "https://spire.bugout.dev")

bugout_client = Bugout(brood_api_url=BUGOUT_BROOD_URL, spire_api_url=BUGOUT_SPIRE_URL)

# Web3 signature
BUGOUT_APPLICATION_ID_HEADER_RAW = os.environ.get("BUGOUT_APPLICATION_ID_HEADER")
if BUGOUT_APPLICATION_ID_HEADER_RAW is not None:
    BUGOUT_APPLICATION_ID_HEADER = BUGOUT_APPLICATION_ID_HEADER_RAW
else:
    raise ValueError("BUGOUT_APPLICATION_ID_HEADER environment variable must be set")

MOONSTREAM_APPLICATION_ID = os.environ.get("MOONSTREAM_APPLICATION_ID", "")
if MOONSTREAM_APPLICATION_ID == "":
    raise ValueError("MOONSTREAM_APPLICATION_ID environment variable must be set")
