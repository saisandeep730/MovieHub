from __future__ import annotations

from dataclasses import asdict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.utils.filename_types import ParsedFile
from app.wizard.upload import (
    FilesStep,
    PreviewStep,
    TitleStep,
    UploadContext,
    YearStep,
    _format_size,
    _rebuild_display_name,
    _truncate_name,
)


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def make_parsed_file(
    original_filename: str = "Test.Movie.2023.1080p.Hindi.mkv",
    quality: str = "1080p",
    languages: list[str] | None = None,
    file_size: int = 1_000_000,
    file_id: str = "abc123",
    file_unique_id: str = "unique1",
    season: str | None = None,
    episode: str | None = None,
    episode_end: str | None = None,
    missing_quality: bool = False,
    missing_language: bool = False,
    use_original_filename: bool = False,
) -> ParsedFile:
    from app.utils.filename_parser import build_display_name, build_language_label
    langs = languages or ["Hindi"]
    label = build_language_label(langs, None)
    display_name = build_display_name(quality, label, season, episode, episode_end)
    return ParsedFile(
        original_filename=original_filename,
        display_name=display_name or original_filename,
        quality=quality,
        languages=langs,
        season=season,
        episode=episode,
        episode_end=episode_end,
        missing_quality=missing_quality,
        missing_language=missing_language,
        file_size=file_size,
        file_id=file_id,
        file_unique_id=file_unique_id,
        use_original_filename=use_original_filename,
    )


def make_context(**overrides: object) -> UploadContext:
    defaults = {
        "title": "Test Movie",
        "year": 2023,
        "poster_file_id": "poster123",
        "poster_unique_id": "poster_unique",
        "files": [make_parsed_file()],
        "_validating": False,
        "_edit_index": None,
        "_edit_phase": "list",
        "_preview_edit_mode": None,
        "_preview_file_index": None,
    }
    merged = {**defaults, **overrides}
    ctx = UploadContext()
    for k, v in merged.items():
        setattr(ctx, k, v)
    return ctx


def mock_message(
    text: str | None = None,
    photo: bool = False,
    video: bool = False,
    document: bool = False,
) -> MagicMock:
    msg = MagicMock()
    msg.text = text
    if photo:
        msg.photo.file_id = "photo_id"
        msg.photo.file_unique_id = "photo_uid"
    else:
        msg.photo = None
    if video:
        msg.video.file_name = "video.mp4"
        msg.video.file_id = "vid123"
        msg.video.file_unique_id = "vid_uid"
        msg.video.file_size = 500_000_000
        msg.video.mime_type = "video/mp4"
    else:
        msg.video = None
    if document:
        msg.document.file_name = "doc.mkv"
        msg.document.file_id = "doc123"
        msg.document.file_unique_id = "doc_uid"
        msg.document.file_size = 1_000_000_000
        msg.document.mime_type = "video/x-matroska"
    else:
        msg.document = None
    return msg


def mock_callback(data: str = "") -> MagicMock:
    cb = MagicMock()
    cb.data = data
    cb.from_user.id = 12345
    cb.from_user.mention = "Admin"
    cb.message.chat.id = -100123
    cb.answer = AsyncMock()
    cb.edit_message_text = AsyncMock()
    return cb


# ══════════════════════════════════════════════════════════════════════════════
# 1. PREVIEW SCREEN GENERATION
# ══════════════════════════════════════════════════════════════════════════════

