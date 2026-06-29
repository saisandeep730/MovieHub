from logging import getLogger

from pyrogram import Client, filters
from pyrogram.handlers import CallbackQueryHandler, MessageHandler
from pyrogram import idle

from app.config import settings
from app.core import plugin_manager
from app.database import db_manager
from app.events import BotStartedEvent, BotStoppedEvent, event_bus
from app.handlers import callback_handlers, start_handlers, upload_handlers
from app.logging import setup_logging
from app.tasks import task_manager

logger = getLogger(__name__)


class BotApplication:
    """Main bot application that manages lifecycle and dependencies."""

    def __init__(self) -> None:
        self.client: Client = Client(
            name="moviehub",
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
            bot_token=settings.BOT_TOKEN,
            in_memory=True,
        )
        self._register_handlers()

    def _register_handlers(self) -> None:
        for handler_fn, handler_filter in start_handlers:
            self.client.add_handler(MessageHandler(handler_fn, handler_filter))
        for handler_fn, _ in callback_handlers:
            self.client.add_handler(CallbackQueryHandler(handler_fn))
        for handler_fn, handler_filter in upload_handlers:
            self.client.add_handler(MessageHandler(handler_fn, handler_filter))

    async def startup(self) -> None:
        """Initialize all dependencies and start the bot."""
        setup_logging()
        logger.info("Bot startup — initializing dependencies")
        await db_manager.startup()
        await plugin_manager.startup()
        await event_bus.publish(BotStartedEvent())
        logger.info("Bot dependencies ready")

    async def shutdown(self) -> None:
        """Clean up all resources gracefully."""
        logger.info("Bot shutdown — cleaning up")
        await event_bus.publish(BotStoppedEvent())
        await plugin_manager.shutdown()
        task_manager.clear_all()
        await db_manager.shutdown()
        logger.info("Bot shutdown complete")

    async def run(self) -> None:
        """Start the bot with full lifecycle management."""
        try:
            await self.startup()
            await self.client.start()
            logger.info("Bot is running")
            await idle()
        except Exception:
            logger.exception("Fatal bot error")
            raise
        finally:
            await self.client.stop()
            await self.shutdown()
