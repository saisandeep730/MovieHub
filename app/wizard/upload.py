from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from logging import getLogger

from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from app.core import CallbackAction
from app.keyboards import Button, KeyboardBuilder
from app.ui.icons import Icons
from app.ui.keyboards import language_keyboard, quality_keyboard
from app.utils import normalize_title
from app.utils.filename_parser import (
    build_display_name,
    build_language_label,
    parse_filename,
)
from app.utils.filename_types import ParsedFile
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


def _file_short_label(f: ParsedFile, max_len: int = 28) -> str:
    return _truncate_name(f.original_filename, max_len)


def _rebuild_display_name(f: ParsedFile) -> str:
    if f.use_original_filename:
        return f.original_filename
    label = build_language_label(f.languages, None)
    return build_display_name(f.quality, label, f.season, f.episode, f.episode_end)


def _incomplete(f: ParsedFile) -> bool:
    return (f.missing_quality or f.missing_language) and not f.use_original_filename


def _validate_year(text: str) -> tuple[str | None, int | None]:
    text = text.strip()
    if not text.isdigit():
        return (
            f"Please send a valid year between "
            f"<b>{YEAR_MIN}</b> and <b>{datetime.now(UTC).year + YEAR_MAX_OFFSET}</b>.",
            None,
        )
    year = int(text)
    year_max = datetime.now(UTC).year + YEAR_MAX_OFFSET
    if year < YEAR_MIN or year > year_max:
        return (
            f"Please send a valid year between "
            f"<b>{YEAR_MIN}</b> and <b>{datetime.now(UTC).year + YEAR_MAX_OFFSET}</b>.",
            None,
        )
    return None, year


LANGUAGES_IN_ORDER = [
    "Hindi", "English", "Tamil", "Telugu",
    "Malayalam", "Kannada", "Japanese", "Korean",
    "Chinese", "Turkish",
]


