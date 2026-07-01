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


def upload_title_prompt() -> str:
    return (
        f"{Icons.UPLOAD} <b>Upload New Movie</b>\n\n"
        f"Please send the movie title.\n\n"
        f"<b>Example:</b>\n"
        f"Avengers: Endgame"
    )


def upload_title_success(title: str) -> str:
    return (
        f"{Icons.SUCCESS} <b>Movie title saved.</b>\n\n"
        f"Now send the <b>release year</b>.\n\n"
        f"<b>Example:</b>\n"
        f"2019"
    )


def upload_title_invalid() -> str:
    return (
        f"{Icons.WARNING} <b>Invalid input.</b>\n\n"
        f"Please send a text message with the movie title.\n\n"
        f"<b>Example:</b>\n"
        f"Avengers: Endgame"
    )


def upload_year_success() -> str:
    return (
        f"{Icons.SUCCESS} <b>Release year saved.</b>\n\n"
        f"{Icons.MOVIE} Please send the movie poster.\n\n"
        f"If you don\u2019t have a poster, press Skip."
    )


def upload_year_invalid() -> str:
    return (
        f"{Icons.WARNING} <b>Invalid release year.</b>\n\n"
        f"Please send a valid year between <b>1888</b> and <b>{_current_year() + 2}</b>.\n\n"
        f"<b>Example:</b>\n"
        f"2023"
    )


def upload_poster_prompt(title: str) -> str:
    return (
        f"{Icons.UPLOAD} <b>Upload Poster</b>\n\n"
        f"<b>Movie:</b> {title}\n\n"
        f"Send a photo to use as the movie poster.\n\n"
        f"Or press Skip to continue without a poster."
    )


def upload_poster_success() -> str:
    return (
        f"{Icons.SUCCESS} <b>Poster saved.</b>\n\n"
        f"{Icons.FOLDER} Now forward all movie files together."
    )


def upload_poster_invalid() -> str:
    return (
        f"{Icons.WARNING} <b>Invalid input.</b>\n\n"
        f"Please send a <b>photo</b> to use as the movie poster."
    )


def no_drafts_message() -> str:
    return f"{Icons.INFO} <b>No Drafts Found</b>\n\nThere are no saved drafts."


def draft_detail_message(movie: dict) -> str:
    mid = movie.get("movie_id", "N/A")
    title = movie.get("title", "Unknown")
    year = movie.get("year", "N/A")
    status = movie.get("status", "unknown")
    return (
        f"{Icons.FILE} <b>Draft Details</b>\n\n"
        f"Movie ID: <code>{mid}</code>\n"
        f"Title: {title}\n"
        f"Year: {year}\n"
        f"Status: {status}\n\n"
        f"What would you like to do?"
    )


def upload_files_prompt() -> str:
    return (
        f"{Icons.FOLDER} Now forward all movie files together.\n\n"
        f"You can forward one or multiple files in a single step."
    )


def _current_year() -> int:
    from datetime import UTC, datetime
    return datetime.now(UTC).year
