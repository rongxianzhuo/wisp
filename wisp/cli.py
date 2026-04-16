#!/usr/bin/env python3
"""
Wisp CLI - Command line interface for Wisp client

Usage:
    wisp --server ws://ruby.example.com --user-id xxx --token yyy
"""

import argparse
import asyncio
import logging
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
    wisp --server ws://ruby.example.com --user-id user123 --token abc123
    wisp --server ws://localhost:8000 --user-id user123 --token abc123 --device-name "My MacBook"
    wisp --server ws://ruby.example.com --user-id user123 --token abc123 --no-auto-reconnect
        """
    )
    
    parser.add_argument(
        "--server", "-s",
        required=True,
        help="Ruby WebSocket server URL (e.g., ws://ruby.example.com)"
    )
    
    parser.add_argument(
        "--user-id", "-u",
        required=True,
        help="User ID for authentication"
    )
    
    parser.add_argument(
        "--token", "-t",
        required=True,
        help="JWT token for authentication"
    )
    
    parser.add_argument(
        "--device-id",
        help="Custom device ID (auto-generated if not provided)"
    )
    
    parser.add_argument(
        "--device-name",
        help="Custom device name (e.g., 'My MacBook Pro')"
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


async def main():
    args = parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    logger.info(f"Starting Wisp v{__version__}")
    logger.info(f"Server: {args.server}")
    logger.info(f"User ID: {args.user_id}")
    logger.info(f"Capabilities: {args.capabilities}")
    
    # Create client
    client = WispClient(
        server_url=args.server,
        user_id=args.user_id,
        token=args.token,
        device_id=args.device_id,
        device_name=args.device_name,
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


if __name__ == "__main__":
    asyncio.run(main())
