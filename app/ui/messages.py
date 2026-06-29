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


def admin_dashboard(bot_name: str, user_mention: str) -> str:
    return (
        f"{Icons.ADMIN} <b>Admin Dashboard</b>\n\n"
        f"Welcome, {user_mention}.\n"
        f"<b>{bot_name}</b> management panel.\n\n"
        f"Select an option below."
    )


def admin_upload_placeholder() -> str:
    return (
        f"{Icons.UPLOAD} <b>Upload Movie</b>\n\n"
        f"Upload a new movie to the library.\n\n"
        f"This feature will be available soon."
    )


def admin_manage_placeholder() -> str:
    return (
        f"{Icons.MANAGE} <b>Manage Movies</b>\n\n"
        f"Edit, delete, or update existing movies.\n\n"
        f"This feature will be available soon."
    )


def admin_requests_placeholder() -> str:
    return (
        f"{Icons.REQUEST} <b>Movie Requests</b>\n\n"
        f"View and manage movie requests from users.\n\n"
        f"This feature will be available soon."
    )


def admin_broadcast_placeholder() -> str:
    return (
        f"{Icons.BROADCAST} <b>Broadcast</b>\n\n"
        f"Send messages to all bot users.\n\n"
        f"This feature will be available soon."
    )


def admin_users_placeholder() -> str:
    return (
        f"{Icons.USERS} <b>Users</b>\n\n"
        f"View and manage bot users.\n\n"
        f"This feature will be available soon."
    )


def admin_stats_placeholder() -> str:
    return (
        f"{Icons.STATS} <b>Statistics</b>\n\n"
        f"View bot usage statistics.\n\n"
        f"This feature will be available soon."
    )


def admin_settings_placeholder() -> str:
    return (
        f"{Icons.SETTINGS} <b>Settings</b>\n\n"
        f"Configure bot settings.\n\n"
        f"This feature will be available soon."
    )


def admin_backup_placeholder() -> str:
    return (
        f"{Icons.BACKUP} <b>Backup</b>\n\n"
        f"Backup and restore bot data.\n\n"
        f"This feature will be available soon."
    )


def admin_health_placeholder() -> str:
    return (
        f"{Icons.HEALTH} <b>Health Dashboard</b>\n\n"
        f"View system health status.\n\n"
        f"This feature will be available soon."
    )


def unauthorized_access() -> str:
    return f"{Icons.ERROR} You are not authorized to access this page."
