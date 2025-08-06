"""Tests for TFS Client."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from tfs_mcp_server.tfs_client import TFSClient
from tfs_mcp_server.types import TFSCheckoutOptions, TFSCheckinOptions, TFSCommandResult


class TestTFSClient:
    """Test cases for TFS Client."""

    def setup_method(self) -> None:
        """Setup method called before each test."""
        self.client = TFSClient(tf_exe_path="tf.exe", working_directory="/test/dir")

    def test_client_initialization(self) -> None:
        """Test client initialization."""
        assert self.client.tf_exe_path == "tf.exe"
        assert self.client.working_directory == "/test/dir"

    def test_client_initialization_defaults(self) -> None:
        """Test client initialization with defaults."""
        client = TFSClient()
        assert client.tf_exe_path == "tf"
        assert client.working_directory is not None

    @pytest.mark.asyncio
    async def test_execute_command_success(self) -> None:
        """Test successful command execution."""
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"Success output", b"")
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process):
            result = await self.client._execute_command(["status", "."])
            
            assert result.success is True
            assert result.output == "Success output"
            assert result.error is None
            assert result.return_code == 0
            assert "tf.exe status ." in result.command

    @pytest.mark.asyncio
    async def test_execute_command_failure(self) -> None:
        """Test failed command execution."""
        mock_process = AsyncMock()
        mock_process.returncode = 1
        mock_process.communicate.return_value = (b"", b"Error occurred")
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process):
            result = await self.client._execute_command(["invalid", "command"])
            
            assert result.success is False
            assert result.output == ""
            assert result.error == "Error occurred"
            assert result.return_code == 1
            assert "tf.exe invalid command" in result.command

    @pytest.mark.asyncio
    async def test_execute_command_exception(self) -> None:
        """Test command execution with exception."""
        with patch('asyncio.create_subprocess_exec', side_effect=Exception("Process error")):
            result = await self.client._execute_command(["test"])
            
            assert result.success is False
            assert result.error == "Process error"
            assert result.return_code == -1

    @pytest.mark.asyncio
    async def test_checkout_files(self) -> None:
        """Test checkout files operation."""
        options = TFSCheckoutOptions(
            paths=["file1.txt", "file2.txt"],
            lock_type="checkout",
            recursive=True,
            type="text"
        )
        
        with patch.object(self.client, '_execute_command') as mock_exec:
            mock_exec.return_value = TFSCommandResult(
                success=True, 
                output="Checked out files",
                error=None,
                return_code=0,
                command="test"
            )
            
            result = await self.client.checkout_files(options)
            
            assert result.success is True
            mock_exec.assert_called_once()
            # Verify the command includes expected parameters
            called_args = mock_exec.call_args[0][0]
            assert "checkout" in called_args
            assert "/lock:checkout" in called_args
            assert "/recursive" in called_args
            assert "/type:text" in called_args
            assert "file1.txt" in called_args
            assert "file2.txt" in called_args

    @pytest.mark.asyncio
    async def test_checkin_files(self) -> None:
        """Test checkin files operation."""
        options = TFSCheckinOptions(
            paths=["file1.txt"],
            comment="Test checkin",
            recursive=False,
            associate=[123, 456],
            resolve=[789]
        )
        
        with patch.object(self.client, '_execute_command') as mock_exec:
            mock_exec.return_value = TFSCommandResult(
                success=True,
                output="Checked in files", 
                error=None,
                return_code=0,
                command="test"
            )
            
            result = await self.client.checkin_files(options)
            
            assert result.success is True
            mock_exec.assert_called_once()
            called_args = mock_exec.call_args[0][0]
            assert "checkin" in called_args
            assert "/comment:Test checkin" in called_args
            assert "/associate:123" in called_args
            assert "/associate:456" in called_args
            assert "/resolve:789" in called_args
            assert "file1.txt" in called_args

    @pytest.mark.asyncio
    async def test_add_files(self) -> None:
        """Test add files operation."""
        with patch.object(self.client, '_execute_command') as mock_exec:
            mock_exec.return_value = TFSCommandResult(
                success=True,
                output="Added files",
                error=None, 
                return_code=0,
                command="test"
            )
            
            result = await self.client.add_files(["new_file.txt"], recursive=True)
            
            assert result.success is True
            mock_exec.assert_called_once()
            called_args = mock_exec.call_args[0][0]
            assert "add" in called_args
            assert "/recursive" in called_args
            assert "new_file.txt" in called_args

    @pytest.mark.asyncio
    async def test_get_status(self) -> None:
        """Test get status operation."""
        with patch.object(self.client, '_execute_command') as mock_exec:
            mock_exec.return_value = TFSCommandResult(
                success=True,
                output="file.txt - edit",
                error=None,
                return_code=0, 
                command="test"
            )
            
            result = await self.client.get_status(["file.txt"], recursive=True)
            
            assert result.success is True
            assert result.output == "file.txt - edit"
            mock_exec.assert_called_once()
            called_args = mock_exec.call_args[0][0]
            assert "status" in called_args
            assert "/recursive" in called_args
            assert "file.txt" in called_args 