class TestPreviewRender:
    def test_preview_shows_title_year_poster_files(self):
        ctx = make_context()
        step = PreviewStep()
        text = step.render_prompt(ctx)
        assert "Test Movie" in text
        assert "2023" in text
        assert "1080p" in text
        assert "Hindi" in text
        assert "977 KB" in text or "1" in text

    def test_preview_shows_no_poster(self):
        ctx = make_context(poster_file_id=None, poster_unique_id=None)
        step = PreviewStep()
        text = step.render_prompt(ctx)
        assert "Skipped" in text

    def test_preview_shows_multiple_files(self):
        f1 = make_parsed_file(original_filename="a.mkv", quality="1080p")
        f2 = make_parsed_file(original_filename="b.mkv", quality="720p")
        ctx = make_context(files=[f1, f2])
        step = PreviewStep()
        text = step.render_prompt(ctx)
        assert "1080p" in text
        assert "720p" in text

    def test_preview_shows_display_name_not_raw_name(self):
        f = make_parsed_file(original_filename="super.raw.name.1080p.Hindi.mkv")
        ctx = make_context(files=[f])
        step = PreviewStep()
        text = step.render_prompt(ctx)
        assert f.display_name in text
        assert "super.raw.name" not in text or f.display_name == "super.raw.name"

    def test_preview_edit_menu_shows_options(self):
        ctx = make_context(_preview_edit_mode="menu")
        step = PreviewStep()
        text = step.render_prompt(ctx)
        assert "Edit Movie" in text
        kb = step.get_keyboard(context=ctx)
        assert kb is not None

    def test_preview_title_edit_prompt(self):
        ctx = make_context(_preview_edit_mode="title")
        step = PreviewStep()
        text = step.render_prompt(ctx)
        assert "Edit Movie Title" in text
        assert "Test Movie" in text

    def test_preview_year_edit_prompt(self):
        ctx = make_context(_preview_edit_mode="year")
        step = PreviewStep()
        text = step.render_prompt(ctx)
        assert "Edit Release Year" in text
        assert "2023" in text

    def test_preview_poster_edit_prompt(self):
        ctx = make_context(_preview_edit_mode="poster")
        step = PreviewStep()
        text = step.render_prompt(ctx)
        assert "Edit Poster" in text

    def test_preview_no_poster_on_edit_prompt(self):
        ctx = make_context(_preview_edit_mode="poster", poster_file_id=None)
        step = PreviewStep()
        text = step.render_prompt(ctx)
        assert "None" in text


# ══════════════════════════════════════════════════════════════════════════════
# 2. PREVIEW KEYBOARD
# ══════════════════════════════════════════════════════════════════════════════

class TestPreviewKeyboard:
    def test_preview_keyboard_default(self):
        ctx = make_context()
        step = PreviewStep()
        kb = step.get_keyboard(context=ctx)
        assert kb is not None

    def test_edit_menu_keyboard(self):
        ctx = make_context(_preview_edit_mode="menu")
        step = PreviewStep()
        kb = step.get_keyboard(context=ctx)
        assert kb is not None

    def test_title_edit_keyboard(self):
        ctx = make_context(_preview_edit_mode="title")
        step = PreviewStep()
        kb = step.get_keyboard(context=ctx)
        assert kb is not None

    def test_file_management_keyboard(self):
        ctx = make_context(_preview_edit_mode="files")
        step = PreviewStep()
        kb = step.get_keyboard(context=ctx)
        assert kb is not None

    def test_file_detail_keyboard(self):
        ctx = make_context(_preview_edit_mode="files", _preview_file_index=0)
        step = PreviewStep()
        kb = step.get_keyboard(context=ctx)
        assert kb is not None

    def test_add_files_keyboard(self):
        ctx = make_context(_preview_edit_mode="add_files")
        step = PreviewStep()
        kb = step.get_keyboard(context=ctx)
        assert kb is not None


# ══════════════════════════════════════════════════════════════════════════════
# 3. PREVIEW EDIT — TITLE / YEAR / POSTER CHANGES
# ══════════════════════════════════════════════════════════════════════════════

