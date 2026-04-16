# Wisp

A lightweight client agent that enables Ruby server to execute commands on user machines.

## Features

- **File Operations**: Read and write files on the client machine
- **Shell Commands**: Execute shell commands
- **Auto Reconnect**: Automatically reconnects when disconnected
- **Multiple Devices**: One user can run multiple Wisp instances on different devices

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python -m wisp.cli --server ws://ruby.example.com --user-id your_user_id --token your_token
```

### Options

| Option | Description |
|--------|-------------|
| `--server`, `-s` | Ruby WebSocket server URL |
| `--user-id`, `-u` | User ID for authentication |
| `--token`, `-t` | JWT token for authentication |
| `--device-id` | Custom device ID (auto-generated if not provided) |
| `--device-name` | Custom device name |
| `--capabilities` | Capabilities to advertise (default: read_file write_file shell) |
| `--no-auto-reconnect` | Disable auto-reconnect |
| `--reconnect-interval` | Seconds between reconnection attempts (default: 5) |
| `--verbose`, `-v` | Enable verbose logging |

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
