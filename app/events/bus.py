from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from logging import getLogger
from typing import Any, Callable, Coroutine

logger = getLogger(__name__)

EventHandler = Callable[..., Coroutine[Any, Any, None]]


@dataclass
class Event:
    """Base event for the pub/sub system."""


@dataclass
class MovieUploadedEvent(Event):
    movie_id: str
    title: str
    year: int
    created_by: int
    status: str


@dataclass
class DraftSavedEvent(Event):
    movie_id: str
    title: str
    year: int
    created_by: int


@dataclass
class MovieDownloadedEvent(Event):
    movie_id: str
    user_id: int
    file_unique_id: str


@dataclass
class MovieRequestedEvent(Event):
    movie_name: str
    user_id: int


@dataclass
class BroadcastCompletedEvent(Event):
    broadcast_id: str
    total_users: int
    success_count: int
    fail_count: int


@dataclass
class BackupCompletedEvent(Event):
    backup_id: str
    type_: str


@dataclass
class BotStartedEvent(Event):
    """Published after all startup tasks complete."""


@dataclass
class BotStoppedEvent(Event):
    """Published before shutdown tasks begin."""


class EventBus:
    """Async publish-subscribe event bus with typed events."""

    def __init__(self) -> None:
        self._subscribers: dict[type[Event], list[EventHandler]] = {}

    def subscribe(self, event_type: type[Event], handler: EventHandler) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.debug("Handler subscribed to %s", event_type.__name__)

    def unsubscribe(self, event_type: type[Event], handler: EventHandler) -> None:
        handlers = self._subscribers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)
            logger.debug("Handler unsubscribed from %s", event_type.__name__)

    async def publish(self, event: Event) -> None:
        handlers = self._subscribers.get(type(event), [])
        if not handlers:
            return
        logger.debug("Publishing %s to %d handlers", type(event).__name__, len(handlers))
        results = await asyncio.gather(*[h(event) for h in handlers], return_exceptions=True)
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.exception("Handler %d failed for %s", i, type(event).__name__)

    def clear(self) -> None:
        self._subscribers.clear()


event_bus = EventBus()
