"""Pydantic-модели, описывающие ответы API."""

from typing import Any

from pydantic import BaseModel


class PublicResponse(BaseModel):
    ok: bool
    message: str
    server_time: str


class TokenResponse(BaseModel):
    ok: bool
    endpoint: str
    header: dict[str, Any] | None = None
    claims: dict[str, Any]
    note: str | None = None


class ErrorResponse(BaseModel):
    detail: str
