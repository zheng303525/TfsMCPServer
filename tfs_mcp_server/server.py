"""TFS MCP Server implementation."""

from typing import Dict, List, Optional, Any, Union, Literal
import json
import os
from pathlib import Path

from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

from .tfs_client import TFSClient
from .types import (
    TFSCommandResult,
    TFSFileStatus,
    TFSWorkspaceInfo,
    TFSCheckoutOptions,
    TFSCheckinOptions,
    TFSBranchInfo,
    TFSMergeOptions,
    TFSHistoryOptions,
)


class TFSMcpServer:
    """TFS MCP Server for Team Foundation Server operations."""

    def __init__(
        self, 
        name: str = "TFS MCP Server",
        tf_exe_path: Optional[str] = None,
        default_working_directory: Optional[str] = None
    ) -> None:
        """Initialize TFS MCP Server.
        
        Args:
            name: Server name.
            tf_exe_path: Path to tf.exe executable.
            default_working_directory: Default working directory.
        """
        self.mcp = FastMCP(name)
        self.tfs_client = TFSClient(tf_exe_path, default_working_directory)
        self._register_tools()
        self._register_resources()

    def _register_tools(self) -> None:
        """Register TFS tools with the MCP server."""
        
        @self.mcp.tool
        async def tf_checkout(
            ctx: Context,
            paths: List[str],
            lock_type: Optional[str] = None,
            recursive: bool = False,
            file_type: Optional[str] = None,
            working_directory: Optional[str] = None
        ) -> Dict[str, Any]:
            """Checkout files from TFS for editing.
            
            Args:
                paths: List of file or folder paths to checkout
                lock_type: Lock type (none, checkin, checkout)
                recursive: Recursively checkout files in folders
                file_type: File type specification
                working_directory: Working directory for path resolution (if not provided, uses server default)
                ctx: MCP context
                
            Returns:
                Dictionary containing operation result
            """
            await ctx.info(f"Checking out {len(paths)} path(s)...")
            
            # Create a temporary client with the specified working directory if provided
            client = self.tfs_client
            if working_directory:
                client = TFSClient(self.tfs_client.tf_exe_path, working_directory)
            
            options = TFSCheckoutOptions(
                paths=paths,
                lock_type=lock_type,
                recursive=recursive,
                type=file_type
            )
            
            result = await client.checkout_files(options)
            
            if result.success:
                await ctx.info(f"Successfully checked out files: {result.output}")
            else:
                await ctx.error(f"Checkout failed: {result.error}")
            
            return {
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "command": result.command
            }

        @self.mcp.tool
        async def tf_checkin(
            ctx: Context,
            paths: List[str],
            comment: str,
            recursive: bool = False,
            associate: Optional[List[int]] = None,
            resolve: Optional[List[int]] = None,
            override_reason: Optional[str] = None,
            working_directory: Optional[str] = None
        ) -> Dict[str, Any]:
            """Checkin files to TFS.
            
            Args:
                paths: List of file or folder paths to checkin
                comment: Checkin comment (required)
                recursive: Recursively checkin files in folders
                associate: Work item IDs to associate with this checkin
                resolve: Work item IDs to resolve with this checkin  
                override_reason: Reason for overriding policy failures
                working_directory: Working directory for path resolution (if not provided, uses server default)
                ctx: MCP context
                
            Returns:
                Dictionary containing operation result
            """
            await ctx.info(f"Checking in {len(paths)} path(s) with comment: {comment}")
            
            # Create a temporary client with the specified working directory if provided
            client = self.tfs_client
            if working_directory:
                client = TFSClient(self.tfs_client.tf_exe_path, working_directory)
            
            options = TFSCheckinOptions(
                paths=paths,
                comment=comment,
                recursive=recursive,
                associate=associate,
                resolve=resolve,
                override=override_reason
            )
            
            result = await client.checkin_files(options)
            
            if result.success:
                await ctx.info(f"Successfully checked in files: {result.output}")
            else:
                await ctx.error(f"Checkin failed: {result.error}")
            
            return {
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "command": result.command
            }

        @self.mcp.tool
        async def tf_add(
            ctx: Context,
            paths: List[str],
            recursive: bool = False,
            working_directory: Optional[str] = None
        ) -> Dict[str, Any]:
            """Add files to TFS source control.
            
            Args:
                paths: List of file or folder paths to add
                recursive: Recursively add files in folders
                working_directory: Working directory for path resolution (if not provided, uses server default)
                ctx: MCP context
                
            Returns:
                Dictionary containing operation result
            """
            await ctx.info(f"Adding {len(paths)} path(s) to TFS...")
            
            # Create a temporary client with the specified working directory if provided
            client = self.tfs_client
            if working_directory:
                client = TFSClient(self.tfs_client.tf_exe_path, working_directory)
            
            result = await client.add_files(paths, recursive)
            
            if result.success:
                await ctx.info(f"Successfully added files: {result.output}")
            else:
                await ctx.error(f"Add failed: {result.error}")
            
            return {
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "command": result.command
            }

        @self.mcp.tool
        async def tf_delete(
            ctx: Context,
            paths: List[str],
            recursive: bool = False,
            working_directory: Optional[str] = None
        ) -> Dict[str, Any]:
            """Delete files from TFS source control.
            
            Args:
                paths: List of file or folder paths to delete
                recursive: Recursively delete files in folders
                working_directory: Working directory for path resolution (if not provided, uses server default)
                ctx: MCP context
                
            Returns:
                Dictionary containing operation result
            """
            await ctx.info(f"Deleting {len(paths)} path(s) from TFS...")
            
            # Create a temporary client with the specified working directory if provided
            client = self.tfs_client
            if working_directory:
                client = TFSClient(self.tfs_client.tf_exe_path, working_directory)
            
            result = await client.delete_files(paths, recursive)
            
            if result.success:
                await ctx.info(f"Successfully deleted files: {result.output}")
            else:
                await ctx.error(f"Delete failed: {result.error}")
            
            return {
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "command": result.command
            }

        @self.mcp.tool
        async def tf_rename(
            ctx: Context,
            old_path: str,
            new_path: str,
            working_directory: Optional[str] = None
        ) -> Dict[str, Any]:
            """Rename a file in TFS source control.
            
            Args:
                old_path: Current path of the file
                new_path: New path for the file
                working_directory: Working directory for path resolution (if not provided, uses server default)
                ctx: MCP context
                
            Returns:
                Dictionary containing operation result
            """
            await ctx.info(f"Renaming '{old_path}' to '{new_path}'...")
            
            # Create a temporary client with the specified working directory if provided
            client = self.tfs_client
            if working_directory:
                client = TFSClient(self.tfs_client.tf_exe_path, working_directory)
            
            result = await client.rename_file(old_path, new_path)
            
            if result.success:
                await ctx.info(f"Successfully renamed file: {result.output}")
            else:
                await ctx.error(f"Rename failed: {result.error}")
            
            return {
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "command": result.command
            }

        @self.mcp.tool
        async def tf_undo(
            ctx: Context,
            paths: List[str],
            recursive: bool = False,
            working_directory: Optional[str] = None
        ) -> Dict[str, Any]:
            """Undo pending changes in TFS.
            
            Args:
                paths: List of file or folder paths to undo changes for
                recursive: Recursively undo changes in folders
                working_directory: Working directory for path resolution (if not provided, uses server default)
                ctx: MCP context
                
            Returns:
                Dictionary containing operation result
            """
            await ctx.info(f"Undoing changes for {len(paths)} path(s)...")
            
            # Create a temporary client with the specified working directory if provided
            client = self.tfs_client
            if working_directory:
                client = TFSClient(self.tfs_client.tf_exe_path, working_directory)
            
            result = await client.undo_changes(paths, recursive)
            
            if result.success:
                await ctx.info(f"Successfully undid changes: {result.output}")
            else:
                await ctx.error(f"Undo failed: {result.error}")
            
            return {
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "command": result.command
            }

        @self.mcp.tool
        async def tf_status(
            ctx: Context,
            paths: Optional[List[str]] = None,
            recursive: bool = False,
            working_directory: Optional[str] = None
        ) -> Dict[str, Any]:
            """Get status of files in TFS.
            
            Args:
                paths: List of paths to check status for (defaults to current directory)
                recursive: Recursively check status in folders
                working_directory: Working directory for path resolution (if not provided, uses server default)
                ctx: MCP context
                
            Returns:
                Dictionary containing status information
            """
            path_info = f" for {len(paths)} path(s)" if paths else " for current directory"
            await ctx.info(f"Getting TFS status{path_info}...")
            
            # Create a temporary client with the specified working directory if provided
            client = self.tfs_client
            if working_directory:
                client = TFSClient(self.tfs_client.tf_exe_path, working_directory)
            
            result = await client.get_status(paths, recursive)
            
            if result.success:
                await ctx.info("Successfully retrieved status information")
            else:
                await ctx.error(f"Status check failed: {result.error}")
            
            return {
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "command": result.command
            }

        @self.mcp.tool
        async def tf_get_latest(
            ctx: Context,
            paths: Optional[List[str]] = None,
            recursive: bool = False,
            force: bool = False,
            working_directory: Optional[str] = None
        ) -> Dict[str, Any]:
            """Get latest version of files from TFS.
            
            Args:
                paths: List of paths to get latest for (defaults to current directory)
                recursive: Recursively get latest in folders
                force: Force overwrite local changes
                working_directory: Working directory for path resolution (if not provided, uses server default)
                ctx: MCP context
                
            Returns:
                Dictionary containing operation result
            """
            path_info = f" for {len(paths)} path(s)" if paths else " for current directory"
            await ctx.info(f"Getting latest version{path_info}...")
            
            # Create a temporary client with the specified working directory if provided
            client = self.tfs_client
            if working_directory:
                client = TFSClient(self.tfs_client.tf_exe_path, working_directory)
            
            result = await client.get_latest(paths, recursive, force)
            
            if result.success:
                await ctx.info(f"Successfully retrieved latest version: {result.output}")
            else:
                await ctx.error(f"Get latest failed: {result.error}")
            
            return {
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "command": result.command
            }

        @self.mcp.tool
        async def tf_branch(
            ctx: Context,
            source_path: str,
            target_path: str,
            version: Optional[str] = None
        ) -> Dict[str, Any]:
            """Create a branch in TFS.
            
            Args:
                source_path: Source path to branch from
                target_path: Target path for the new branch
                version: Version specification (optional)
                ctx: MCP context
                
            Returns:
                Dictionary containing operation result
            """
            await ctx.info(f"Creating branch from '{source_path}' to '{target_path}'...")
            
            branch_info = TFSBranchInfo(
                source_path=source_path,
                target_path=target_path,
                version=version
            )
            
            result = await self.tfs_client.create_branch(branch_info)
            
            if result.success:
                await ctx.info(f"Successfully created branch: {result.output}")
            else:
                await ctx.error(f"Branch creation failed: {result.error}")
            
            return {
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "command": result.command
            }

        @self.mcp.tool
        async def tf_merge(
            ctx: Context,
            source: str,
            target: str,
            version: Optional[str] = None,
            recursive: bool = False,
            discard: bool = False,
            baseless: bool = False
        ) -> Dict[str, Any]:
            """Merge files in TFS.
            
            Args:
                source: Source path or branch to merge from
                target: Target path to merge to
                version: Version specification (optional)
                recursive: Recursively merge folders
                discard: Discard changes instead of merging
                baseless: Perform baseless merge
                ctx: MCP context
                
            Returns:
                Dictionary containing operation result
            """
            await ctx.info(f"Merging from '{source}' to '{target}'...")
            
            options = TFSMergeOptions(
                source=source,
                target=target,
                version=version,
                recursive=recursive,
                discard=discard,
                baseless=baseless
            )
            
            result = await self.tfs_client.merge_files(options)
            
            if result.success:
                await ctx.info(f"Successfully merged: {result.output}")
            else:
                await ctx.error(f"Merge failed: {result.error}")
            
            return {
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "command": result.command
            }

        @self.mcp.tool
        async def tf_history(
            ctx: Context,
            path: str,
            recursive: bool = False,
            stopafter: Optional[int] = None,
            version: Optional[str] = None,
            user: Optional[str] = None
        ) -> Dict[str, Any]:
            """Get history of a file or folder in TFS.
            
            Args:
                path: Path to get history for
                recursive: Recursively get history for folders
                stopafter: Maximum number of changes to return
                version: Version range specification
                user: Filter by specific user
                ctx: MCP context
                
            Returns:
                Dictionary containing history information
            """
            await ctx.info(f"Getting history for '{path}'...")
            
            options = TFSHistoryOptions(
                path=path,
                recursive=recursive,
                stopafter=stopafter,
                version=version,
                user=user
            )
            
            result = await self.tfs_client.get_history(options)
            
            if result.success:
                await ctx.info(f"Successfully retrieved history: {len(result.output.splitlines())} entries")
            else:
                await ctx.error(f"History retrieval failed: {result.error}")
            
            return {
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "command": result.command
            }

    def _register_resources(self) -> None:
        """Register TFS resources with the MCP server."""
        
        @self.mcp.resource("tfs://workspace/info")
        async def get_workspace_info() -> str:
            """Get current TFS workspace information.
            
            Returns:
                JSON string containing workspace information.
            """
            try:
                workspace_info = await self.tfs_client.get_workspace_info()
                return json.dumps(workspace_info.model_dump(), indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        @self.mcp.resource("tfs://status/{path}")
        async def get_path_status(path: str) -> str:
            """Get TFS status for a specific path.
            
            Args:
                path: Path to check status for.
                
            Returns:
                JSON string containing status information.
            """
            try:
                # Note: Path normalization is handled in TFSClient.get_status()
                result = await self.tfs_client.get_status([path], recursive=False)
                return json.dumps({
                    "path": path,
                    "success": result.success,
                    "output": result.output,
                    "error": result.error
                }, indent=2)
            except Exception as e:
                return json.dumps({"path": path, "error": str(e)}, indent=2)

    def run(
        self, 
        transport: Literal["stdio", "http", "sse", "streamable-http"] = "stdio", 
        host: str = "127.0.0.1", 
        port: int = 8000,
        **kwargs: Any
    ) -> None:
        """Run the TFS MCP server.
        
        Args:
            transport: Transport type (stdio, http, sse)
            host: Host address for http/sse transport
            port: Port number for http/sse transport
            **kwargs: Additional arguments for the server
        """
        if transport == "stdio":
            # stdio transport doesn't accept host/port parameters
            self.mcp.run(transport=transport, **kwargs)
        else:
            # http/sse transports need host/port parameters
            self.mcp.run(transport=transport, host=host, port=port, **kwargs) 