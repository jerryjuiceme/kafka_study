from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.middlewares import register_middlewares
from src.error_handlers import register_errors_handlers
from src.actions.create_superuser import create_superuser
from src.config import settings
from src.api import api_router as main_api_router
from src.database import dispose
from src.healthcheck import router as healthcheck_router
from src.logging_conf import configure_logging
from src.broker import start_consumers, stop_consumers


configure_logging(level="INFO")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await create_superuser()
    # await broker.connect()
    # await stream_app.start()
    await start_consumers()
    yield
    # shutdown
    # await stream_app.stop()
    # await broker.close()
    await stop_consumers()
    await dispose()


app = FastAPI(
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    title=settings.project_name,
    version="0.1.0",
)

app.include_router(main_api_router)
app.include_router(healthcheck_router)

register_errors_handlers(app)
register_middlewares(app)
