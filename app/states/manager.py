from __future__ import annotations

from typing import Any

StateKey = tuple[int, int | None]  # (user_id, chat_id or None for private)


class StateManager:
    """In-memory per-user conversation state management for multi-step workflows."""

    def __init__(self) -> None:
        self._states: dict[StateKey, dict[str, Any]] = {}

    def _key(self, user_id: int, chat_id: int | None = None) -> StateKey:
        return (user_id, chat_id)

    def set_state(self, user_id: int, state: str, chat_id: int | None = None) -> None:
        key = self._key(user_id, chat_id)
        if key not in self._states:
            self._states[key] = {"state": None, "data": {}}
        self._states[key]["state"] = state

    def get_state(self, user_id: int, chat_id: int | None = None) -> str | None:
        key = self._key(user_id, chat_id)
        entry = self._states.get(key)
        return entry["state"] if entry else None

    def clear_state(self, user_id: int, chat_id: int | None = None) -> None:
        key = self._key(user_id, chat_id)
        self._states.pop(key, None)

    def update_data(self, user_id: int, data: dict[str, Any], chat_id: int | None = None) -> None:
        key = self._key(user_id, chat_id)
        if key not in self._states:
            self._states[key] = {"state": None, "data": {}}
        self._states[key]["data"].update(data)

    def get_data(self, user_id: int, chat_id: int | None = None) -> dict[str, Any]:
        key = self._key(user_id, chat_id)
        entry = self._states.get(key)
        return entry["data"] if entry else {}

    def get_full(self, user_id: int, chat_id: int | None = None) -> dict[str, Any] | None:
        return self._states.get(self._key(user_id, chat_id))

    def clear_all(self) -> None:
        self._states.clear()


state_manager = StateManager()
