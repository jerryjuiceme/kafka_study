from functools import partial
import logging

from litestar import Litestar, get

from src.broker.utils import start_consumers, stop_consumers
from src.config import settings
from src.logging_conf import configure_logging

configure_logging(level=settings.logging.log_level)

logger = logging.getLogger(__name__)


@get("/")
async def healthcheck() -> str:
    return "OK"


app = Litestar(
    on_startup=[partial(start_consumers)],
    on_shutdown=[partial(stop_consumers)],
    route_handlers=[healthcheck],
)
