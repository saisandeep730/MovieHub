from app.ui.icons import Icons


def welcome(bot_name: str) -> str:
    return (
        f"{Icons.LOGO} <b>{bot_name}</b>\n\n"
        f"Welcome to <b>{bot_name}</b> \u2014 your personal movie "
        f"storage and distribution system.\n\n"
        f"Use the buttons below to explore."
    )


def search_placeholder() -> str:
    return (
        f"{Icons.SEARCH} <b>Search Movie</b>\n\n"
        f"Search for movies by name.\n\n"
        f"This feature will be available soon."
    )


def latest_placeholder() -> str:
    return (
        f"{Icons.LATEST} <b>Latest Movies</b>\n\n"
        f"Browse the newest movies added to the library.\n\n"
        f"This feature will be available soon."
    )


def request_placeholder() -> str:
    return (
        f"{Icons.REQUEST} <b>Request Movie</b>\n\n"
        f"Can\u2019t find a movie? Request it here.\n\n"
        f"This feature will be available soon."
    )


def updates_placeholder() -> str:
    return (
        f"{Icons.UPDATES} <b>Updates Channel</b>\n\n"
        f"Join our updates channel to stay informed "
        f"about new releases.\n\n"
        f"This feature will be available soon."
    )


def contact_placeholder() -> str:
    return (
        f"{Icons.CONTACT} <b>Contact Admin</b>\n\n"
        f"Need help? Contact the administrator.\n\n"
        f"This feature will be available soon."
    )


def about(bot_name: str) -> str:
    return (
        f"{Icons.ABOUT} <b>About {bot_name}</b>\n\n"
        f"{Icons.MOVIE} <b>{bot_name}</b> is a Telegram-based "
        f"movie storage and distribution system.\n\n"
        f"{Icons.STAR} Version 1.0\n"
        f"{Icons.SETTINGS} Built with Pyrogram + MongoDB\n"
        f"{Icons.INFO} Fully manageable from Telegram"
    )


def error_screen() -> str:
    return f"{Icons.ERROR} Something went wrong. Please try again."