class TestPreviewEditFieldChanges:
    def test_edit_title_text(self):
        ctx = make_context(_preview_edit_mode="title")
        step = PreviewStep()
        msg = mock_message(text="New Title")
        assert step.validate(msg, ctx) is None
        step.process(msg, ctx)
        assert ctx.title == "new title"
        assert ctx._preview_edit_mode == "menu"

    def test_edit_year_valid(self):
        ctx = make_context(_preview_edit_mode="year")
        step = PreviewStep()
        msg = mock_message(text="2024")
        assert step.validate(msg, ctx) is None
        step.process(msg, ctx)
        assert ctx.year == 2024
        assert ctx._preview_edit_mode == "menu"

    def test_edit_year_invalid_text(self):
        ctx = make_context(_preview_edit_mode="year")
        step = PreviewStep()
        msg = mock_message(text="abc")
        assert step.validate(msg, ctx) is not None

    def test_edit_year_invalid_future(self):
        ctx = make_context(_preview_edit_mode="year")
        step = PreviewStep()
        msg = mock_message(text="99999")
        assert step.validate(msg, ctx) is not None

    def test_edit_poster_photo(self):
        ctx = make_context(_preview_edit_mode="poster", poster_file_id=None)
        step = PreviewStep()
        msg = mock_message(photo=True)
        assert step.validate(msg, ctx) is None
        step.process(msg, ctx)
        assert ctx.poster_file_id == "photo_id"
        assert ctx._preview_edit_mode == "menu"

    def test_edit_poster_non_photo_rejected(self):
        ctx = make_context(_preview_edit_mode="poster")
        step = PreviewStep()
        msg = mock_message(text="not a photo")
        assert step.validate(msg, ctx) is not None

    def test_edit_poster_skip_clears(self):
        ctx = make_context(_preview_edit_mode="poster", poster_file_id="old")
        step = PreviewStep()
        step.on_skip(ctx)
        assert ctx.poster_file_id is None
        assert ctx._preview_edit_mode == "menu"

    def test_edit_title_empty_rejected(self):
        ctx = make_context(_preview_edit_mode="title")
        step = PreviewStep()
        msg = mock_message(text="")
        assert step.validate(msg, ctx) is not None


# ══════════════════════════════════════════════════════════════════════════════
# 4. FILE MANAGEMENT — ADD / REMOVE / EDIT
# ══════════════════════════════════════════════════════════════════════════════

