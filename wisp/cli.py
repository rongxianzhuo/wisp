#!/usr/bin/env python3
"""
Wisp CLI - Command line interface for Wisp client

Usage:
    # From environment variables (recommended)
    export WISP_SERVER=ws://ruby.example.com
    export WISP_USER_ID=xxx
    export WISP_TOKEN=yyy
    wisp

    # Or from command line arguments
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


def get_env_or_arg(env_var: str, arg_value, required: bool = True):
    """Get value from environment variable or command line argument"""
    env_value = os.environ.get(env_var)
    if env_value:
        return env_value
    if arg_value is not None:
        return arg_value
    if required:
        raise ValueError(f"Missing required value: set {env_var} environment variable or provide --{env_var.lower().replace('_', '-')}")
    return None


def parse_args():
    parser = argparse.ArgumentParser(
        description="Wisp - Client agent for Ruby",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Using environment variables (recommended)
    export WISP_SERVER=ws://ruby.example.com
    export WISP_USER_ID=user123
    export WISP_TOKEN=abc123
    wisp

    # Using command line arguments
    wisp --server ws://ruby.example.com --user-id user123 --token abc123
    
    # Mix: environment variables for sensitive data, args for options
    export WISP_SERVER=ws://ruby.example.com
    export WISP_USER_ID=user123
    export WISP_TOKEN=abc123
    wisp --device-name "My MacBook" --verbose
        """
    )
    
    parser.add_argument(
        "--server", "-s",
        help="Ruby WebSocket server URL (e.g., ws://ruby.example.com)"
    )
    
    parser.add_argument(
        "--user-id", "-u",
        help="User ID for authentication"
    )
    
    parser.add_argument(
        "--token", "-t",
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


async def async_main():
    args = parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    # Get credentials from environment variables or command line arguments
    server = get_env_or_arg("WISP_SERVER", args.server)
    user_id = get_env_or_arg("WISP_USER_ID", args.user_id)
    token = get_env_or_arg("WISP_TOKEN", args.token)
    
    # Optional settings from environment variables
    device_id = os.environ.get("WISP_DEVICE_ID") or args.device_id
    device_name = os.environ.get("WISP_DEVICE_NAME") or args.device_name
    
    # Show which values came from environment vs arguments
    logger.info(f"Starting Wisp v{__version__}")
    logger.info(f"Server: {server}")
    logger.info(f"User ID: {user_id}")
    logger.info(f"Device: {device_name or 'auto-generated'}")
    logger.info(f"Capabilities: {args.capabilities}")
    
    # Create client
    client = WispClient(
        server_url=server,
        user_id=user_id,
        token=token,
        device_id=device_id,
        device_name=device_name,
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
