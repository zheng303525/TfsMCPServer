"""TFS client for executing TFS command line operations."""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Union
import asyncio

from .types import (
    TFSCommandResult,
    TFSFileInfo,
    TFSFileStatus,
    TFSWorkspaceInfo,
    TFSCheckoutOptions,
    TFSCheckinOptions,
    TFSBranchInfo,
    TFSMergeOptions,
    TFSHistoryOptions,
    TFSChangesetInfo,
)


class TFSClient:
    """Client for executing TFS command line operations."""

    def __init__(
        self, 
        tf_exe_path: Optional[str] = None, 
        working_directory: Optional[str] = None
    ) -> None:
        """Initialize TFS client.
        
        Args:
            tf_exe_path: Path to tf.exe. If None, assumes it's in PATH.
            working_directory: Default working directory for TFS operations.
        """
        self.tf_exe_path = tf_exe_path or "tf"
        self.working_directory = working_directory or os.getcwd()

    async def _execute_command(
        self, 
        command: List[str], 
        working_dir: Optional[str] = None
    ) -> TFSCommandResult:
        """Execute a TFS command asynchronously.
        
        Args:
            command: Command and arguments to execute.
            working_dir: Working directory for the command.
            
        Returns:
            Command execution result.
        """
        cmd = [self.tf_exe_path] + command
        work_dir = working_dir or self.working_directory
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=work_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout_bytes, stderr_bytes = await process.communicate()
            stdout = stdout_bytes.decode('utf-8') if stdout_bytes else ""
            stderr = stderr_bytes.decode('utf-8') if stderr_bytes else ""
            
            return TFSCommandResult(
                success=process.returncode == 0,
                output=stdout,
                error=stderr if process.returncode != 0 else None,
                return_code=process.returncode or 0,
                command=" ".join(cmd)
            )
            
        except Exception as e:
            return TFSCommandResult(
                success=False,
                output="",
                error=str(e),
                return_code=-1,
                command=" ".join(cmd)
            )

    async def get_workspace_info(self) -> TFSWorkspaceInfo:
        """Get information about the current workspace.
        
        Returns:
            Workspace information.
            
        Raises:
            Exception: If unable to get workspace information.
        """
        result = await self._execute_command(["workfold", "/collection"])
        
        if not result.success:
            raise Exception(f"Failed to get workspace info: {result.error}")
        
        # Parse workspace information from output
        # This is a simplified parsing - real implementation would be more robust
        lines = result.output.strip().split('\n')
        workspace_line = next((line for line in lines if "Workspace:" in line), "")
        owner_line = next((line for line in lines if "Owner:" in line), "")
        
        return TFSWorkspaceInfo(
            name=workspace_line.split(":")[-1].strip() if workspace_line else "Unknown",
            owner=owner_line.split(":")[-1].strip() if owner_line else "Unknown", 
            computer=os.environ.get("COMPUTERNAME", "Unknown"),
            comment=None,
            collection="Unknown",
            location="Local"
        )

    async def checkout_files(self, options: TFSCheckoutOptions) -> TFSCommandResult:
        """Checkout files from TFS.
        
        Args:
            options: Checkout options.
            
        Returns:
            Command execution result.
        """
        command = ["checkout"]
        
        if options.lock_type:
            command.extend(["/lock:" + options.lock_type])
        
        if options.recursive:
            command.append("/recursive")
            
        if options.type:
            command.extend(["/type:" + options.type])
            
        command.extend(options.paths)
        
        return await self._execute_command(command)

    async def checkin_files(self, options: TFSCheckinOptions) -> TFSCommandResult:
        """Checkin files to TFS.
        
        Args:
            options: Checkin options.
            
        Returns:
            Command execution result.
        """
        command = ["checkin"]
        
        command.extend(["/comment:" + options.comment])
        
        if options.recursive:
            command.append("/recursive")
            
        if options.associate:
            for work_item in options.associate:
                command.extend(["/associate:" + str(work_item)])
                
        if options.resolve:
            for work_item in options.resolve:
                command.extend(["/resolve:" + str(work_item)])
                
        if options.override:
            command.extend(["/override:" + options.override])
            
        command.extend(options.paths)
        
        return await self._execute_command(command)

    async def add_files(self, paths: List[str], recursive: bool = False) -> TFSCommandResult:
        """Add files to TFS.
        
        Args:
            paths: Paths to add.
            recursive: Whether to add recursively.
            
        Returns:
            Command execution result.
        """
        command = ["add"]
        
        if recursive:
            command.append("/recursive")
            
        command.extend(paths)
        
        return await self._execute_command(command)

    async def delete_files(self, paths: List[str], recursive: bool = False) -> TFSCommandResult:
        """Delete files from TFS.
        
        Args:
            paths: Paths to delete.
            recursive: Whether to delete recursively.
            
        Returns:
            Command execution result.
        """
        command = ["delete"]
        
        if recursive:
            command.append("/recursive")
            
        command.extend(paths)
        
        return await self._execute_command(command)

    async def rename_file(self, old_path: str, new_path: str) -> TFSCommandResult:
        """Rename a file in TFS.
        
        Args:
            old_path: Current path of the file.
            new_path: New path for the file.
            
        Returns:
            Command execution result.
        """
        command = ["rename", old_path, new_path]
        return await self._execute_command(command)

    async def undo_changes(self, paths: List[str], recursive: bool = False) -> TFSCommandResult:
        """Undo pending changes in TFS.
        
        Args:
            paths: Paths to undo changes for.
            recursive: Whether to undo recursively.
            
        Returns:
            Command execution result.
        """
        command = ["undo"]
        
        if recursive:
            command.append("/recursive")
            
        command.extend(paths)
        
        return await self._execute_command(command)

    async def get_status(
        self, 
        paths: Optional[List[str]] = None, 
        recursive: bool = False
    ) -> TFSCommandResult:
        """Get status of files in TFS.
        
        Args:
            paths: Paths to check status for. If None, checks current directory.
            recursive: Whether to check status recursively.
            
        Returns:
            Command execution result.
        """
        command = ["status"]
        
        if recursive:
            command.append("/recursive")
            
        if paths:
            command.extend(paths)
        else:
            command.append(".")
            
        return await self._execute_command(command)

    async def get_latest(
        self, 
        paths: Optional[List[str]] = None, 
        recursive: bool = False,
        force: bool = False
    ) -> TFSCommandResult:
        """Get latest version from TFS.
        
        Args:
            paths: Paths to get latest for. If None, gets current directory.
            recursive: Whether to get latest recursively.
            force: Whether to force overwrite local changes.
            
        Returns:
            Command execution result.
        """
        command = ["get"]
        
        if recursive:
            command.append("/recursive")
            
        if force:
            command.append("/force")
            
        if paths:
            command.extend(paths)
        else:
            command.append(".")
            
        return await self._execute_command(command)

    async def create_branch(self, branch_info: TFSBranchInfo) -> TFSCommandResult:
        """Create a branch in TFS.
        
        Args:
            branch_info: Branch information.
            
        Returns:
            Command execution result.
        """
        command = ["branch", branch_info.source_path, branch_info.target_path]
        
        if branch_info.version:
            command.extend(["/version:" + branch_info.version])
            
        return await self._execute_command(command)

    async def merge_files(self, options: TFSMergeOptions) -> TFSCommandResult:
        """Merge files in TFS.
        
        Args:
            options: Merge options.
            
        Returns:
            Command execution result.
        """
        command = ["merge", options.source, options.target]
        
        if options.version:
            command.extend(["/version:" + options.version])
            
        if options.recursive:
            command.append("/recursive")
            
        if options.discard:
            command.append("/discard")
            
        if options.baseless:
            command.append("/baseless")
            
        return await self._execute_command(command)

    async def get_history(self, options: TFSHistoryOptions) -> TFSCommandResult:
        """Get history of a file or folder in TFS.
        
        Args:
            options: History options.
            
        Returns:
            Command execution result.
        """
        command = ["history", options.path]
        
        if options.recursive:
            command.append("/recursive")
            
        if options.stopafter:
            command.extend(["/stopafter:" + str(options.stopafter)])
            
        if options.version:
            command.extend(["/version:" + options.version])
            
        if options.user:
            command.extend(["/user:" + options.user])
            
        return await self._execute_command(command) 