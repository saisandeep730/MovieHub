import asyncio
import sys

from app.bot import BotApplication


async def main() -> None:
    bot = BotApplication()
    await bot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        sys.exit(1)
