"""Публичный эндпоинт — авторизация не требуется."""

from datetime import datetime, timezone

from fastapi import APIRouter

from app.schemas import PublicResponse

router = APIRouter(tags=["public"])


@router.get("/public", response_model=PublicResponse, summary="Публичный, без авторизации")
def public_endpoint() -> PublicResponse:
    """Возвращает приветствие. Для этого роута токен не нужен."""
    return PublicResponse(
        ok=True,
        message="Привет, аноним! Этот эндпоинт публичный.",
        server_time=datetime.now(timezone.utc).isoformat(),
    )