class TestFileManagement:
    @pytest.mark.asyncio
    async def test_file_remove(self):
        f1 = make_parsed_file(original_filename="a.mkv")
        f2 = make_parsed_file(original_filename="b.mkv")
        ctx = make_context(files=[f1, f2], _preview_edit_mode="files", _preview_file_index=0)
        step = PreviewStep()
        cb = mock_callback()
        from app.core import CallbackAction
        await step.handle_callback(None, cb, CallbackAction.FILE_REMOVE, ["0"], ctx)
        assert len(ctx.files) == 1
        assert ctx.files[0].original_filename == "b.mkv"

    @pytest.mark.asyncio
    async def test_file_remove_last(self):
        f1 = make_parsed_file(original_filename="a.mkv")
        ctx = make_context(files=[f1], _preview_edit_mode="files", _preview_file_index=0)
        step = PreviewStep()
        cb = mock_callback()
        from app.core import CallbackAction
        await step.handle_callback(None, cb, CallbackAction.FILE_REMOVE, ["0"], ctx)
        assert len(ctx.files) == 0

    @pytest.mark.asyncio
    async def test_file_select_opens_detail(self):
        ctx = make_context(_preview_edit_mode="files")
        step = PreviewStep()
        cb = mock_callback()
        from app.core import CallbackAction
        await step.handle_callback(None, cb, CallbackAction.FILE_SELECT, ["0"], ctx)
        assert ctx._preview_file_index == 0

    @pytest.mark.asyncio
    async def test_manage_files_add_mode(self):
        ctx = make_context(_preview_edit_mode="files", _preview_file_index=None)
        step = PreviewStep()
        cb = mock_callback()
        from app.core import CallbackAction
        await step.handle_callback(None, cb, CallbackAction.MANAGE_FILES, [], ctx)
        assert ctx._preview_edit_mode == "add_files"

    @pytest.mark.asyncio
    async def test_add_files_back_to_file_list(self):
        ctx = make_context(_preview_edit_mode="add_files")
        step = PreviewStep()
        cb = mock_callback()
        from app.core import CallbackAction
        await step.handle_callback(None, cb, CallbackAction.BACK_TO_PREVIEW, [], ctx)
        assert ctx._preview_edit_mode == "files"

    def test_add_file_via_message(self):
        ctx = make_context(_preview_edit_mode="add_files", files=[])
        step = PreviewStep()
        msg = mock_message(document=True)
        assert step.validate(msg, ctx) is None
        step.process(msg, ctx)
        assert len(ctx.files) == 1
        assert ctx.files[0].file_id == "doc123"

    def test_add_files_continue_returns_to_file_list(self):
        ctx = make_context(_preview_edit_mode="add_files")
        step = PreviewStep()
        result = step.on_continue(ctx)
        assert result is None
        assert ctx._preview_edit_mode == "files"

    @pytest.mark.asyncio
    async def test_file_detail_quality_select(self):
        f = make_parsed_file(quality="720p", languages=["Hindi"])
        ctx = make_context(files=[f], _preview_edit_mode="files", _preview_file_index=0)
        step = PreviewStep()
        cb = mock_callback()
        from app.core import CallbackAction
        await step.handle_callback(None, cb, CallbackAction.QUALITY_SELECT, ["4K"], ctx)
        assert ctx.files[0].quality == "4K"

    @pytest.mark.asyncio
    async def test_file_detail_language_select(self):
        f = make_parsed_file(quality="1080p", languages=["Hindi"])
        ctx = make_context(files=[f], _preview_edit_mode="files", _preview_file_index=0)
        step = PreviewStep()
        cb = mock_callback()
        from app.core import CallbackAction
        await step.handle_callback(None, cb, CallbackAction.LANGUAGE_SELECT, ["Tamil"], ctx)
        assert ctx.files[0].languages == ["Tamil"]

    @pytest.mark.asyncio
    async def test_file_detail_use_original_filename(self):
        f = make_parsed_file(original_filename="My.Raw.File.mkv")
        assert f.use_original_filename is False
        ctx = make_context(files=[f], _preview_edit_mode="files", _preview_file_index=0)
        step = PreviewStep()
        cb = mock_callback()
        from app.core import CallbackAction
        await step.handle_callback(None, cb, CallbackAction.USE_ORIGINAL, ["0"], ctx)
        assert ctx.files[0].use_original_filename is True
        assert ctx.files[0].display_name == "My.Raw.File.mkv"

    @pytest.mark.asyncio
    async def test_back_to_preview_clears_edit_state(self):
        ctx = make_context(_preview_edit_mode="menu", _preview_file_index=0)
        step = PreviewStep()
        cb = mock_callback()
        from app.core import CallbackAction
        await step.handle_callback(None, cb, CallbackAction.BACK_TO_PREVIEW, [], ctx)
        assert ctx._preview_edit_mode is None
        assert ctx._preview_file_index is None


# ══════════════════════════════════════════════════════════════════════════════
# 5. SAVE DRAFT & PUBLISH — VALIDATION
# ══════════════════════════════════════════════════════════════════════════════

class TestSaveDraftPublishValidation:
    @pytest.mark.asyncio
    async def test_validate_before_save_missing_title(self):
        ctx = make_context(title=None)
        session = _make_session(ctx)
        err = await session._validate_before_save()
        assert err is not None
        assert "title" in err.lower()

    @pytest.mark.asyncio
    async def test_validate_before_save_missing_year(self):
        ctx = make_context(year=None)
        session = _make_session(ctx)
        err = await session._validate_before_save()
        assert err is not None
        assert "year" in err.lower()

    @pytest.mark.asyncio
    async def test_validate_before_save_missing_files(self):
        ctx = make_context(files=[])
        session = _make_session(ctx)
        err = await session._validate_before_save()
        assert err is not None
        assert "file" in err.lower()

    @pytest.mark.asyncio
    async def test_validate_before_save_ok(self):
        ctx = make_context()
        session = _make_session(ctx)
        err = await session._validate_before_save()
        assert err is None


