"""Главное окно учебного клиента на PyQt6."""

import json
from typing import Any, Callable

from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import api
from tokens import (
    build_encrypted_token,
    build_signed_token,
    build_unsigned_token,
)


class MainWindow(QWidget):
    """Окно с кнопкой на каждый эндпоинт и логом запросов/ответов."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Клиент учебного API")
        self.resize(900, 640)
        self._build_ui()

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Базовый URL + выбор роли
        top_row = QHBoxLayout()
        top_row.addWidget(QLabel(f"API: {api.BASE_URL}"))
        top_row.addStretch()
        top_row.addWidget(QLabel("Роль:"))
        self.role_selector = QComboBox()
        self.role_selector.addItems(["user", "admin"])
        top_row.addWidget(self.role_selector)
        layout.addLayout(top_row)

        # Кнопки эндпоинтов
        buttons_row = QHBoxLayout()
        buttons: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
            ("/public", api.call_public),
            ("/private/none", api.call_private_none),
            ("/private/admin", api.call_private_admin),
            ("/private/signed", api.call_private_signed),
            ("/private/encrypted", api.call_private_encrypted),
        ]
        for label, handler in buttons:
            button = QPushButton(label)
            button.clicked.connect(self._make_callback(handler))
            buttons_row.addWidget(button)
        layout.addLayout(buttons_row)

        # Предпросмотр токена
        layout.addWidget(QLabel("Сгенерированный токен (для последней использованной схемы):"))
        self.token_view = QPlainTextEdit()
        self.token_view.setReadOnly(True)
        self.token_view.setFixedHeight(90)
        layout.addWidget(self.token_view)

        # Лог
        layout.addWidget(QLabel("Лог запросов / ответов:"))
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view)

    def _make_callback(self, handler: Callable[[dict[str, Any]], dict[str, Any]]):
        """Оборачивает вызов API так, чтобы он также обновлял лог и предпросмотр токена."""

        def callback() -> None:
            role = self.role_selector.currentText()
            self._show_token(handler.__name__, role)
            result = handler(role) if self._accepts_role(handler) else handler()
            self._append_log(result)

        return callback

    @staticmethod
    def _accepts_role(handler: Callable[..., dict[str, Any]]) -> bool:
        return handler.__name__ != "call_public"

    # --------------------------------------------------------------- helpers
    def _show_token(self, handler_name: str, role: str) -> None:
        """Показывает токен, который клиент собирается отправить."""
        if handler_name in ("call_private_none", "call_private_admin"):
            token = build_unsigned_token(role)
        elif handler_name == "call_private_signed":
            token = build_signed_token(role)
        elif handler_name == "call_private_encrypted":
            token = build_encrypted_token(role)
        else:
            token = "(токен не отправляется)"
        self.token_view.setPlainText(token)

    def _append_log(self, result: dict[str, Any]) -> None:
        tags = "=" * 70
        lines = [tags]
        lines.append(f"GET {result.get('url', '?')}")
        if result.get("request_headers"):
            lines.append(f"Заголовки запроса: {result['request_headers']}")
        if result.get("error"):
            lines.append(f"ОШИБКА: {result['error']}")
        else:
            lines.append(f"Статус: {result.get('status')}")
            body = result.get("body")
            if isinstance(body, (dict, list)):
                lines.append(json.dumps(body, indent=2, ensure_ascii=False))
            else:
                lines.append(str(body))
        lines.append(tags)
        self.log_view.appendPlainText("\n".join(lines))
