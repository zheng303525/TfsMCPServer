"""Main entry point for TFS MCP Server."""

import argparse
import os
import sys
from typing import Optional

from .server import TFSMcpServer


def main() -> None:
    """Main entry point for the TFS MCP Server."""
    parser = argparse.ArgumentParser(
        description="TFS MCP Server - A FastMCP server for Team Foundation Server operations"
    )
    
    parser.add_argument(
        "--name",
        type=str,
        default="TFS MCP Server",
        help="Server name (default: 'TFS MCP Server')"
    )
    
    parser.add_argument(
        "--tf-exe-path",
        type=str,
        default=None,
        help="Path to tf.exe executable (default: assumes it's in PATH)"
    )
    
    parser.add_argument(
        "--working-directory",
        type=str,
        default=None,
        help="Default working directory for TFS operations (default: current directory)"
    )
    
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "http", "sse"],
        default="stdio",
        help="Transport protocol (default: stdio)"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address for http/sse transport (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number for http/sse transport (default: 8000)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="TFS MCP Server 0.1.0"
    )
    
    args = parser.parse_args()
    
    try:
        # Create and run the server
        server = TFSMcpServer(
            name=args.name,
            tf_exe_path=args.tf_exe_path,
            default_working_directory=args.working_directory
        )
        
        print(f"Starting {args.name}...")
        print(f"Transport: {args.transport}")
        if args.transport in ["http", "sse"]:
            print(f"Address: {args.host}:{args.port}")
        
        server.run(
            transport=args.transport,
            host=args.host,
            port=args.port
        )
        
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 