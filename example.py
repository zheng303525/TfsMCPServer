#!/usr/bin/env python3
"""
Example usage of TFS MCP Server.

This script demonstrates how to use the TFS MCP Server programmatically.
"""

import asyncio
from tfs_mcp_server import TFSMcpServer


def main() -> None:
    """Main example function."""
    print("TFS MCP Server Example")
    print("=" * 50)
    
    # Create the server with custom configuration
    server = TFSMcpServer(
        name="Example TFS Server",
        tf_exe_path="tf.exe",  # Adjust path as needed
        default_working_directory=r"C:\Source\MyProject"  # Adjust as needed
    )
    
    print(f"Server created: {server.mcp.name}")
    print("Available tools:")
    
    # List all available tools
    for tool in server.mcp._tools:
        print(f"  - {tool.name}: {tool.description}")
    
    print("\nAvailable resources:")
    
    # List all available resources
    for resource in server.mcp._resources:
        print(f"  - {resource.uri_template}")
    
    print("\nStarting server...")
    print("Use Ctrl+C to stop the server")
    
    try:
        # Run the server
        server.run(transport="stdio")
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    main() 