from __future__ import annotations

from logging import getLogger
from typing import Any

from pyrogram.types import CallbackQuery, Message

from app.core import CallbackAction
from app.states import state_manager
from app.wizard.core import WizardContext, WizardStep
from app.wizard.message import delete_message_safe, edit_or_send
from app.wizard.renderer import render_wizard_screen

logger = getLogger(__name__)


class WizardSession:
    def __init__(
        self,
        user_id: int,
        chat_id: int,
        wizard_name: str,
        steps: list[WizardStep],
        context_factory: type[WizardContext],
        title: str,
    ) -> None:
        self.user_id = user_id
        self.chat_id = chat_id
        self.wizard_name = wizard_name
        self.steps = steps
        self.title = title

        total = len(steps)
        for i, step in enumerate(steps):
            step.step_number = i + 1

        self.current_step = 0
        self.context: WizardContext = context_factory()
        self.message_id: int | None = None
        self._state_key = f"wizard:{wizard_name}"

    @property
    def current(self) -> WizardStep:
        return self.steps[self.current_step]

    @property
    def is_last_step(self) -> bool:
        return self.current_step >= len(self.steps) - 1

    @property
    def has_back(self) -> bool:
        return self.current_step > 0

    @property
    def has_skip(self) -> bool:
        return self.current.optional

    @property
    def has_continue(self) -> bool:
        if self.current.collects_multiple:
            items = getattr(self.context, self.current.field_name, None)
            return bool(items)
        return False

    def _persist(self) -> None:
        state_manager.set_state(self.user_id, self._state_key, self.chat_id)
        state_manager.update_data(
            self.user_id,
            {
                "wizard_name": self.wizard_name,
                "current_step": self.current_step,
                "message_id": self.message_id,
                "context": self.context,
            },
            self.chat_id,
        )

    async def render_current(self, client: object, error: str | None = None) -> None:
        text = render_wizard_screen(
            title=self.title,
            step=self.current.step_number,
            total=len(self.steps),
            steps=self.steps,
            context=self.context,
            prompt=self.current.render_prompt(self.context),
            error=error,
        )
        keyboard = self.current.get_keyboard(
            has_back=self.has_back,
            has_skip=self.has_skip,
            has_continue=self.has_continue,
            context=self.context,
        )
        self.message_id = await edit_or_send(
            client=client,
            chat_id=self.chat_id,
            message_id=self.message_id,
            text=text,
            reply_markup=keyboard,
        )
        self._persist()

    async def _handle_input(self, client: object, message: Message) -> None:
        await delete_message_safe(client, self.chat_id, message.id)

        err = self.current.validate(message, self.context)
        if err is not None:
            await self.render_current(client, error=err)
            return

        self.current.process(message, self.context)

        if self.current.collects_multiple:
            await self.render_current(client)
            return

        if self.is_last_step:
            await self._complete(client)
            return

        self.current_step += 1
        await self.render_current(client)

    async def handle_message(self, client: object, message: Message) -> None:
        await self._handle_input(client, message)

    async def handle_media(self, client: object, message: Message) -> None:
        await self._handle_input(client, message)

    async def handle_skip(self, client: object, callback: CallbackQuery) -> None:
        self.current.on_skip(self.context)

        if self.is_last_step:
            await self._complete(client)
            return

        self.current_step += 1
        await self.render_current(client)
        await callback.answer()

    async def handle_back(self, client: object, callback: CallbackQuery) -> None:
        if self.current_step > 0:
            self.current_step -= 1
        await self.render_current(client)
        await callback.answer()

    async def handle_continue(self, client: object, callback: CallbackQuery) -> None:
        if self.current.collects_multiple:
            items = getattr(self.context, self.current.field_name, None)
            if not items:
                await self.render_current(client, error="Please add at least one file before continuing.")
                await callback.answer()
                return

        msg = self.current.on_continue(self.context)
        if msg is not None:
            await self.render_current(client, error=msg if msg else None)
            await callback.answer()
            return

        if self.is_last_step:
            await self._complete(client)
            return

        self.current_step += 1
        await self.render_current(client)
        await callback.answer()

    async def handle_step_callback(
        self, client: object, callback: CallbackQuery, action: object, args: list[str]
    ) -> None:
        handler = getattr(self.current, 'handle_callback', None)
        if handler:
            await handler(client, callback, action, args, self.context)
            self._persist()
            await self.render_current(client)
            await callback.answer()
        else:
            await callback.answer("Unknown action")

    async def handle_edit(self, client: object, callback: CallbackQuery) -> None:
        await callback.answer("Edit coming soon")
        logger.debug("Edit requested for wizard %s by user %d", self.wizard_name, self.user_id)

    async def _validate_before_save(self) -> str | None:
        from app.wizard.upload import UploadContext
        ctx = self.context
        if not isinstance(ctx, UploadContext):
            return "Invalid wizard context"
        if not ctx.title:
            return "Movie title is required."
        if not ctx.year:
            return "Release year is required."
        if not ctx.files:
            return "At least one file is required."
        return None

    async def _show_success(
        self,
        callback: CallbackQuery,
        status: str,
        movie: dict,
    ) -> None:
        from app.core.container import container
        from app.ui.keyboards import admin_dashboard_keyboard

        movie_id = movie.get("movie_id", "N/A")
        bot_name = await container.config_service.get_bot_name()
        mention = callback.from_user.mention
        merged = movie.get("_merged_files", 0)
        skipped = movie.get("_skipped_files", 0)
        extra = ""
        if merged:
            extra = f"\n\n{merged} new files added, {skipped} duplicates skipped."
        success_text = (
            f"\u2705 <b>Movie {status.title()}ed!</b>{extra}\n\n"
            f"Movie ID: <code>{movie_id}</code>"
        )
        await callback.edit_message_text(
            success_text,
            reply_markup=admin_dashboard_keyboard(bot_name, mention),
        )

    async def _show_duplicate_dialog(
        self,
        callback: CallbackQuery,
        dup: dict,
    ) -> None:
        from app.ui.keyboards import duplicate_dialog_keyboard

        ctx = self.context
        text = (
            f"\u26A0\uFE0F <b>Duplicate Detected</b>\n\n"
            f"A movie with the title <b>{ctx.title}</b> "
            f"and year <b>{ctx.year}</b> already exists.\n\n"
            f"<b>Existing:</b> <code>{dup.get('movie_id', 'N/A')}</code>\n"
            f"How would you like to proceed?"
        )
        await callback.edit_message_text(
            text,
            reply_markup=duplicate_dialog_keyboard(),
        )

    async def _save_and_cleanup(
        self,
        client: object,
        callback: CallbackQuery,
        status: str,
    ) -> bool:
        from app.core.container import container
        from app.wizard.upload import UploadContext, _truncate_name

        ctx = self.context
        if not isinstance(ctx, UploadContext):
            await callback.answer("Invalid context")
            return False

        err = await self._validate_before_save()
        if err:
            await self.render_current(client, error=err)
            await callback.answer()
            return False

        try:
            if status == "draft":
                movie = await container.upload_service.save_draft(
                    title=ctx.title,
                    year=ctx.year,
                    poster_file_id=ctx.poster_file_id,
                    files=ctx.files,
                    created_by=self.user_id,
                )
                self._cleanup()
                await self._show_success(callback, "draft", movie)
                await callback.answer()
                logger.info("Draft saved: %s by user %d", ctx.title, self.user_id)
                return True

            dup = await container.upload_service.find_duplicate(ctx.title, ctx.year)
            if dup:
                ctx._duplicate_movie = dup
                await self._show_duplicate_dialog(callback, dup)
                await callback.answer()
                return True

            movie = await container.upload_service.publish_movie(
                title=ctx.title,
                year=ctx.year,
                poster_file_id=ctx.poster_file_id,
                files=ctx.files,
                created_by=self.user_id,
            )
            self._cleanup()
            await self._show_success(callback, "publish", movie)
            await callback.answer()
            logger.info("Movie published: %s (%s) by user %d", ctx.title, movie.get("movie_id"), self.user_id)
            return True

        except Exception:
            logger.exception("Failed to save movie %s as %s", ctx.title, status)
            await self.render_current(
                client, error="\u274C An error occurred while saving. Please try again.",
            )
            await callback.answer()
            return False

    async def handle_duplicate_merge(self, client: object, callback: CallbackQuery) -> None:
        from app.core.container import container
        from app.wizard.upload import UploadContext

        ctx = self.context
        if not isinstance(ctx, UploadContext):
            await callback.answer("Invalid context")
            return

        dup = getattr(ctx, "_duplicate_movie", None)
        if not dup:
            await callback.answer("No duplicate data found")
            return

        try:
            movie = await container.upload_service.merge_movie(
                existing_movie=dup,
                new_files=ctx.files,
                updated_by=self.user_id,
            )
            self._cleanup()
            await self._show_success(callback, "merge", movie)
            await callback.answer()
        except Exception:
            logger.exception("Failed to merge movie")
            await callback.answer("\u274C Merge failed. Please try again.")

    async def handle_duplicate_replace(self, client: object, callback: CallbackQuery) -> None:
        from app.core.container import container
        from app.wizard.upload import UploadContext

        ctx = self.context
        if not isinstance(ctx, UploadContext):
            await callback.answer("Invalid context")
            return

        dup = getattr(ctx, "_duplicate_movie", None)
        if not dup:
            await callback.answer("No duplicate data found")
            return

        try:
            movie = await container.upload_service.replace_movie(
                existing_movie=dup,
                new_title=ctx.title,
                new_year=ctx.year,
                new_poster_file_id=ctx.poster_file_id,
                new_files=ctx.files,
                updated_by=self.user_id,
            )
            self._cleanup()
            await self._show_success(callback, "replace", movie)
            await callback.answer()
        except Exception:
            logger.exception("Failed to replace movie")
            await callback.answer("\u274C Replace failed. Please try again.")

    async def handle_save_draft(self, client: object, callback: CallbackQuery) -> None:
        await self._save_and_cleanup(client, callback, "draft")

    async def handle_publish(self, client: object, callback: CallbackQuery) -> None:
        await self._save_and_cleanup(client, callback, "public")

    async def handle_cancel(self, client: object, callback: CallbackQuery) -> None:
        self._cleanup()
        from app.ui.keyboards import admin_dashboard_keyboard
        from app.ui.messages import admin_dashboard
        from app.core.container import container

        bot_name = await container.config_service.get_bot_name()
        mention = callback.from_user.mention
        await callback.edit_message_text(
            admin_dashboard(bot_name, mention),
            reply_markup=admin_dashboard_keyboard(),
        )
        await callback.answer()
        logger.info("Wizard %s cancelled by user %d", self.wizard_name, self.user_id)

    def _cleanup(self) -> None:
        state_manager.clear_state(self.user_id, self.chat_id)
        from app.wizard import wizard_manager
        wizard_manager.remove(self.user_id)

    async def _complete(self, client: object) -> None:
        self._cleanup()
        logger.info(
            "Wizard %s completed by user %d — context: %s",
            self.wizard_name,
            self.user_id,
            self.context,
        )


class WizardManager:
    def __init__(self) -> None:
        self._sessions: dict[int, WizardSession] = {}

    def create(
        self,
        user_id: int,
        chat_id: int,
        wizard_name: str,
        steps: list[WizardStep],
        context_factory: type[WizardContext],
        title: str,
    ) -> WizardSession:
        session = WizardSession(
            user_id=user_id,
            chat_id=chat_id,
            wizard_name=wizard_name,
            steps=steps,
            context_factory=context_factory,
            title=title,
        )
        self._sessions[user_id] = session
        return session

    def get_active(self, user_id: int) -> WizardSession | None:
        return self._sessions.get(user_id)

    def remove(self, user_id: int) -> None:
        self._sessions.pop(user_id, None)


wizard_manager = WizardManager()
