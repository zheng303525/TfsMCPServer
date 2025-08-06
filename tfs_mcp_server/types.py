"""Type definitions for TFS MCP Server."""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class TFSFileStatus(str, Enum):
    """TFS file status enumeration."""
    
    ADD = "add"
    EDIT = "edit"
    DELETE = "delete"
    RENAME = "rename"
    UNDELETE = "undelete"
    BRANCH = "branch"
    MERGE = "merge"
    UNKNOWN = "unknown"


class TFSCommandResult(BaseModel):
    """Result of a TFS command execution."""
    
    success: bool = Field(..., description="Whether the command succeeded")
    output: str = Field(default="", description="Command output")
    error: Optional[str] = Field(default=None, description="Error message if command failed")
    return_code: int = Field(default=0, description="Command return code")
    command: str = Field(..., description="The command that was executed")


class TFSFileInfo(BaseModel):
    """Information about a TFS-tracked file."""
    
    server_path: str = Field(..., description="Server path of the file")
    local_path: str = Field(..., description="Local path of the file")
    status: TFSFileStatus = Field(..., description="File status in TFS")
    version: Optional[int] = Field(default=None, description="File version")
    user: Optional[str] = Field(default=None, description="User who last modified")
    change: Optional[int] = Field(default=None, description="Change number")


class TFSWorkspaceInfo(BaseModel):
    """Information about a TFS workspace."""
    
    name: str = Field(..., description="Workspace name")
    owner: str = Field(..., description="Workspace owner")
    computer: str = Field(..., description="Computer name")
    comment: Optional[str] = Field(default=None, description="Workspace comment")
    collection: str = Field(..., description="Team Project Collection URL")
    location: str = Field(..., description="Workspace location (Local/Server)")


class TFSCheckoutOptions(BaseModel):
    """Options for TFS checkout operation."""
    
    paths: List[str] = Field(..., description="Paths to checkout")
    lock_type: Optional[str] = Field(
        default=None, 
        description="Lock type (none, checkin, checkout)"
    )
    recursive: bool = Field(default=False, description="Recursive checkout")
    type: Optional[str] = Field(default=None, description="File type")


class TFSCheckinOptions(BaseModel):
    """Options for TFS checkin operation."""
    
    paths: List[str] = Field(..., description="Paths to checkin")
    comment: str = Field(..., description="Checkin comment")
    recursive: bool = Field(default=False, description="Recursive checkin")
    associate: Optional[List[int]] = Field(
        default=None, 
        description="Work item IDs to associate"
    )
    resolve: Optional[List[int]] = Field(
        default=None, 
        description="Work item IDs to resolve"
    )
    override: Optional[str] = Field(
        default=None, 
        description="Override reason for policy failures"
    )


class TFSBranchInfo(BaseModel):
    """Information about a TFS branch."""
    
    source_path: str = Field(..., description="Source path")
    target_path: str = Field(..., description="Target path") 
    version: Optional[str] = Field(default=None, description="Version specification")
    
    
class TFSMergeOptions(BaseModel):
    """Options for TFS merge operation."""
    
    source: str = Field(..., description="Source path or branch")
    target: str = Field(..., description="Target path") 
    version: Optional[str] = Field(default=None, description="Version specification")
    recursive: bool = Field(default=False, description="Recursive merge")
    discard: bool = Field(default=False, description="Discard changes")
    baseless: bool = Field(default=False, description="Baseless merge")


class TFSHistoryOptions(BaseModel):
    """Options for TFS history operation."""
    
    path: str = Field(..., description="Path to get history for")
    recursive: bool = Field(default=False, description="Recursive history")
    stopafter: Optional[int] = Field(default=None, description="Maximum number of changes")
    version: Optional[str] = Field(default=None, description="Version range")
    user: Optional[str] = Field(default=None, description="Filter by user")


class TFSChangesetInfo(BaseModel):
    """Information about a TFS changeset."""
    
    changeset: int = Field(..., description="Changeset number")
    date: str = Field(..., description="Changeset date")
    user: str = Field(..., description="User who created the changeset")
    comment: str = Field(..., description="Changeset comment")
    files: List[TFSFileInfo] = Field(default_factory=list, description="Files in changeset") 