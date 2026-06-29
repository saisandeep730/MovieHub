from __future__ import annotations

import re
from enum import Enum
from typing import Any

SEPARATOR = "|"
_MAX_CALLBACK_LENGTH = 64


class CallbackAction(str, Enum):
    HOME = "home"
    SEARCH = "search"
    MOVIE_DETAIL = "mv"
    DOWNLOAD_FILE = "dl"
    REQUEST_MOVIE = "rq"
    LATEST = "lt"
    UPDATES = "up"
    CONTACT = "ct"
    ABOUT = "ab"
    PAGE_NEXT = "pn"
    PAGE_PREV = "pp"
    PAGE_GOTO = "pg"
    CONFIRM = "cf"
    CANCEL = "cx"
    BACK = "bk"
    ADMIN_HOME = "ah"
    ADMIN_UPLOAD = "au"
    ADMIN_MANAGE = "am"
    ADMIN_REQUESTS = "ar"
    ADMIN_BROADCAST = "ab"
    ADMIN_USERS = "aus"
    ADMIN_STATS = "as"
    ADMIN_SETTINGS = "ad"
    ADMIN_BACKUP = "ak"
    ADMIN_HEALTH = "ahc"


def encode(action: CallbackAction, *args: str | int) -> str:
    """Encode a callback action with optional payload arguments.

    Result must stay within Telegram's 64-byte callback_data limit.
    """
    parts = [action.value, *(str(a) for a in args)]
    result = SEPARATOR.join(parts)
    if len(result.encode()) > _MAX_CALLBACK_LENGTH:
        raise ValueError(
            f"Callback data exceeds {_MAX_CALLBACK_LENGTH} bytes: {result}"
        )
    return result


def decode(data: str) -> tuple[CallbackAction, list[str]]:
    """Decode a callback data string into an action and argument list."""
    parts = data.split(SEPARATOR)
    action = CallbackAction(parts[0])
    args = parts[1:]
    return action, args


def is_valid_callback(data: str) -> bool:
    """Check whether a string is a valid encoded callback."""
    try:
        action, _ = decode(data)
        return action in CallbackAction
    except (ValueError, KeyError):
        return False
