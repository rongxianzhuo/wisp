"""
File operations for Wisp
Provides read and write capabilities for local filesystem
"""

import aiofiles
import aiofiles.os
import os
from pathlib import Path


async def read_file(path: str, max_size: int = 1024 * 1024) -> dict:
    """
    Read file from local filesystem
    
    Args:
        path: Path to the file
        max_size: Maximum file size to read (default 1MB)
    
    Returns:
        dict with success status and data/error
    """
    try:
        # Security: check if path exists
        if not await aiofiles.os.path.exists(path):
            return {"success": False, "error": f"File not found: {path}"}
        
        # Security: check if it's a file (not directory)
        if not await aiofiles.os.path.isfile(path):
            return {"success": False, "error": f"Not a file: {path}"}
        
        # Security: check file size
        stat = await aiofiles.os.stat(path)
        if stat.st_size > max_size:
            return {
                "success": False, 
                "error": f"File too large: {stat.st_size} bytes (max {max_size})"
            }
        
        # Read file
        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        return {"success": True, "data": content}
        
    except PermissionError:
        return {"success": False, "error": f"Permission denied: {path}"}
    except UnicodeDecodeError:
        return {"success": False, "error": f"Cannot decode file as text: {path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def write_file(path: str, content: str) -> dict:
    """
    Write content to local filesystem
    
    Args:
        path: Path to write to
        content: Content to write
    
    Returns:
        dict with success status and data/error
    """
    try:
        # Create parent directories if they don't exist
        parent = Path(path).parent
        parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        async with aiofiles.open(path, 'w', encoding='utf-8') as f:
            await f.write(content)
        
        return {"success": True, "data": f"File written: {path}"}
        
    except PermissionError:
        return {"success": False, "error": f"Permission denied: {path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
