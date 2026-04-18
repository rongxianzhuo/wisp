#!/usr/bin/env python3
"""
Wisp CLI - Command line interface for Wisp client

Usage:
    wisp --server ws://ruby.example.com --user-id xxx --token yyy
"""

import argparse
import asyncio
import logging
import os
import sys

from wisp import __version__
from wisp.client import WispClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Wisp - Client agent for Ruby",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Using command line arguments
    wisp --server ws://ruby.example.com --user-id user123 --token abc123
"""
    )
    
    parser.add_argument(
        "--server", "-s",
        default='ws://127.0.0.1:5003',
        help="Ruby WebSocket server URL (e.g., ws://ruby.example.com)"
    )
    
    parser.add_argument(
        "--user-id", "-u",
        default='user',
        help="User ID for authentication"
    )
    
    parser.add_argument(
        "--token", "-t",
        default='none',
        help="JWT token for authentication"
    )
    
    parser.add_argument(
        "--wisp-name",
        default='My Computer',
        help="Custom wisp name (e.g., 'My MacBook Pro')"
    )
    
    parser.add_argument(
        "--capabilities",
        nargs="+",
        default=["read_file", "write_file", "shell"],
        help="Capabilities to advertise (default: read_file write_file shell)"
    )
    
    parser.add_argument(
        "--no-auto-reconnect",
        action="store_true",
        help="Disable auto-reconnect on disconnect"
    )
    
    parser.add_argument(
        "--reconnect-interval",
        type=int,
        default=5,
        help="Seconds to wait before reconnecting (default: 5)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--version", "-V",
        action="version",
        version=f"Wisp {__version__}"
    )
    
    return parser.parse_args()


async def async_main():
    args = parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    # Show which values came from environment vs arguments
    logger.info(f"Starting Wisp v{__version__}")
    logger.info(f"Server: {args.server}")
    logger.info(f"User ID: {args.user_id}")
    logger.info(f"Wisp: {args.wisp_name or 'auto-generated'}")
    logger.info(f"Capabilities: {args.capabilities}")
    
    # Create client
    client = WispClient(
        server_url=args.server,
        user_id=args.user_id,
        token=args.token,
        wisp_id='',
        wisp_name=args.wisp_name,
        capabilities=args.capabilities,
        auto_reconnect=not args.no_auto_reconnect,
        reconnect_interval=args.reconnect_interval,
    )
    
    try:
        # Run client
        await client.run()
    except KeyboardInterrupt:
        logger.info("Received interrupt, shutting down...")
        await client.disconnect()
        sys.exit(0)
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)


def main():
    """Entry point that handles both asyncio and non-asyncio Python versions"""
    try:
        # Try Python 3.7+ approach
        asyncio.run(async_main())
    except AttributeError:
        # Fallback for older Python versions
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(async_main())
        finally:
            loop.close()


if __name__ == "__main__":
    main()
