from pyrogram.types import InlineKeyboardMarkup

from app.core import CallbackAction
from app.keyboards import Button, KeyboardBuilder
from app.ui.icons import Icons


def home_keyboard() -> InlineKeyboardMarkup:
    return (
        KeyboardBuilder()
        .button(f"{Icons.SEARCH} Search Movie", CallbackAction.SEARCH)
        .button(f"{Icons.LATEST} Latest Movies", CallbackAction.LATEST)
        .button(f"{Icons.REQUEST} Request Movie", CallbackAction.REQUEST_MOVIE)
        .button(f"{Icons.UPDATES} Updates Channel", CallbackAction.UPDATES)
        .button(f"{Icons.CONTACT} Contact Admin", CallbackAction.CONTACT)
        .button(f"{Icons.ABOUT} About", CallbackAction.ABOUT)
        .build()
    )


def back_keyboard(action: CallbackAction = CallbackAction.HOME) -> InlineKeyboardMarkup:
    return (
        KeyboardBuilder()
        .button(f"{Icons.BACK} Back", action)
        .build()
    )


def simple_keyboard(buttons: list[Button]) -> InlineKeyboardMarkup:
    kb = KeyboardBuilder()
    for btn in buttons:
        kb.row(btn)
    return kb.build()
