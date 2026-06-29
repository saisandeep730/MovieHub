from __future__ import annotations

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core import CallbackAction, encode


class Button:
    """Represents a single inline keyboard button."""

    def __init__(self, text: str, callback_data: str) -> None:
        self.text = text
        self.callback_data = callback_data

    def to_dict(self) -> dict[str, str]:
        return {"text": self.text, "callback_data": self.callback_data}

    @classmethod
    def action(cls, text: str, action: CallbackAction, *args: str | int) -> Button:
        return cls(text, encode(action, *args))

    @classmethod
    def url(cls, text: str, url: str) -> Button:
        btn = cls.__new__(cls)
        btn.text = text
        btn.callback_data = url
        return btn

    def to_url_dict(self) -> dict[str, str]:
        return {"text": self.text, "url": self.callback_data}


class Row(list[Button]):
    """A single row of inline keyboard buttons."""


class KeyboardBuilder:
    """Builds Telegram inline keyboard markup row by row."""

    def __init__(self) -> None:
        self._rows: list[Row] = []

    def row(self, *buttons: Button) -> KeyboardBuilder:
        self._rows.append(Row(buttons))
        return self

    def button(self, text: str, action: CallbackAction, *args: str | int) -> KeyboardBuilder:
        return self.row(Button.action(text, action, *args))

    def url_button(self, text: str, url: str) -> KeyboardBuilder:
        return self.row(Button.url(text, url))

    def build(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            [[InlineKeyboardButton(b.text, callback_data=b.callback_data) for b in row] for row in self._rows]
        )

    def build_with_urls(self) -> InlineKeyboardMarkup:
        result: list[list[InlineKeyboardButton]] = []
        for row in self._rows:
            formatted: list[InlineKeyboardButton] = []
            for btn in row:
                if btn.callback_data.startswith("http"):
                    formatted.append(InlineKeyboardButton(btn.text, url=btn.callback_data))
                else:
                    formatted.append(InlineKeyboardButton(btn.text, callback_data=btn.callback_data))
            result.append(formatted)
        return InlineKeyboardMarkup(result)

    @staticmethod
    def home() -> InlineKeyboardMarkup:
        return KeyboardBuilder().button("🏠 Home", CallbackAction.HOME).build()
