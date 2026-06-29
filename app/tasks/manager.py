from __future__ import annotations

import asyncio
import uuid
from logging import getLogger
from typing import Any, Callable, Coroutine

logger = getLogger(__name__)


class ScheduledTask:
    """Represents a scheduled task with metadata."""

    def __init__(
        self,
        task_id: str,
        user_id: int | None,
        coro: Coroutine[Any, Any, None],
        delay: float | None = None,
    ) -> None:
        self.task_id = task_id
        self.user_id = user_id
        self._coro = coro
        self._delay = delay
        self._task: asyncio.Task[Any] | None = None
        self._cancelled = False

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled

    def cancel(self) -> None:
        self._cancelled = True
        if self._task and not self._task.done():
            self._task.cancel()


class TaskManager:
    """Centralized async scheduler for delayed and recurring operations."""

    def __init__(self) -> None:
        self._tasks: dict[str, ScheduledTask] = {}

    async def schedule_task(
        self,
        coro: Coroutine[Any, Any, None],
        delay: float = 0,
        user_id: int | None = None,
        task_id: str | None = None,
    ) -> str:
        tid = task_id or uuid.uuid4().hex[:12]
        scheduled = ScheduledTask(tid, user_id, coro, delay)

        async def _runner() -> None:
            try:
                if delay > 0:
                    await asyncio.sleep(delay)
                if not scheduled.is_cancelled:
                    await coro
            except asyncio.CancelledError:
                pass
            except Exception:
                logger.exception("Task %s failed", tid)

        scheduled._task = asyncio.create_task(_runner())
        self._tasks[tid] = scheduled
        logger.debug("Task %s scheduled (delay=%s)", tid, delay)
        return tid

    def cancel_task(self, task_id: str) -> None:
        task = self._tasks.pop(task_id, None)
        if task:
            task.cancel()
            logger.debug("Task %s cancelled", task_id)

    def cancel_all_for_user(self, user_id: int) -> None:
        to_cancel = [tid for tid, t in self._tasks.items() if t.user_id == user_id]
        for tid in to_cancel:
            self.cancel_task(tid)
        logger.debug("Cancelled %d tasks for user %d", len(to_cancel), user_id)

    def cleanup_finished(self) -> None:
        finished = [tid for tid, t in self._tasks.items() if t._task and t._task.done()]
        for tid in finished:
            self._tasks.pop(tid, None)
        logger.debug("Cleaned up %d finished tasks", len(finished))

    @property
    def active_count(self) -> int:
        return len(self._tasks)

    def clear_all(self) -> None:
        for tid in list(self._tasks.keys()):
            self.cancel_task(tid)


task_manager = TaskManager()