@dataclass
class UploadContext(WizardContext):
    title: str | None = None
    year: int | None = None
    poster_file_id: str | None = None
    poster_unique_id: str | None = None
    files: list[ParsedFile] = field(default_factory=list)
    _validating: bool = False
    _edit_index: int | None = None
    _edit_phase: str = "list"
    _preview_edit_mode: str | None = None
    _preview_file_index: int | None = None
    _cancel_return_dashboard: bool = False


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
        err, _ = _validate_year(message.text)
        return err

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
        if not context._validating:
            return self._render_collection(context)
        if context._edit_index is not None:
            return self._render_edit(context)
        return self._render_validation_list(context)

    def _render_collection(self, context: UploadContext) -> str:
        n = len(context.files)
        if n == 0:
            return (
                f"Send video or document files.\n\n"
                f"Press <b>Continue</b> when you are done."
            )
        total_size = sum(f.file_size for f in context.files)
        lines: list[str] = [
            f"{Icons.FOLDER} <b>Files:</b> {n}  ({_format_size(total_size)})",
            "",
        ]
        for i, f in enumerate(context.files):
            if i >= _MAX_FILE_ROWS:
                lines.append(f"{Icons.INFO} ... and {n - _MAX_FILE_ROWS} more")
                break
            name = f.display_name or _truncate_name(f.original_filename)
            sz = _format_size(f.file_size)
            lines.append(f"  {i + 1}. {name} ({sz})")
        return "\n".join(lines)

    def _render_validation_list(self, context: UploadContext) -> str:
        lines: list[str] = [
            f"{Icons.WARNING} <b>Some files need additional information.</b>",
            "",
        ]
        for i, f in enumerate(context.files):
            if _incomplete(f):
                label = _file_short_label(f)
                missing: list[str] = []
                if f.missing_quality:
                    missing.append("Quality")
                if f.missing_language:
                    missing.append("Language")
                lines.append(
                    f"{i + 1}\uFE0F\u20E3 {label}\n"
                    f"{Icons.ERROR} Missing: {', '.join(missing)}"
                )
                lines.append("")
        return "\n".join(lines).rstrip()

    def _render_edit(self, context: UploadContext) -> str:
        f = context.files[context._edit_index]
        label = _file_short_label(f, 40)
        phase = context._edit_phase
        if phase == "quality":
            return (
                f"{Icons.FILE} <b>{label}</b>\n\n"
                f"Missing: Quality\n\n"
                f"Select a quality:"
            )
        if phase == "language":
            return (
                f"{Icons.FILE} <b>{label}</b>\n\n"
                f"Missing: Language\n\n"
                f"Select a language:"
            )
        if phase == "custom_quality":
            return (
                f"{Icons.FILE} <b>{label}</b>\n\n"
                f"Please type the quality value.\n\n"
                f"<b>Example:</b> 1080p"
            )
        if phase == "custom_language":
            return (
                f"{Icons.FILE} <b>{label}</b>\n\n"
                f"Please type the language value.\n\n"
                f"<b>Example:</b> Hindi"
            )
        return ""

    def render_summary_value(self, context: UploadContext) -> str | None:
        n = len(context.files)
        if n == 0:
            return None
        total_size = sum(f.file_size for f in context.files)
        return f"{n} files ({_format_size(total_size)})"

    def get_keyboard(
        self,
        has_back: bool = False,
        has_skip: bool = False,
        has_continue: bool = False,
        context: WizardContext | None = None,
    ) -> InlineKeyboardMarkup:
        ctx = context
        if not ctx or not ctx._validating:
            return self._collection_keyboard(ctx)
        if ctx._edit_index is not None:
            return self._edit_keyboard(ctx)
        return self._validation_list_keyboard(ctx)

    def _collection_keyboard(self, ctx: UploadContext | None) -> InlineKeyboardMarkup:
        has_cn = bool(ctx and ctx.files)
        return (
            KeyboardBuilder()
            .row(
                Button.action(f"{Icons.NEXT} Continue", CallbackAction.CONTINUE),
                Button.action(f"{Icons.ERROR} Cancel", CallbackAction.CANCEL),
            )
            .build()
        ) if has_cn else (
            KeyboardBuilder()
            .button(f"{Icons.ERROR} Cancel", CallbackAction.CANCEL)
            .build()
        )

    def _validation_list_keyboard(self, ctx: UploadContext) -> InlineKeyboardMarkup:
        kb = KeyboardBuilder()
        for i, f in enumerate(ctx.files):
            if not _incomplete(f):
                continue
            label = _file_short_label(f, 28)
            kb.button(
                f"{Icons.FILE} {label}",
                CallbackAction.FILE_SELECT, i,
            )
        all_resolved = not any(_incomplete(f) for f in ctx.files)
        if all_resolved:
            kb.row(
                Button.action(f"{Icons.NEXT} Continue", CallbackAction.CONTINUE),
                Button.action(f"{Icons.ERROR} Cancel", CallbackAction.CANCEL),
            )
        else:
            kb.button(f"{Icons.ERROR} Cancel", CallbackAction.CANCEL)
        return kb.build()

    def _edit_keyboard(self, ctx: UploadContext) -> InlineKeyboardMarkup:
        phase = ctx._edit_phase
        if phase == "quality":
            return quality_keyboard()
        if phase == "language":
            return language_keyboard()
        if phase in ("custom_quality", "custom_language"):
            return (
                KeyboardBuilder()
                .button(f"{Icons.ERROR} Cancel", CallbackAction.CANCEL)
                .build()
            )
        return (
            KeyboardBuilder()
            .button(f"{Icons.ERROR} Cancel", CallbackAction.CANCEL)
            .build()
        )

    def validate(self, message: Message, context: UploadContext) -> str | None:
        if context._validating and context._edit_phase in ("custom_quality", "custom_language"):
            if not message.text or not message.text.strip():
                return "Please send a text message with the value."
            return None
        if context._validating:
            return "Please use the buttons below."
        if message.video or message.document:
            return None
        return "Please send a <b>video</b> or <b>document</b> file."

    def process(self, message: Message, context: UploadContext) -> None:
        if context._validating and context._edit_phase == "custom_quality":
            self._apply_custom_quality(context, message.text.strip())
            return
        if context._validating and context._edit_phase == "custom_language":
            self._apply_custom_language(context, message.text.strip())
            return

        media = message.video or message.document
        file_name = (
            getattr(media, "file_name", None)
            or getattr(message.video, "file_name", None)
            or f"file_{len(context.files) + 1}"
        )

        parsed = parse_filename(file_name)
        parsed.file_id = media.file_id
        parsed.file_unique_id = media.file_unique_id
        parsed.file_size = media.file_size or 0
        parsed.mime_type = media.mime_type

        if not parsed.display_name:
            parsed.display_name = _truncate_name(parsed.original_filename)

        context.files.append(parsed)
        logger.info(
            "File added (step %d): %s (%s)",
            len(context.files), parsed.display_name, _format_size(media.file_size or 0),
        )

    def _apply_custom_quality(self, context: UploadContext, value: str) -> None:
        f = context.files[context._edit_index]
        f.quality = value
        f.missing_quality = False
        f.display_name = _rebuild_display_name(f)
        if f.missing_language:
            context._edit_phase = "language"
        else:
            context._edit_index = None
            context._edit_phase = "list"

    def _apply_custom_language(self, context: UploadContext, value: str) -> None:
        f = context.files[context._edit_index]
        lang = value.strip().title()
        f.languages = [lang]
        f.missing_language = False
        f.display_name = _rebuild_display_name(f)
        if f.missing_quality:
            context._edit_phase = "quality"
        else:
            context._edit_index = None
            context._edit_phase = "list"

    def on_continue(self, context: UploadContext) -> str | None:
        if context._validating:
            still_incomplete = any(_incomplete(f) for f in context.files)
            if still_incomplete:
                return ""
            context._validating = False
            context._edit_index = None
            context._edit_phase = "list"
            return None

        if not context.files:
            return "Please add at least one file before continuing."

        incomplete = [f for f in context.files if f.missing_quality or f.missing_language]
        if incomplete:
            context._validating = True
            context._edit_index = None
            context._edit_phase = "list"
            return ""

        return None

    async def handle_callback(
        self,
        client: object,
        callback: CallbackQuery,
        action: CallbackAction,
        args: list[str],
        context: UploadContext,
    ) -> None:
        if not context._validating:
            await callback.answer()
            return

        if action == CallbackAction.FILE_SELECT:
            idx = int(args[0])
            context._edit_index = idx
            f = context.files[idx]
            if f.missing_quality and f.missing_language:
                context._edit_phase = "quality"
            elif f.missing_quality:
                context._edit_phase = "quality"
            elif f.missing_language:
                context._edit_phase = "language"
            else:
                context._edit_index = None
                context._edit_phase = "list"

        elif action == CallbackAction.QUALITY_SELECT:
            if context._edit_index is None:
                return
            val = args[0]
            f = context.files[context._edit_index]
            f.quality = val
            f.missing_quality = False
            f.display_name = _rebuild_display_name(f)
            if f.missing_language and not f.use_original_filename:
                context._edit_phase = "language"
            else:
                context._edit_index = None
                context._edit_phase = "list"

        elif action == CallbackAction.LANGUAGE_SELECT:
            if context._edit_index is None:
                return
            val = args[0]
            f = context.files[context._edit_index]
            f.languages = [val]
            f.missing_language = False
            f.display_name = _rebuild_display_name(f)
            if f.missing_quality and not f.use_original_filename:
                context._edit_phase = "quality"
            else:
                context._edit_index = None
                context._edit_phase = "list"

        elif action == CallbackAction.USE_ORIGINAL:
            idx = int(args[0])
            f = context.files[idx]
            f.use_original_filename = True
            f.display_name = f.original_filename
            if context._edit_index == idx:
                context._edit_index = None
                context._edit_phase = "list"

        elif action == CallbackAction.CUSTOM_INPUT:
            if context._edit_index is None:
                return
            field = args[0]
            context._edit_phase = f"custom_{field}"


