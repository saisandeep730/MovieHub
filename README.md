# MovieHub

A production-ready Telegram Movie Storage & Distribution Bot.

## Folder Structure

```
moviehub/
├── app/
│   ├── bot/            # Bot application and lifecycle
│   ├── cache/          # Caching layer
│   ├── config/         # Pydantic Settings configuration
│   ├── database/       # MongoDB manager and base repository
│   ├── filters/        # Telegram message filters
│   ├── handlers/       # Telegram update handlers
│   ├── keyboards/      # Inline keyboard builders
│   ├── logging/        # Centralized logging with rotation
│   ├── middlewares/    # Pyrogram middlewares
│   ├── models/         # Pydantic data models
│   ├── repositories/   # Data access repositories
│   ├── server/         # FastAPI redirect server
│   ├── services/       # Business logic layer
│   └── utils/          # Constants, helpers, validators, exceptions
├── logs/               # Rotating log files
├── run_bot.py          # Telegram Bot entry point
├── run_server.py       # Redirect Server entry point
├── .env                # Environment secrets
├── .env.example        # Environment template
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Requirements

- Python 3.12+
- MongoDB Atlas (or local MongoDB)

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/moviehub.git
cd moviehub

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

## Environment Variables

| Variable           | Description                    | Required |
|--------------------|--------------------------------|----------|
| `BOT_TOKEN`        | Telegram Bot Token             | Yes      |
| `API_ID`           | Telegram API ID                | Yes      |
| `API_HASH`         | Telegram API Hash              | Yes      |
| `MONGODB_URI`      | MongoDB connection string      | Yes      |
| `DATABASE_NAME`    | MongoDB database name          | No       |
| `ADMIN_IDS`        | Comma-separated admin user IDs | Yes      |
| `DB_CHANNEL_ID`    | Telegram database channel ID   | Yes      |
| `LOG_CHANNEL_ID`   | Telegram log channel ID        | Yes      |
| `BACKUP_CHANNEL_ID`| Telegram backup channel ID     | Yes      |
| `PORT`             | Redirect server port           | No       |
| `HOST`             | Redirect server host           | No       |
| `LOG_LEVEL`        | Logging level                  | No       |

## Running

### Telegram Bot

```bash
python run_bot.py
```

### Redirect Server (FastAPI)

```bash
python run_server.py
```

## Tech Stack

- Python 3.12+
- Pyrogram (Telegram client)
- Motor (async MongoDB driver)
- FastAPI + Uvicorn (redirect server)
- Pydantic Settings (configuration)
- MongoDB Atlas
