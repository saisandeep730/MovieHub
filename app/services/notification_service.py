from logging import getLogger
from typing import Callable, Coroutine

logger = getLogger(__name__)

NotifySender = Callable[[int, str], Coroutine[None, None, None]]


class NotificationService:
    """Queues and dispatches notifications to users and admins.

    The actual Telegram sending is delegated to a sender callback
    injected by the application layer to keep this service Telegram-free.
    """

    def __init__(self, sender: NotifySender | None = None) -> None:
        self._sender = sender

    def set_sender(self, sender: NotifySender) -> None:
        self._sender = sender

    async def notify_user(self, user_id: int, message: str) -> None:
        if self._sender:
            await self._sender(user_id, message)
        else:
            logger.info("Notification queued for user %d: %s", user_id, message)

    async def notify_admins(self, message: str, admin_ids: list[int]) -> None:
        for admin_id in admin_ids:
            await self.notify_user(admin_id, message)

    async def send_log(self, message: str, log_channel_id: int) -> None:
        logger.info("Log to channel %d: %s", log_channel_id, message)