class PreviewStep(WizardStep):
    title = ""
    field_name = ""
    optional = False
    collects_multiple = False

    def render_prompt(self, context: UploadContext) -> str:
        mode = context._preview_edit_mode
        if mode is None:
            return self._render_preview(context)
        if mode == "menu":
            return self._render_edit_menu(context)
        if mode == "title":
            return f"{Icons.EDIT} <b>Edit Movie Title</b>\n\nCurrent: {context.title or 'N/A'}\n\nPlease send the new movie title."
        if mode == "year":
            return f"{Icons.EDIT} <b>Edit Release Year</b>\n\nCurrent: {context.year or 'N/A'}\n\nPlease send the new release year."
        if mode == "poster":
            return (
                f"{Icons.EDIT} <b>Edit Poster</b>\n\n"
                f"Current: {'Uploaded' if context.poster_file_id else 'None'}\n\n"
                f"Send a new photo, or press Back to keep the current poster."
            )
        if mode == "files":
            return self._render_file_management(context)
        if mode == "add_files":
            return self._render_add_files(context)
        return self._render_preview(context)

    def _render_preview(self, context: UploadContext) -> str:
        poster_text = (
            f"{Icons.SUCCESS} Uploaded"
            if context.poster_file_id is not None
            else f"{Icons.INFO} Skipped"
        )
        file_count = len(context.files)
        total_size = sum(f.file_size for f in context.files)

        lines: list[str] = [
            f"{Icons.MOVIE} <b>Movie:</b> {context.title or 'N/A'}",
            f"{Icons.CALENDAR} <b>Year:</b> {context.year or 'N/A'}",
            f"{Icons.WALLPAPER} <b>Poster:</b> {poster_text}",
            f"{Icons.FILE} <b>Files:</b> {file_count} ({_format_size(total_size)})",
            "",
        ]

        for i, f in enumerate(context.files):
            name = f.display_name or _truncate_name(f.original_filename, 40)
            sz = _format_size(f.file_size)
            lines.append(f"{Icons.FILE} {name} ({sz})")

        return "\n".join(lines)

    def _render_edit_menu(self, context: UploadContext) -> str:
        return (
            f"{Icons.EDIT} <b>Edit Movie</b>\n\n"
            f"Select what you would like to edit:"
        )

    def _render_file_management(self, context: UploadContext) -> str:
        if context._preview_file_index is not None:
            return self._render_file_detail(context)
        lines: list[str] = [
            f"{Icons.FILE} <b>Manage Files</b>",
            f"Total: {len(context.files)} files",
            "",
        ]
        for i, f in enumerate(context.files):
            name = f.display_name or _truncate_name(f.original_filename, 35)
            sz = _format_size(f.file_size)
            lines.append(f"{i + 1}. {name} ({sz})")
        return "\n".join(lines)

    def _render_file_detail(self, context: UploadContext) -> str:
        idx = context._preview_file_index
        f = context.files[idx]
        name = f.display_name or f.original_filename
        phase = context._edit_phase
        if phase == "quality":
            return (
                f"{Icons.FILE} <b>{name}</b>\n\n"
                f"Current quality: {f.quality or 'Unknown'}\n\n"
                f"Select a quality:"
            )
        if phase == "language":
            return (
                f"{Icons.FILE} <b>{name}</b>\n\n"
                f"Current language: {build_language_label(f.languages, None) or 'Unknown'}\n\n"
                f"Select a language:"
            )
        if phase == "custom_quality":
            return (
                f"{Icons.FILE} <b>{name}</b>\n\n"
                f"Please type the quality value.\n\n"
                f"<b>Example:</b> 1080p"
            )
        if phase == "custom_language":
            return (
                f"{Icons.FILE} <b>{name}</b>\n\n"
                f"Please type the language value.\n\n"
                f"<b>Example:</b> Hindi"
            )
        sz = _format_size(f.file_size)
        return (
            f"{Icons.FILE} <b>{name}</b>\n\n"
            f"Size: {sz}\n"
            f"Quality: {f.quality or 'Unknown'}\n"
            f"Language: {build_language_label(f.languages, None) or 'Unknown'}\n"
            f"Use Original: {'Yes' if f.use_original_filename else 'No'}"
        )

    def _render_add_files(self, context: UploadContext) -> str:
        n = len(context.files)
        total_size = sum(f.file_size for f in context.files)
        lines: list[str] = [
            f"{Icons.FILE} <b>Add Files</b>",
            f"Current files: {n} ({_format_size(total_size)})",
            "",
            f"Send video or document files to add.\n"
            f"Press <b>Continue</b> when done.",
        ]
        return "\n".join(lines)

    def get_keyboard(
        self,
        has_back: bool = False,
        has_skip: bool = False,
        has_continue: bool = False,
        context: WizardContext | None = None,
    ) -> InlineKeyboardMarkup:
        ctx = context
        if not ctx:
            return KeyboardBuilder().home()
        mode = ctx._preview_edit_mode
        if mode is None:
            return self._preview_keyboard()
        if mode == "menu":
            return self._edit_menu_keyboard(ctx)
        if mode == "title":
            return self._cancel_back_keyboard()
        if mode == "year":
            return self._cancel_back_keyboard()
        if mode == "poster":
            return self._poster_edit_keyboard()
        if mode == "files":
            return self._file_management_keyboard(ctx)
        if mode == "add_files":
            return self._add_files_keyboard(ctx)
        return self._preview_keyboard()

    def _preview_keyboard(self) -> InlineKeyboardMarkup:
        return (
            KeyboardBuilder()
            .row(
                Button.action(f"{Icons.EDIT} Edit", CallbackAction.PREVIEW_EDIT),
                Button.action(f"{Icons.SAVE} Save Draft", CallbackAction.SAVE_DRAFT),
            )
            .button(f"{Icons.PUBLISH} Publish", CallbackAction.PUBLISH)
            .button(f"{Icons.ERROR} Cancel", CallbackAction.CANCEL)
            .build()
        )

    def _edit_menu_keyboard(self, ctx: UploadContext) -> InlineKeyboardMarkup:
        kb = KeyboardBuilder()
        kb.button(f"{Icons.MOVIE} Title: {ctx.title or 'N/A'}", CallbackAction.EDIT_TITLE)
        kb.button(f"{Icons.CALENDAR} Year: {ctx.year or 'N/A'}", CallbackAction.EDIT_YEAR)
        poster_status = "Set" if ctx.poster_file_id else "None"
        kb.button(f"{Icons.WALLPAPER} Poster: {poster_status}", CallbackAction.EDIT_POSTER)
        kb.button(f"{Icons.FILE} Files ({len(ctx.files)})", CallbackAction.MANAGE_FILES)
        kb.button(f"{Icons.BACK} Back to Preview", CallbackAction.BACK_TO_PREVIEW)
        return kb.build()

    def _cancel_back_keyboard(self) -> InlineKeyboardMarkup:
        return (
            KeyboardBuilder()
            .button(f"{Icons.BACK} Back", CallbackAction.BACK_TO_PREVIEW)
            .build()
        )

    def _poster_edit_keyboard(self) -> InlineKeyboardMarkup:
        return (
            KeyboardBuilder()
            .row(
                Button.action(f"{Icons.SKIP} Remove Poster", CallbackAction.SKIP),
                Button.action(f"{Icons.BACK} Back", CallbackAction.BACK_TO_PREVIEW),
            )
            .build()
        )

    def _file_management_keyboard(self, ctx: UploadContext) -> InlineKeyboardMarkup:
        if ctx._preview_file_index is not None:
            return self._file_detail_keyboard(ctx)
        kb = KeyboardBuilder()
        for i in range(len(ctx.files)):
            f = ctx.files[i]
            label = f.display_name or _truncate_name(f.original_filename, 20)
            kb.button(f"{i + 1}. {label}", CallbackAction.FILE_SELECT, i)
        kb.button(f"{Icons.UPLOAD} Add Files", CallbackAction.MANAGE_FILES)
        kb.button(f"{Icons.BACK} Back to Edit Menu", CallbackAction.BACK_TO_PREVIEW)
        return kb.build()

    def _file_detail_keyboard(self, ctx: UploadContext) -> InlineKeyboardMarkup:
        phase = ctx._edit_phase
        if phase == "quality":
            return quality_keyboard()
        if phase == "language":
            return language_keyboard()
        if phase in ("custom_quality", "custom_language"):
            return (
                KeyboardBuilder()
                .button(f"{Icons.BACK} Back", CallbackAction.BACK_TO_PREVIEW)
                .build()
            )
        idx = ctx._preview_file_index
        kb = KeyboardBuilder()
        kb.button(f"{Icons.EDIT} Edit Quality", CallbackAction.QUALITY_SELECT, ctx.files[idx].quality or "edit")
        kb.button(f"{Icons.EDIT} Edit Language", CallbackAction.LANGUAGE_SELECT, "edit")
        kb.button(f"{Icons.FILE} Use Original Filename", CallbackAction.USE_ORIGINAL, idx)
        kb.button(f"{Icons.ERROR} Remove File", CallbackAction.FILE_REMOVE, idx)
        kb.button(f"{Icons.BACK} Back to File List", CallbackAction.MANAGE_FILES)
        return kb.build()

    def _add_files_keyboard(self, ctx: UploadContext) -> InlineKeyboardMarkup:
        return (
            KeyboardBuilder()
            .row(
                Button.action(f"{Icons.NEXT} Continue", CallbackAction.CONTINUE),
                Button.action(f"{Icons.BACK} Back", CallbackAction.BACK_TO_PREVIEW),
            )
            .build()
        )

    def validate(self, message: Message, context: UploadContext) -> str | None:
        mode = context._preview_edit_mode
        if mode == "title":
            if not message.text or not message.text.strip():
                return "Please send a text message with the new title."
            return None
        if mode == "year":
            if not message.text or not message.text.strip():
                return (
                    f"Please send a valid year between "
                    f"<b>{YEAR_MIN}</b> and <b>{datetime.now(UTC).year + YEAR_MAX_OFFSET}</b>."
                )
            err, _ = _validate_year(message.text)
            return err
        if mode == "poster":
            if message.photo:
                return None
            return "Please send a <b>photo</b> to use as the movie poster."
        if mode == "add_files":
            if message.video or message.document:
                return None
            return "Please send a <b>video</b> or <b>document</b> file."
        if context._preview_file_index is not None and context._edit_phase in ("custom_quality", "custom_language"):
            if not message.text or not message.text.strip():
                return "Please send a text message with the value."
            return None
        return "Please use the buttons below."

    def process(self, message: Message, context: UploadContext) -> None:
        mode = context._preview_edit_mode
        if mode == "title":
            context.title = normalize_title(message.text.strip())
            context._preview_edit_mode = "menu"
            return
        if mode == "year":
            context.year = int(message.text.strip())
            context._preview_edit_mode = "menu"
            return
        if mode == "poster":
            context.poster_file_id = message.photo.file_id
            context.poster_unique_id = getattr(message.photo, "file_unique_id", None)
            context._preview_edit_mode = "menu"
            return
        if mode == "add_files":
            media = message.video or message.document
            file_name = (
                getattr(media, "file_name", None)
                or getattr(message.video, "file_name", None)
                or f"file_{len(context.files) + 1}"
            )
            parsed = parse_filename(file_name)
            parsed.file_id = media.file_id
            parsed.file_unique_id = media.file_unique_id
            parsed.file_size = media.file_size or 0
            parsed.mime_type = media.mime_type
            if not parsed.display_name:
                parsed.display_name = _truncate_name(parsed.original_filename)
            context.files.append(parsed)
            return
        if context._preview_file_index is not None and context._edit_phase == "custom_quality":
            f = context.files[context._preview_file_index]
            f.quality = message.text.strip()
            f.missing_quality = False
            f.display_name = _rebuild_display_name(f)
            context._edit_phase = "list"
            return
        if context._preview_file_index is not None and context._edit_phase == "custom_language":
            f = context.files[context._preview_file_index]
            f.languages = [message.text.strip().title()]
            f.missing_language = False
            f.display_name = _rebuild_display_name(f)
            context._edit_phase = "list"
            return

    def on_continue(self, context: UploadContext) -> str | None:
        if context._preview_edit_mode == "add_files":
            context._preview_edit_mode = "files"
            return None
        return None

    def on_skip(self, context: UploadContext) -> None:
        if context._preview_edit_mode == "poster":
            context.poster_file_id = None
            context.poster_unique_id = None
            context._preview_edit_mode = "menu"

    async def handle_callback(
        self,
        client: object,
        callback: CallbackQuery,
        action: CallbackAction,
        args: list[str],
        context: UploadContext,
    ) -> None:
        if action == CallbackAction.PREVIEW_EDIT:
            context._preview_edit_mode = "menu"
            context._preview_file_index = None
            context._edit_phase = "list"

        elif action == CallbackAction.EDIT_TITLE:
            context._preview_edit_mode = "title"

        elif action == CallbackAction.EDIT_YEAR:
            context._preview_edit_mode = "year"

        elif action == CallbackAction.EDIT_POSTER:
            context._preview_edit_mode = "poster"

        elif action == CallbackAction.MANAGE_FILES:
            if context._preview_file_index is not None:
                context._preview_file_index = None
                context._edit_phase = "list"
            elif context._preview_edit_mode == "files":
                context._preview_edit_mode = "add_files"
            else:
                context._preview_edit_mode = "files"

        elif action == CallbackAction.FILE_SELECT:
            idx = int(args[0])
            context._preview_file_index = idx
            context._edit_phase = "list"

        elif action == CallbackAction.FILE_REMOVE:
            idx = int(args[0])
            if 0 <= idx < len(context.files):
                removed = context.files.pop(idx)
                logger.info("File removed during preview edit: %s", removed.original_filename)
            if context._preview_file_index == idx:
                context._preview_file_index = None
            elif context._preview_file_index is not None and context._preview_file_index > idx:
                context._preview_file_index -= 1

        elif action == CallbackAction.QUALITY_SELECT:
            idx = context._preview_file_index
            if idx is not None and 0 <= idx < len(context.files):
                f = context.files[idx]
                f.quality = args[0]
                f.display_name = _rebuild_display_name(f)
                context._edit_phase = "list"

        elif action == CallbackAction.LANGUAGE_SELECT:
            val = args[0]
            idx = context._preview_file_index
            if idx is not None and 0 <= idx < len(context.files):
                f = context.files[idx]
                f.languages = [val]
                f.missing_language = False
                f.display_name = _rebuild_display_name(f)
                context._edit_phase = "list"

        elif action == CallbackAction.USE_ORIGINAL:
            idx = int(args[0])
            if 0 <= idx < len(context.files):
                f = context.files[idx]
                f.use_original_filename = True
                f.display_name = f.original_filename

        elif action == CallbackAction.CUSTOM_INPUT:
            if context._preview_file_index is not None:
                field = args[0]
                context._edit_phase = f"custom_{field}"

        elif action == CallbackAction.BACK_TO_PREVIEW:
            if context._preview_edit_mode == "add_files":
                context._preview_edit_mode = "files"
            else:
                context._preview_edit_mode = None
            context._preview_file_index = None
            context._edit_phase = "list"

        else:
            await callback.answer()
