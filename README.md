# Wisp

A lightweight client agent that enables Ruby server to execute commands on user machines.

## Installation

```bash
# Clone the repository
git clone git@github.com:rongxianzhuo/wisp.git
cd wisp

# Install in development mode (recommended)
pip install -e .
```

## Usage

### Environment Variables

Set the following environment variables:

```bash
# Required
export WISP_SERVER=ws://ruby.example.com
export WISP_USER_ID=your_user_id
export WISP_TOKEN=your_jwt_token

# Optional
export WISP_DEVICE_NAME="My MacBook Pro"  # Custom wisp name
export WISP_DEVICE_ID="macbook-001"       # Custom wisp ID
```

On Windows (PowerShell):
```powershell
$env:WISP_SERVER="ws://ruby.example.com"
$env:WISP_USER_ID="your_user_id"
$env:WISP_TOKEN="your_jwt_token"
```

### Run Wisp

```bash
wisp
```

## Features

- **File Operations**: Read and write files on the client machine
- **Shell Commands**: Execute shell commands
- **Auto Reconnect**: Automatically reconnects when disconnected
- **Multiple Wisps**: One user can run multiple Wisp instances on different wisps

## How It Works

```
User ←→ Ruby (Server) ←→ Wisp (Client)
                    ↓
              Send commands
                    ↓
              Wisp executes
                    ↓
              Return results
```

1. Wisp connects to Ruby server via WebSocket
2. Wisp authenticates with user_id and token
3. Wisp registers its capabilities
4. Ruby can now send commands to Wisp
5. Wisp executes commands locally and returns results

## Protocol

### Registration

```json
{"type": "register", "wisp_id": "xxx", "wisp_name": "xxx", "capabilities": ["read_file", "write_file", "shell"]}
```

### Ruby → Wisp Commands

```json
{"type": "execute", "message_id": "xxx", "command": "read_file", "path": "/path/to/file"}
{"type": "execute", "message_id": "xxx", "command": "write_file", "path": "/path", "content": "..."}
{"type": "execute", "message_id": "xxx", "command": "shell", "cmd": "ls -la"}
```

### Wisp → Ruby Response

```json
{"type": "result", "message_id": "xxx", "command": "shell", "success": true, "data": "..."}
{"type": "error", "message_id": "xxx", "error": "Permission denied"}
```

## License

MIT
