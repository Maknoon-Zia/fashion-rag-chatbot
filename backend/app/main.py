"""FastAPI application factory."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.errors import register_error_handlers
from app.db import mongo
from app.db.qdrant import close_qdrant
from app.routers import auth, chat, conversations, health

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_settings()  # fail fast with a clear message if .env is incomplete
    try:
        mongo.ensure_indexes()
    except Exception as exc:
        raise RuntimeError(
            "Cannot connect to MongoDB. Check MONGODB_URI, the Atlas user/password and that your "
            f"IP address is allowed in Atlas > Network Access. ({type(exc).__name__})"
        ) from exc
    logger.info("MongoDB connected and indexes ensured")
    yield
    mongo.close_client()
    close_qdrant()


def create_app() -> FastAPI:
    app = FastAPI(title="Fashion Styling RAG Chatbot API", version="1.0.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().cors_origin_list,
        allow_credentials=False,  # bearer tokens, no cookies
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    register_error_handlers(app)
    for r in (health.router, auth.router, conversations.router, chat.router):
        app.include_router(r)
    return app


app = create_app()