def _make_session(ctx: UploadContext | None = None):
    from app.wizard.base import WizardSession
    if ctx is None:
        ctx = make_context()
    session = WizardSession(
        user_id=12345,
        chat_id=-100123,
        wizard_name="upload",
        steps=[],
        context_factory=UploadContext,
        title="Test",
    )
    session.context = ctx
    return session


@pytest.mark.asyncio
async def test_save_draft_calls_service():
    ctx = make_context()
    session = _make_session(ctx)
    cb = mock_callback()

    with patch("app.core.container.container") as mock_container:
        mock_container.upload_service.save_draft = AsyncMock(return_value={
            "movie_id": "MH000042",
            "title": "Test Movie",
        })
        mock_container.config_service.get_bot_name = AsyncMock(return_value="MovieHub")
        mock_container.admin_service = MagicMock()

        result = await session._save_and_cleanup(None, cb, "draft")
        assert result is True
        mock_container.upload_service.save_draft.assert_called_once_with(
            title=ctx.title,
            year=ctx.year,
            poster_file_id=ctx.poster_file_id,
            files=ctx.files,
            created_by=12345,
        )


@pytest.mark.asyncio
async def test_publish_calls_service():
    ctx = make_context()
    session = _make_session(ctx)
    cb = mock_callback()

    with patch("app.core.container.container") as mock_container:
        mock_container.upload_service.duplicate_check = AsyncMock(return_value=False)
        mock_container.upload_service.publish_movie = AsyncMock(return_value={
            "movie_id": "MH000043",
            "title": "Test Movie",
        })
        mock_container.config_service.get_bot_name = AsyncMock(return_value="MovieHub")
        mock_container.admin_service = MagicMock()

        result = await session._save_and_cleanup(None, cb, "public")
        assert result is True
        mock_container.upload_service.publish_movie.assert_called_once_with(
            title=ctx.title,
            year=ctx.year,
            poster_file_id=ctx.poster_file_id,
            files=ctx.files,
            created_by=12345,
        )


@pytest.mark.asyncio
async def test_publish_duplicate_detected():
    ctx = make_context(title="Duplicate", year=2023)
    session = _make_session(ctx)
    cb = mock_callback()

    with patch("app.core.container.container") as mock_container:
        mock_container.upload_service.duplicate_check = AsyncMock(return_value=True)
        mock_container.config_service.get_bot_name = AsyncMock(return_value="MovieHub")
        mock_container.admin_service = MagicMock()

        result = await session._save_and_cleanup(None, cb, "public")
        assert result is True
        mock_container.upload_service.publish_movie.assert_not_called()
        cb.edit_message_text.assert_called_once()


# ══════════════════════════════════════════════════════════════════════════════
# 6. CANCEL — CLEANUP
# ══════════════════════════════════════════════════════════════════════════════

class TestCancelCleanup:
    def test_cleanup_removes_state_and_session(self):
        from app.wizard.base import wizard_manager

        session = _make_session()
        wizard_manager._sessions[12345] = session
        assert wizard_manager.get_active(12345) is not None
        session._cleanup()
        assert wizard_manager.get_active(12345) is None


