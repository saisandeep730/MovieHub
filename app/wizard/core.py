from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from pyrogram.types import InlineKeyboardMarkup, Message


@dataclass
class WizardContext:
    pass


class WizardStep(ABC):
    step_number: int = 0
    title: str = ""
    field_name: str = ""
    optional: bool = False
    collects_multiple: bool = False

    @abstractmethod
    def render_prompt(self, context: WizardContext) -> str:
        ...

    def render_summary_value(self, context: WizardContext) -> str | None:
        return None

    @abstractmethod
    def validate(self, message: Message, context: WizardContext) -> str | None:
        ...

    @abstractmethod
    def process(self, message: Message, context: WizardContext) -> None:
        ...

    def get_keyboard(
        self,
        has_back: bool = False,
        has_skip: bool = False,
        has_continue: bool = False,
        context: WizardContext | None = None,
    ) -> InlineKeyboardMarkup:
        from app.wizard.navigation import wizard_nav_keyboard
        return wizard_nav_keyboard(
            has_back=has_back,
            has_skip=has_skip,
            has_continue=has_continue,
        )

    def on_skip(self, context: WizardContext) -> None:
        pass

    def on_continue(self, context: WizardContext) -> str | None:
        """Return None to advance. Return '' to stay silently.
        Return a non-empty string to stay and show that error."""
        return None
