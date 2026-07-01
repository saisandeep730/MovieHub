from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from logging import getLogger

from pyrogram.types import InlineKeyboardMarkup, Message

from app.core import CallbackAction
from app.keyboards import Button, KeyboardBuilder

from app.ui.icons import Icons
from app.utils import normalize_title
from app.wizard.core import WizardContext, WizardStep

logger = getLogger(__name__)

YEAR_MIN = 1888
YEAR_MAX_OFFSET = 2
_MAX_FILE_ROWS = 5


def _format_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    elif size < 1024 ** 2:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 ** 3:
        return f"{size / 1024 ** 2:.1f} MB"
    else:
        return f"{size / 1024 ** 3:.2f} GB"


def _truncate_name(name: str, max_len: int = 30) -> str:
    if not name:
        return "unknown"
    if len(name) <= max_len:
        return name
    return name[: max_len - 3] + "..."


@dataclass
class UploadContext(WizardContext):
    title: str | None = None
    year: int | None = None
    poster_file_id: str | None = None
    poster_unique_id: str | None = None
    files: list[dict] = field(default_factory=list)


class TitleStep(WizardStep):
    title = "Movie Title"
    field_name = "title"

    def render_prompt(self, context: UploadContext) -> str:
        return (
            f"Please send the movie title.\n\n"
            f"<b>Example:</b>\n"
            f"Avengers: Endgame"
        )

    def render_summary_value(self, context: UploadContext) -> str | None:
        return context.title if context.title else None

    def validate(self, message: Message, context: UploadContext) -> str | None:
        if not message.text or not message.text.strip():
            return "Please send a text message with the movie title."
        return None

    def process(self, message: Message, context: UploadContext) -> None:
        raw = message.text.strip()
        context.title = normalize_title(raw)


class YearStep(WizardStep):
    title = "Release Year"
    field_name = "year"

    def render_prompt(self, context: UploadContext) -> str:
        return (
            f"Please send the release year.\n\n"
            f"<b>Example:</b>\n"
            f"2019"
        )

    def render_summary_value(self, context: UploadContext) -> str | None:
        return str(context.year) if context.year else None

    def validate(self, message: Message, context: UploadContext) -> str | None:
        if not message.text or not message.text.strip():
            return (
                f"Please send a valid year between "
                f"<b>{YEAR_MIN}</b> and <b>{datetime.now(UTC).year + YEAR_MAX_OFFSET}</b>."
            )
        text = message.text.strip()
        if not text.isdigit():
            return (
                f"Please send a valid year between "
                f"<b>{YEAR_MIN}</b> and <b>{datetime.now(UTC).year + YEAR_MAX_OFFSET}</b>."
            )
        year = int(text)
        year_max = datetime.now(UTC).year + YEAR_MAX_OFFSET
        if year < YEAR_MIN or year > year_max:
            return (
                f"Please send a valid year between "
                f"<b>{YEAR_MIN}</b> and <b>{datetime.now(UTC).year + YEAR_MAX_OFFSET}</b>."
            )
        return None

    def process(self, message: Message, context: UploadContext) -> None:
        context.year = int(message.text.strip())


class PosterStep(WizardStep):
    title = "Movie Poster"
    field_name = "poster_file_id"
    optional = True

    def render_prompt(self, context: UploadContext) -> str:
        return (
            f"Please send a photo to use as the movie poster.\n\n"
            f"Or press Skip to continue without a poster."
        )

    def render_summary_value(self, context: UploadContext) -> str | None:
        if context.poster_file_id is None:
            return None
        return "Poster"

    def validate(self, message: Message, context: UploadContext) -> str | None:
        if message.photo:
            return None
        return "Please send a <b>photo</b> to use as the movie poster."

    def process(self, message: Message, context: UploadContext) -> None:
        context.poster_file_id = message.photo.file_id
        context.poster_unique_id = getattr(message.photo, "file_unique_id", None)

    def on_skip(self, context: UploadContext) -> None:
        context.poster_file_id = None
        context.poster_unique_id = None


