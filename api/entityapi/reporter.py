import uuid

from humbug.consent import HumbugConsent
from humbug.report import HumbugReporter

from .settings import ENTITY_HUMBUG_REPORTS_BUGOUT_TOKEN
from .version import VERSION

session_id = str(uuid.uuid4())
client_id = "entity-backend"

humbug_consent = HumbugConsent(True)
humbug_reporter = HumbugReporter(
    name="entity",
    consent=HumbugConsent(True),
    client_id=client_id,
    session_id=session_id,
    bugout_token=ENTITY_HUMBUG_REPORTS_BUGOUT_TOKEN,
    tags=[],
)

humbug_version_tag = f"version:{VERSION}"
humbug_tags = [humbug_version_tag]


class ExceptionWithReporting(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        humbug_reporter.error_report(self, tags=humbug_tags, publish=True)
