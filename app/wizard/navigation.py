from pyrogram.types import InlineKeyboardMarkup

from app.core import CallbackAction
from app.keyboards import Button, KeyboardBuilder
from app.ui.icons import Icons


def wizard_nav_keyboard(
    has_back: bool = False,
    has_skip: bool = False,
    has_continue: bool = False,
) -> InlineKeyboardMarkup:
    kb = KeyboardBuilder()

    if has_continue:
        kb.row(
            Button.action(f"{Icons.NEXT} Continue", CallbackAction.CONTINUE),
            Button.action(f"{Icons.ERROR} Cancel", CallbackAction.CANCEL),
        )
    elif has_skip:
        kb.row(
            Button.action(f"{Icons.SKIP} Skip", CallbackAction.SKIP),
            Button.action(f"{Icons.ERROR} Cancel", CallbackAction.CANCEL),
        )
    elif has_back:
        kb.row(
            Button.action(f"{Icons.BACK} Back", CallbackAction.WIZARD_BACK),
            Button.action(f"{Icons.ERROR} Cancel", CallbackAction.CANCEL),
        )
    else:
        kb.row(Button.action(f"{Icons.ERROR} Cancel", CallbackAction.CANCEL))

    return kb.build()
