from __future__ import annotations

from logging import getLogger
from typing import Any

from pyrogram.types import CallbackQuery, Message

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

        if self.is_last_step:
            await self._complete(client)
            return

        self.current_step += 1
        await self.render_current(client)
        await callback.answer()

    async def handle_edit(self, client: object, callback: CallbackQuery) -> None:
        await callback.answer("Edit coming soon")
        logger.debug("Edit requested for wizard %s by user %d", self.wizard_name, self.user_id)

    async def handle_save_draft(self, client: object, callback: CallbackQuery) -> None:
        await callback.answer("Save Draft coming soon")
        logger.debug("Save Draft requested for wizard %s by user %d", self.wizard_name, self.user_id)

    async def handle_publish(self, client: object, callback: CallbackQuery) -> None:
        await callback.answer("Publish coming soon")
        logger.debug("Publish requested for wizard %s by user %d", self.wizard_name, self.user_id)

    async def handle_cancel(self, client: object, callback: CallbackQuery) -> None:
        state_manager.clear_state(self.user_id, self.chat_id)
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

    async def _complete(self, client: object) -> None:
        state_manager.clear_state(self.user_id, self.chat_id)
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
