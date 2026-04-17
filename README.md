# Wisp

A lightweight client agent that enables Ruby server to execute commands on user machines.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Environment Variables (Recommended)

```bash
export WISP_SERVER=ws://ruby.example.com
export WISP_USER_ID=your_user_id
export WISP_TOKEN=your_jwt_token
wisp
```

### Optional Settings

```bash
export WISP_DEVICE_NAME="My MacBook Pro"  # Custom device name
export WISP_DEVICE_ID="macbook-001"        # Custom device ID (auto-generated if not set)
```

### Command Line Arguments

You can also override settings via command line:

```bash
wisp --server ws://ruby.example.com --user-id your_user_id --token your_token
```

## Features

- **File Operations**: Read and write files on the client machine
- **Shell Commands**: Execute shell commands
- **Auto Reconnect**: Automatically reconnects when disconnected
- **Multiple Devices**: One user can run multiple Wisp instances on different devices

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
{"type": "register", "device_id": "xxx", "device_name": "xxx", "capabilities": ["read_file", "write_file", "shell"]}
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
