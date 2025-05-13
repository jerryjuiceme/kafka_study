import logging
import time
from typing import Callable, Awaitable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from src.database import async_engine, async_session_factory


log = logging.getLogger(__name__)


ALLOW_ORIGINS = [
    "http://localhost",
    "http://localhost:8000",
]


type CallNext = Callable[[Request], Awaitable[Response]]


async def add_process_time_to_requests(
    request: Request,
    call_next: CallNext,
) -> Response:
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.5f}"
    return response


async def db_session_middleware(
    request: Request,
    call_next: CallNext,
) -> Response:
    try:
        session = async_session_factory()
        request.state.db = session
        response = await call_next(request)
    except Exception as e:
        raise e from None
    finally:
        await session.close()  # Вариант 1
        await request.state.db.close()  # Вариант 2
    return response


class ProcessTimeHeaderMiddleware(BaseHTTPMiddleware):
    def __init__(self, *args, process_time_header_name: str, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.header_name = process_time_header_name

    async def dispatch(
        self,
        request: Request,
        call_next: CallNext,
    ) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers[self.header_name] = f"{process_time:.5f}"
        return response


def register_middlewares(app: FastAPI) -> None:
    @app.middleware("http")
    async def log_new_requests(
        request: Request,
        call_next: CallNext,
    ) -> Response:
        log.info(
            "Request %s to %s",
            request.method,
            # request.url,
            request.url.path,
        )
        return await call_next(request)

    # app.middleware("http")(add_process_time_to_requests)
    app.middleware("http")(db_session_middleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOW_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        ProcessTimeHeaderMiddleware,
        process_time_header_name="X-Process-Time",
    )
