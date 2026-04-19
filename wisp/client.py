"""
Wisp WebSocket Client
Handles connection to Ruby server and command execution
"""

import asyncio
import json
import logging
from wisp import config
import os
import platform
import uuid
import websockets
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class WispClient:
    """WebSocket client for connecting to Ruby server"""
    
    def __init__(
        self,
        server_url: str,
        wisp_id: Optional[str] = None,
        wisp_name: Optional[str] = None,
        auto_reconnect: bool = True,
        reconnect_interval: int = 10,
    ):
        self.server_url = server_url.rstrip("/")
        self.user_id = config.user_id()
        self.token = config.user_token()
        self.wisp_id = wisp_id or self._generate_wisp_id()
        self.wisp_name = wisp_name or self._get_default_wisp_name()
        self.auto_reconnect = auto_reconnect
        self.reconnect_interval = reconnect_interval
        with open('information.txt', 'r', encoding='utf-8') as f:
            self.information = f.read()

        
        self.ws = None
        self.connected = False
        self._command_handlers = {}
        
    def _generate_wisp_id(self) -> str:
        """Generate a unique wisp ID based on platform and uuid"""
        return f"{platform.system().lower()}-{uuid.getnode():012x}"
    
    def _get_default_wisp_name(self) -> str:
        """Get a default wisp name based on platform"""
        system = platform.system()
        if system == "Darwin":
            return f"Mac {platform.node()}"
        elif system == "Linux":
            return f"Linux {platform.node()}"
        elif system == "Windows":
            return f"Windows {platform.node()}"
        return f"{system} {platform.node()}"
    
    async def connect(self) -> bool:
        """Connect to Ruby server"""
        try:
            url = f"{self.server_url}/ws/wisp/{self.user_id}?token={self.token}"
            logger.info(f"Connecting to {url}")
            
            self.ws = await websockets.connect(url)
            
            # Send registration message
            await self.ws.send(json.dumps({
                "type": "register",
                "wisp_id": self.wisp_id,
                "wisp_name": self.wisp_name,
                "information": self.information,
            }))
            
            # Wait for acknowledgment
            response = await self.ws.recv()
            data = json.loads(response)
            
            if data.get("type") == "connected":
                self.connected = True
                logger.info(f"Connected as {data.get('message')}")
                return True
            else:
                logger.error(f"Connection failed: {data}")
                await self.ws.close()
                return False
                
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from Ruby server"""
        self.connected = False
        if self.ws:
            await self.ws.close()
            self.ws = None
        logger.info("Disconnected from server")
    
    async def listen(self):
        """Listen for commands from Ruby server"""
        while self.connected:
            try:
                message = await self.ws.recv()
                data = json.loads(message)
                
                if data.get("type") == "execute":
                    await self._handle_command(data)
                else:
                    logger.warning(f"Unknown message type: {data.get('type')}")
                    
            except websockets.exceptions.ConnectionClosed:
                logger.warning("Connection closed by server")
                self.connected = False
                break
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
    
    async def _handle_command(self, command: dict):
        """Handle incoming command from Ruby"""
        cmd_type = command.get("command")
        message_id = command.get("message_id")
        print(command)
        
        try:
            if cmd_type == "read_file":
                result = await self._execute_read_file(command.get('args'))
            elif cmd_type == "write_file":
                result = await self._execute_write_file(command.get('args'))
            elif cmd_type == "shell":
                result = await self._execute_shell(command.get('args'))
            else:
                result = {"success": False, "result": f"Unknown command: {cmd_type}"}
            print(result)
            
            # Send result back
            result_str = result.get("result")
            if not result_str:
                result_str = result.get("stdout", 'Empty stdout') if result.get("success", False) else result.get("stderr", 'execute command failed with empty stderr')
            response = {
                "type": "result",
                "message_id": message_id,
                "command": cmd_type,
                "success": result.get("success", False),
                "result": result_str,
            }
            
            await self.ws.send(json.dumps(response))
            
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            await self.ws.send(json.dumps({
                "type": "error",
                "message_id": message_id,
                "command": cmd_type,
                "error": str(e),
            }))
            print(e)
    
    async def _execute_read_file(self, command: dict) -> dict:
        """Read file from local filesystem"""
        from wisp.commands.file_ops import read_file
        path = command.get("path")
        if not path:
            return {"success": False, "result": "Missing path parameter"}
        return await read_file(path)
    
    async def _execute_write_file(self, command: dict) -> dict:
        """Write file to local filesystem"""
        from wisp.commands.file_ops import write_file
        path = command.get("path")
        content = command.get("content", "")
        if not path:
            return {"success": False, "result": "Missing path parameter"}
        return await write_file(path, content)
    
    async def _execute_shell(self, command: dict) -> dict:
        """Execute shell command"""
        from wisp.commands.shell import run_command
        cmd = command.get("cmd")
        if not cmd:
            return {"success": False, "result": "Missing cmd parameter"}
        return await run_command(cmd)
    
    async def run(self):
        """Main run loop with auto-reconnect"""
        while True:
            if self.auto_reconnect:
                success = await self.connect()
                if not success:
                    logger.info(f"Retrying in {self.reconnect_interval} seconds...")
                    await asyncio.sleep(self.reconnect_interval)
                    continue
                
                await self.listen()
                
                if self.auto_reconnect:
                    logger.info(f"Reconnecting in {self.reconnect_interval} seconds...")
                    await asyncio.sleep(self.reconnect_interval)
                else:
                    break
            else:
                await self.connect()
                await self.listen()
                break