class FilesStep(WizardStep):
    title = "Movie Files"
    field_name = "files"
    collects_multiple = True

    def render_prompt(self, context: UploadContext) -> str:
        n = len(context.files)
        if n == 0:
            return (
                f"Send video or document files.\n\n"
                f"Press <b>Continue</b> when you are done."
            )

        total_size = sum(f["file_size"] for f in context.files)
        header = (
            f"{Icons.FOLDER} <b>Files:</b> {n}  "
            f"({_format_size(total_size)})\n\n"
        )

        file_lines: list[str] = []
        for i, f in enumerate(context.files):
            if i >= _MAX_FILE_ROWS:
                remaining = n - _MAX_FILE_ROWS
                file_lines.append(f"{Icons.INFO} ... and {remaining} more")
                break
            name = _truncate_name(f.get("file_name", ""))
            sz = _format_size(f.get("file_size", 0))
            file_lines.append(f"  {i + 1}. {name} ({sz})")

        return header + "\n".join(file_lines) if file_lines else header.rstrip()

    def render_summary_value(self, context: UploadContext) -> str | None:
        n = len(context.files)
        if n == 0:
            return None
        total_size = sum(f["file_size"] for f in context.files)
        return f"{n} files ({_format_size(total_size)})"

    def validate(self, message: Message, context: UploadContext) -> str | None:
        if message.video or message.document:
            return None
        return "Please send a <b>video</b> or <b>document</b> file."

    def process(self, message: Message, context: UploadContext) -> None:
        media = message.video or message.document
        file_name = (
            getattr(media, "file_name", None)
            or getattr(message.video, "file_name", None)
            or f"file_{len(context.files) + 1}"
        )
        context.files.append({
            "file_id": media.file_id,
            "file_unique_id": media.file_unique_id,
            "file_name": file_name,
            "file_size": media.file_size or 0,
            "mime_type": media.mime_type,
        })
        logger.info(
            "File added (step %d): %s (%s)",
            len(context.files), file_name, _format_size(media.file_size or 0),
        )


class PreviewStep(WizardStep):
    title = ""
    field_name = ""
    optional = False
    collects_multiple = False

    def render_prompt(self, context: UploadContext) -> str:
        poster_text = (
            f"{Icons.SUCCESS} Uploaded"
            if context.poster_file_id is not None
            else f"{Icons.INFO} Skipped"
        )
        file_count = len(context.files)
        total_size = sum(f["file_size"] for f in context.files)

        lines: list[str] = [
            f"{Icons.MOVIE} <b>Movie:</b> {context.title or 'N/A'}",
            f"{Icons.CALENDAR} <b>Year:</b> {context.year or 'N/A'}",
            f"{Icons.WALLPAPER} <b>Poster:</b> {poster_text}",
            f"{Icons.FOLDER} <b>Files:</b> {file_count} ({_format_size(total_size)})",
            "",
        ]

        for i, f in enumerate(context.files):
            name = _truncate_name(f.get("file_name", ""), 40)
            sz = _format_size(f.get("file_size", 0))
            lines.append(f"{Icons.FILE} {name} ({sz})")

        return "\n".join(lines)

    def get_keyboard(
        self,
        has_back: bool = False,
        has_skip: bool = False,
        has_continue: bool = False,
        context: WizardContext | None = None,
    ) -> InlineKeyboardMarkup:
        return (
            KeyboardBuilder()
            .row(
                Button.action(f"{Icons.EDIT} Edit", CallbackAction.EDIT),
                Button.action(f"{Icons.SAVE} Save Draft", CallbackAction.SAVE_DRAFT),
            )
            .button(f"{Icons.PUBLISH} Publish", CallbackAction.PUBLISH)
            .button(f"{Icons.ERROR} Cancel", CallbackAction.CANCEL)
            .build()
        )

    def validate(self, message: Message, context: UploadContext) -> str | None:
        return "Please use the buttons below."

    def process(self, message: Message, context: UploadContext) -> None:
        pass
