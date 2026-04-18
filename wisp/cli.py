#!/usr/bin/env python3
"""
Wisp CLI - Command line interface for Wisp client
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
    wisp
"""
    )
    
    parser.add_argument(
        "--server", "-s",
        default='wss://ruby.rongxianzhuo.com',
        help="Ruby WebSocket server URL"
    )
    
    parser.add_argument(
        "--wisp-name",
        default='My Computer',
        help="Custom wisp name (e.g., 'My MacBook Pro')"
    )
    
    parser.add_argument(
        "--no-auto-reconnect",
        action="store_true",
        help="Disable auto-reconnect on disconnect"
    )
    
    parser.add_argument(
        "--reconnect-interval",
        type=int,
        default=10,
        help="Seconds to wait before reconnecting (default: 10)"
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
    
    # Create client
    client = WispClient(
        server_url=args.server,
        wisp_id='',
        wisp_name=args.wisp_name,
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
