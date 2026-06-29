from __future__ import annotations

from typing import Any

from pyrogram.enums import ParseMode

from app.keyboards import KeyboardBuilder


class MessageBuilder:
    """Builds reusable message layouts with optional keyboard attachments."""

    def __init__(self, text: str = "") -> None:
        self._text = text
        self._keyboard: KeyboardBuilder | None = None
        self._parse_mode: ParseMode = ParseMode.HTML

    def text(self, content: str) -> MessageBuilder:
        self._text = content
        return self

    def keyboard(self, builder: KeyboardBuilder) -> MessageBuilder:
        self._keyboard = builder
        return self

    def parse_mode(self, mode: ParseMode) -> MessageBuilder:
        self._parse_mode = mode
        return self

    def build(self) -> dict[str, Any]:
        result: dict[str, Any] = {"text": self._text, "parse_mode": self._parse_mode}
        if self._keyboard:
            result["reply_markup"] = self._keyboard.build()
        return result

    @staticmethod
    def simple(text: str, *buttons: Any) -> dict[str, Any]:
        builder = KeyboardBuilder()
        for btn in buttons:
            builder.row(btn)
        return MessageBuilder(text).keyboard(builder).build()
