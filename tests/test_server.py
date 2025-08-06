"""Tests for TFS MCP Server."""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch

from fastmcp import Client
from tfs_mcp_server.server import TFSMcpServer
from tfs_mcp_server.types import TFSCommandResult


class TestTFSMcpServer:
    """Test cases for TFS MCP Server."""

    def setup_method(self) -> None:
        """Setup method called before each test."""
        self.server = TFSMcpServer(name="Test TFS Server")

    def test_server_initialization(self) -> None:
        """Test server initialization."""
        assert self.server is not None
        assert self.server.mcp.name == "Test TFS Server"
        assert self.server.tfs_client is not None

    @pytest.mark.asyncio
    async def test_tf_checkout_tool(self) -> None:
        """Test tf_checkout tool."""
        # Mock the TFS client
        mock_result = TFSCommandResult(
            success=True,
            output="Checked out file.txt",
            error=None,
            return_code=0,
            command="tf checkout file.txt"
        )
        
        with patch.object(
            self.server.tfs_client, 
            'checkout_files', 
            return_value=mock_result
        ) as mock_checkout:
            # Use FastMCP Client for in-memory testing
            async with Client(self.server.mcp) as client:
                # Get available tools
                tools = await client.list_tools()
                tool_names = [tool.name for tool in tools]
                
                assert "tf_checkout" in tool_names
                
                # Call the tool
                result = await client.call_tool(
                    "tf_checkout",
                    {"paths": ["file.txt"]}
                )
                
                assert result.content[0].text is not None
                result_data = json.loads(result.content[0].text)  # Parse JSON response
                assert result_data["success"] is True
                assert result_data["output"] == "Checked out file.txt"
                mock_checkout.assert_called_once()

    @pytest.mark.asyncio
    async def test_tf_add_tool(self) -> None:
        """Test tf_add tool."""
        mock_result = TFSCommandResult(
            success=True,
            output="Added file.txt",
            error=None,
            return_code=0,
            command="tf add file.txt"
        )
        
        with patch.object(
            self.server.tfs_client, 
            'add_files', 
            return_value=mock_result
        ) as mock_add:
            async with Client(self.server.mcp) as client:
                tools = await client.list_tools()
                tool_names = [tool.name for tool in tools]
                
                assert "tf_add" in tool_names
                
                result = await client.call_tool(
                    "tf_add",
                    {"paths": ["file.txt"]}
                )
                
                result_data = json.loads(result.content[0].text)
                assert result_data["success"] is True
                assert result_data["output"] == "Added file.txt"
                mock_add.assert_called_once_with(["file.txt"], False)

    @pytest.mark.asyncio
    async def test_tf_status_tool(self) -> None:
        """Test tf_status tool."""
        mock_result = TFSCommandResult(
            success=True,
            output="file.txt - edit",
            error=None,
            return_code=0,
            command="tf status ."
        )
        
        with patch.object(
            self.server.tfs_client, 
            'get_status', 
            return_value=mock_result
        ) as mock_status:
            async with Client(self.server.mcp) as client:
                tools = await client.list_tools()
                tool_names = [tool.name for tool in tools]
                
                assert "tf_status" in tool_names
                
                result = await client.call_tool(
                    "tf_status",
                    {}
                )
                
                result_data = json.loads(result.content[0].text)
                assert result_data["success"] is True
                assert result_data["output"] == "file.txt - edit"
                mock_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_tool_registration(self) -> None:
        """Test that all expected tools are registered."""
        expected_tools = {
            "tf_checkout", "tf_checkin", "tf_add", "tf_delete", 
            "tf_rename", "tf_undo", "tf_status", "tf_get_latest",
            "tf_branch", "tf_merge", "tf_history"
        }
        
        async with Client(self.server.mcp) as client:
            tools = await client.list_tools()
            actual_tools = {tool.name for tool in tools}
            
            assert expected_tools.issubset(actual_tools)

    @pytest.mark.asyncio
    async def test_resource_registration(self) -> None:
        """Test that expected resources are registered."""
        async with Client(self.server.mcp) as client:
            resources = await client.list_resources()
            
            # Check that at least one resource is registered
            assert len(resources) >= 1
            
            # Check for expected resource
            resource_uris = [resource.uri for resource in resources]
            assert any('tfs://workspace/info' in str(uri) for uri in resource_uris) 