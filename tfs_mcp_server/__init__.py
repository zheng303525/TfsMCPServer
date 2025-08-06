"""TFS MCP Server - A FastMCP server for Team Foundation Server operations."""

__version__ = "0.1.0"
__author__ = "TFS MCP Server Team"
__description__ = "A FastMCP server for Team Foundation Server (TFS) operations"

from .server import TFSMcpServer
from .types import TFSCommandResult, TFSFileStatus, TFSWorkspaceInfo

__all__ = [
    "TFSMcpServer",
    "TFSCommandResult", 
    "TFSFileStatus",
    "TFSWorkspaceInfo",
] 