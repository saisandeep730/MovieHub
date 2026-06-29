from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from app.core import CallbackAction, encode


@dataclass
class Page:
    items: list[dict[str, Any]]
    page: int
    total_pages: int
    total_items: int
    has_next: bool = False
    has_prev: bool = False
    page_size: int = 10


@dataclass
class Pagination:
    """Generic pagination helper for inline keyboard navigation."""

    collection: str = ""
    items: list[dict[str, Any]] = field(default_factory=list)
    page: int = 1
    page_size: int = 10
    total: int = 0

    @property
    def total_pages(self) -> int:
        return max(1, math.ceil(self.total / self.page_size))

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def start_index(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def end_index(self) -> int:
        return min(self.start_index + self.page_size, self.total)

    @property
    def current_items(self) -> list[dict[str, Any]]:
        return self.items[self.start_index:self.end_index]

    def to_page(self) -> Page:
        return Page(
            items=self.current_items,
            page=self.page,
            total_pages=self.total_pages,
            total_items=self.total,
            has_next=self.has_next,
            has_prev=self.has_prev,
            page_size=self.page_size,
        )

    def navigation_buttons(self, detail_action: CallbackAction | None = None) -> list[dict[str, str]]:
        buttons: list[dict[str, str]] = []
        if self.has_prev:
            buttons.append(
                {"text": "◀️ Prev", "callback_data": encode(CallbackAction.PAGE_PREV, self.collection, str(self.page - 1))}
            )
        buttons.append(
            {"text": f"{self.page}/{self.total_pages}", "callback_data": encode(CallbackAction.PAGE_GOTO, self.collection, str(self.page))}
        )
        if self.has_next:
            buttons.append(
                {"text": "Next ▶️", "callback_data": encode(CallbackAction.PAGE_NEXT, self.collection, str(self.page + 1))}
            )
        return buttons
