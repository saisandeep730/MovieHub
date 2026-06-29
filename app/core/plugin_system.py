from __future__ import annotations

from abc import ABC, abstractmethod
from logging import getLogger
from typing import Any

from app.events import Event

logger = getLogger(__name__)


class Plugin(ABC):
    """Base class for all MovieHub plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    async def on_startup(self) -> None:
        """Called when the bot starts."""

    async def on_shutdown(self) -> None:
        """Called when the bot shuts down."""

    async def on_event(self, event: Event) -> None:
        """Called for each event published on the event bus."""


class PluginManager:
    """Manages plugin registration and lifecycle hooks."""

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        if plugin.name in self._plugins:
            logger.warning("Plugin '%s' already registered, skipping", plugin.name)
            return
        self._plugins[plugin.name] = plugin
        logger.info("Plugin registered: %s", plugin.name)

    def unregister(self, name: str) -> None:
        self._plugins.pop(name, None)
        logger.info("Plugin unregistered: %s", name)

    def get(self, name: str) -> Plugin | None:
        return self._plugins.get(name)

    @property
    def all(self) -> list[Plugin]:
        return list(self._plugins.values())

    async def startup(self) -> None:
        for plugin in self._plugins.values():
            try:
                await plugin.on_startup()
            except Exception:
                logger.exception("Plugin '%s' on_startup failed", plugin.name)

    async def shutdown(self) -> None:
        for plugin in self._plugins.values():
            try:
                await plugin.on_shutdown()
            except Exception:
                logger.exception("Plugin '%s' on_shutdown failed", plugin.name)

    async def emit_event(self, event: Event) -> None:
        for plugin in self._plugins.values():
            try:
                await plugin.on_event(event)
            except Exception:
                logger.exception("Plugin '%s' on_event failed", plugin.name)

    def clear(self) -> None:
        self._plugins.clear()


plugin_manager = PluginManager()
