"""
Shell command execution for Wisp
Provides ability to run shell commands
"""

import asyncio
import os


async def run_command(cmd: str, timeout: int = 600) -> dict:
    """
    Execute shell command
    
    Args:
        cmd: Command to execute
        timeout: Timeout in seconds (default 30)
    
    Returns:
        dict with success status, stdout, stderr, and return code
    """
    try:
        # Use shell=True for complex commands, but sanitize input
        # For MVP, we trust the commands from Ruby server
        
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=os.path.expanduser('~')
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds"
            }
        
        return {
            "success": process.returncode == 0,
            "returncode": process.returncode,
            "stdout": stdout.decode('utf-8', errors='replace'),
            "stderr": stderr.decode('utf-8', errors='replace'),
        }
        
    except Exception as e:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e)
        }