# ══════════════════════════════════════════════════════════════════════════════
# 7. UPLOAD SERVICE TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestUploadService:
    @pytest.mark.asyncio
    async def test_save_draft_creates_movie_and_files(self):
        mock_movie_repo = MagicMock()
        mock_movie_repo.count = AsyncMock(return_value=41)
        mock_movie_repo.insert_one = AsyncMock(return_value="inserted_id")

        mock_file_repo = MagicMock()
        mock_file_repo.insert_many = AsyncMock(return_value=["fid1"])

        from app.services.upload_service import UploadService
        svc = UploadService(
            movie_repo=mock_movie_repo,
            movie_file_repo=mock_file_repo,
        )

        files = [make_parsed_file()]
        result = await svc.save_draft(
            title="Test Movie",
            year=2023,
            poster_file_id="poster123",
            files=files,
            created_by=12345,
        )

        assert result["title"] == "Test Movie"
        assert result["year"] == 2023
        assert result["status"] == "draft"
        assert result["movie_id"] == "MH000042"
        assert result["poster_file_id"] == "poster123"
        mock_movie_repo.insert_one.assert_called_once()
        mock_file_repo.insert_many.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_creates_movie_and_files(self):
        mock_movie_repo = MagicMock()
        mock_movie_repo.count = AsyncMock(return_value=42)
        mock_movie_repo.insert_one = AsyncMock(return_value="inserted_id")

        mock_file_repo = MagicMock()
        mock_file_repo.insert_many = AsyncMock(return_value=["fid1"])

        from app.services.upload_service import UploadService
        svc = UploadService(
            movie_repo=mock_movie_repo,
            movie_file_repo=mock_file_repo,
        )

        files = [make_parsed_file()]
        result = await svc.publish_movie(
            title="Test Movie",
            year=2023,
            poster_file_id=None,
            files=files,
            created_by=12345,
        )

        assert result["status"] == "public"
        assert result["poster_file_id"] is None

    @pytest.mark.asyncio
    async def test_duplicate_check_true(self):
        mock_movie_repo = MagicMock()
        mock_movie_repo.exists = AsyncMock(return_value=True)

        from app.services.upload_service import UploadService
        svc = UploadService(
            movie_repo=mock_movie_repo,
            movie_file_repo=MagicMock(),
        )

        is_dup = await svc.duplicate_check("Test Movie", 2023)
        assert is_dup is True
        mock_movie_repo.exists.assert_called_once_with(
            {"normalized_title": "test movie", "year": 2023}
        )

    @pytest.mark.asyncio
    async def test_duplicate_check_false(self):
        mock_movie_repo = MagicMock()
        mock_movie_repo.exists = AsyncMock(return_value=False)

        from app.services.upload_service import UploadService
        svc = UploadService(
            movie_repo=mock_movie_repo,
            movie_file_repo=MagicMock(),
        )

        is_dup = await svc.duplicate_check("New Movie", 2024)
        assert is_dup is False

    @pytest.mark.asyncio
    async def test_find_duplicate_returns_doc(self):
        mock_movie_repo = MagicMock()
        mock_movie_repo.find_many = AsyncMock(return_value=[{"movie_id": "MH000001"}])

        from app.services.upload_service import UploadService
        svc = UploadService(
            movie_repo=mock_movie_repo,
            movie_file_repo=MagicMock(),
        )

        doc = await svc.find_duplicate("Test Movie", 2023)
        assert doc is not None
        assert doc["movie_id"] == "MH000001"

    @pytest.mark.asyncio
    async def test_find_duplicate_returns_none(self):
        mock_movie_repo = MagicMock()
        mock_movie_repo.find_many = AsyncMock(return_value=[])

        from app.services.upload_service import UploadService
        svc = UploadService(
            movie_repo=mock_movie_repo,
            movie_file_repo=MagicMock(),
        )

        doc = await svc.find_duplicate("New Movie", 2024)
        assert doc is None


# ══════════════════════════════════════════════════════════════════════════════
# 8. UTILITY FUNCTION TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestUtilityFunctions:
    def test_format_size_bytes(self):
        assert _format_size(500) == "500 B"

    def test_format_size_kb(self):
        assert _format_size(2048) == "2.0 KB"

    def test_format_size_mb(self):
        assert _format_size(5 * 1024 * 1024) == "5.0 MB"

    def test_format_size_gb(self):
        assert _format_size(2 * 1024 * 1024 * 1024) == "2.00 GB"

    def test_truncate_name_short(self):
        assert _truncate_name("short.mkv", 20) == "short.mkv"

    def test_truncate_name_long(self):
        result = _truncate_name("very_long_movie_file_name.mkv", 20)
        assert len(result) == 20
        assert result.endswith("...")

    def test_rebuild_display_name_uses_display(self):
        f = make_parsed_file()
        result = _rebuild_display_name(f)
        assert result == f.display_name

    def test_rebuild_display_name_uses_original(self):
        f = make_parsed_file(use_original_filename=True, original_filename="raw.mkv")
        result = _rebuild_display_name(f)
        assert result == "raw.mkv"
