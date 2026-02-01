# Air Guitar Left Hand - Python Server

FastAPI-based server with WebSocket relay, ADB (Android Debug Bridge), and Room management support.

## Features

- **WebSocket Relay**: Message relay between PC and mobile devices
- **Room Management**: Room ID based connection system
  - Create rooms with expiration
  - Validate room IDs
  - Track sessions
- **ADB Server**: Android Debug Bridge API endpoints
  - Device list management
  - Port forwarding (forward/reverse)
  - Screen capture
  - Shell command execution
- **Database**: MySQL with SQLAlchemy + Alembic migrations
- **Health Check**: `/api/health` endpoint for monitoring
- **CORS Support**: Configured for mobile and web development

## Installation

```bash
# Install Python dependencies
pip install -r server/python/requirements.txt

# Install system dependencies (macOS)
brew install mysql android-platform-tools

# Install system dependencies (Linux)
sudo apt-get install mysql-server android-tools-adb

# Install system dependencies (Windows)
# MySQL: https://dev.mysql.com/downloads/mysql/
# ADB: https://developer.android.com/studio/releases/platform-tools
```

## Database Setup

### 1. Create Database

```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE air_guitar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Create user (optional)
CREATE USER 'airguitar'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON air_guitar.* TO 'airguitar'@'localhost';
FLUSH PRIVILEGES;
```

### 2. Configure Environment

Create `.env` file:

```bash
# Database
DATABASE_URL_SYNC=mysql+pymysql://root:password@localhost/air_guitar
DATABASE_URL=mysql+aiomysql://root:password@localhost/air_guitar

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=3000

# CORS
ALLOWED_ORIGINS=http://localhost:8081,http://localhost:19006,exp://192.168.*:*
```

### 3. Run Migrations

```bash
# Run database migrations
pnpm db:migrate

# Or with Python directly
python scripts/db_migrate.py migrate
```

### Migration Commands

```bash
pnpm db:migrate    # Run pending migrations
pnpm db:rollback   # Rollback last migration
pnpm db:current    # Show current version
pnpm db:history    # Show migration history
pnpm db:create     # Create new migration (autogenerate)
```

## Usage

### Start Server

```bash
source .venv/bin/activate
python scripts/run_server.py
```

Or with uvicorn:

```bash
uvicorn server.python.main:app --host 0.0.0.0 --port 3000 --reload
```

Then start Expo:

```bash
pnpm dev:metro
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `mysql+aiomysql://...` | Async database URL |
| `DATABASE_URL_SYNC` | `mysql+pymysql://...` | Sync database URL (Alembic) |
| `SERVER_HOST` | `0.0.0.0` | Host to bind to |
| `SERVER_PORT` | `3000` | Port to bind to |
| `ALLOWED_ORIGINS` | `http://localhost:8081,...` | CORS allowed origins |
| `LOG_LEVEL` | `info` | Logging level |
| `WS_PING_INTERVAL` | `20` | WebSocket ping interval (seconds) |
| `WS_PING_TIMEOUT` | `20` | WebSocket ping timeout (seconds) |

## API Endpoints

### HTTP

- `GET /` - Server information
- `GET /api/health` - Health check

### Room API

- `POST /api/rooms/create` - Create a new room
  - Body: `{"expires_in_hours": 24}`
- `GET /api/rooms/{room_id}` - Get room by ID
- `GET /api/rooms/{room_id}/validate` - Validate room ID

**Room Creation Example:**

```bash
curl -X POST http://localhost:3000/api/rooms/create \
  -H "Content-Type: application/json" \
  -d '{"expires_in_hours": 24}'

# Response:
{
  "id": 1,
  "room_id": "ABC123",
  "created_at": "2026-02-01T12:00:00",
  "expires_at": "2026-02-02T12:00:00"
}
```

**Validate Room Example:**

```bash
curl http://localhost:3000/api/rooms/ABC123/validate

# Response:
{
  "valid": true,
  "room_id": "ABC123",
  "message": "Room valid"
}
```

### ADB API

- `GET /api/adb/devices` - Get list of connected ADB devices
- `POST /api/adb/forward` - Set up port forwarding
  - Parameters: `device_id`, `local_port`, `remote_port`
- `POST /api/adb/reverse` - Set up reverse port forwarding
  - Parameters: `device_id`, `remote_port`, `local_port`
- `POST /api/adb/screen` - Capture device screen
  - Parameters: `device_id`
- `POST /api/adb/shell` - Execute shell command on device
  - Parameters: `device_id`, `command`

### WebSocket

- `WS /ws` - Main WebSocket endpoint for relay

## Database Schema

### rooms

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| room_id | VARCHAR(8) | Unique room ID |
| created_at | DATETIME | Creation time |
| expires_at | DATETIME | Expiration time (nullable) |

### sessions

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| room_id | VARCHAR(8) | Foreign key to rooms |
| client_id | VARCHAR(100) | Client identifier |
| client_type | VARCHAR(10) | "mobile" or "pc" |
| connected_at | DATETIME | Connection time |
| disconnected_at | DATETIME | Disconnection time (nullable) |

## Development

The server consists of:

- `main.py` - FastAPI application setup
- `database.py` - Database connection management
- `models/` - SQLAlchemy models
  - `room.py` - Room model
  - `session.py` - Session model
- `websocket.py` - WebSocket connection management
- `adb.py` - ADB command execution
- `config.py` - Configuration management

## ADB Setup

### Enable Developer Options on Android

1. Go to Settings → About Phone
2. Tap "Build Number" 7 times
3. Go back to Settings → Developer Options
4. Enable "USB Debugging"

### Connect Device via USB

```bash
# Check connected devices
adb devices

# Should see output like:
# List of devices attached
# XXXXXXXXXX    device
```

### Connect Device Wirelessly

```bash
# 1. Connect via USB first
adb devices

# 2. Enable TCP/IP on port 5555
adb tcpip 5555

# 3. Find device IP address
adb shell ip addr show wlan0

# 4. Connect wirelessly
adb connect 192.168.1.XXX:5555

# 5. Disconnect USB cable
```
