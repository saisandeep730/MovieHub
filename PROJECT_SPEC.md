# MovieHub - Project Specification

## Vision

MovieHub is a professional Telegram Movie Storage & Distribution Bot.

The bot should be fully manageable from Telegram using buttons only. Administrators should never need to edit the source code after the initial deployment.

Movie files are stored in Telegram Database Channels.

Movie metadata and configuration are stored in MongoDB Atlas.

The system should be lightweight enough to run continuously on Android using Termux.

---

# V1 Features

## User Features

### Home

* Search Movie
* Latest Movies
* Request Movie
* Updates Channel
* Contact Admin
* About

---

### Search

Users search by movie name only.

The search should support partial matching.

Results display matching movies as inline buttons.

Selecting a movie opens its details page.

---

### Movie Details

Display:

* Poster
* Movie Name
* Release Year

Display every available file as an individual button.

Each button shows:

* Original filename
* File size

---

### Download

Flow:

1. Verify Force Subscribe
2. Send Join buttons if required
3. Verify membership
4. Deliver file
5. Send warning message
6. Show live countdown
7. Delete warning
8. Delete delivered file

Timer must be configurable.

---

### Movie Not Found

Display a friendly message.

Offer:

* Request Movie
* Search Again
* Home

---

### Movie Requests

Store requests.

Duplicate requests increase a counter.

Notify requesting users automatically after publication.

---

### Latest Movies

Display newest public movies.

Maximum count configurable.

---

## Permanent Links

Every movie receives a permanent Movie ID.

Example:

MH000001

External links should always use:

https://moviehub.in/m/{movie_id}

The redirect service should locate the active bot automatically.

Telegram links must never be shared directly.

---

# Admin Features

## Dashboard

Provide button-based access to:

* Upload
* Manage Movies
* Requests
* Broadcast
* Users
* Statistics
* Settings
* Backup
* Health

---

## Upload Workflow

Steps:

Movie Name

↓

Release Year

↓

Poster

↓

Forward all movie files

↓

Read Telegram File IDs

↓

Duplicate Detection

↓

Preview

↓

Draft or Public

↓

Publish

---

## Multi-file Movies

Support unlimited files.

Examples:

480p

720p

1080p

4K

Part 1

Part 2

Part 3

All files belong to one movie.

---

## Duplicate Detection

Use:

Movie Name + Release Year

Provide:

* Replace
* Merge
* Create Anyway
* Cancel

---

## Draft

Hidden from users.

No search.

No links.

No notifications.

No latest listing.

---

## Public

Visible everywhere.

Search enabled.

Permanent links active.

Auto-post enabled.

Notify requesters.

---

## Movie Management

Allow:

* Rename
* Change year
* Replace poster
* Add files
* Replace files
* Delete files
* Delete movie
* Change status
* Copy permanent link
* View statistics

---

## Broadcast

Support:

* Text
* Photo
* Video
* Document
* Forward
* Copy

Display progress while sending.

---

## Auto Post

Publishing a Public movie automatically posts to the Updates Channel.

Configurable template.

---

## Settings

Editable from Telegram.

Examples:

* Bot Name
* Messages
* Buttons
* Channels
* Admins
* Timers
* Templates
* Latest Movie Count

No restart required.

---

## Backup

Support:

* Export Settings
* Import Settings
* Full Backup
* Restore
* Scheduled Backup

Backups should be delivered to the Backup Channel.

---

## Health Dashboard

Display:

* Bot Status
* MongoDB Status
* Telegram Status
* Database Channel Status
* Redirect Server Status
* Last Backup
* Uptime
* Android Device Status

---

# Storage

Movie Files:
Telegram Database Channels

Metadata:
MongoDB Atlas

Logs:
Telegram Log Channel

Backups:
Telegram Backup Channel

---

# Redirect Server

FastAPI service.

Resolve permanent Movie IDs.

Redirect users to the active Telegram bot.

Changing the bot username must never invalidate existing MovieHub links.

---

# Technical Requirements

* Python 3.12+
* Async architecture
* Pyrogram
* Motor
* MongoDB Atlas
* FastAPI
* Pydantic
* Modular structure
* Type hints
* Structured logging
* Robust error handling

---

# Non-Goals (V1)

Do not implement:

* Download history
* Link analytics
* Categories
* Genres
* Search aliases
* Configuration profiles

These may be added in future versions.
