"""Точка входа приложения FastAPI для учебного API."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import APP_NAME, APP_VERSION, LOG_LEVEL
from app.routers import admin, encrypted, none, public, signed

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Намеренно уязвимый API для обучения работе с JWT. "
        "Используется для перехвата трафика в Wireshark и подделки токенов."
    ),
)

# Полностью открытый CORS, чтобы студенты могли обращаться к API любым инструментом.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public.router)
app.include_router(none.router)
app.include_router(admin.router)
app.include_router(signed.router)
app.include_router(encrypted.router)


@app.get("/", tags=["meta"], summary="Баннер сервиса")
def root() -> dict[str, str]:
    """Показывает доступные эндпоинты без авторизации."""
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "endpoints": (
            "GET /public, GET /private/none, GET /private/admin, "
            "GET /private/signed, GET /private/encrypted"
        ),
        "warning": "Только для обучения — не разворачивайте с реальными данными.",
    }
