import logging

from .config import DEBUG

logger = logging.getLogger("graveboards")

logging.basicConfig(
    level=logging.INFO if DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logging.getLogger("push_response").disabled = True
