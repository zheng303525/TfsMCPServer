# TFS MCP Server

A comprehensive FastMCP server implementation for Team Foundation Server (TFS) operations, providing seamless integration with the Model Context Protocol (MCP) ecosystem.

## Features

- **Complete TFS Operations**: Support for all major TFS commands including checkout, checkin, add, delete, rename, undo, status, get latest, branch, merge, and history
- **Type-Safe Implementation**: Full type hints and mypy compatibility for reliable code execution  
- **Async/Await Support**: Non-blocking operations for better performance
- **Comprehensive Error Handling**: Detailed error reporting and logging
- **Flexible Configuration**: Customizable TFS executable path and working directories
- **Multiple Transport Protocols**: Support for stdio, HTTP, and SSE transports
- **Extensive Testing**: Comprehensive test suite with high code coverage
- **Modern Python Practices**: Follows Python best practices and coding standards

## Installation

### Prerequisites

- Python 3.10 or higher
- Team Foundation Server command line tools (`tf.exe`) installed and accessible
- Access to a TFS server with appropriate permissions

### Install from Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tfs-mcp-server.git
cd tfs-mcp-server
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install in development mode:
```bash
pip install -e .
```

### Install from PyPI (when published)

```bash
pip install tfs-mcp-server
```

## Quick Start

### Basic Usage

Start the TFS MCP server with default settings:

```bash
tfs-mcp-server
```

### Custom Configuration

```bash
tfs-mcp-server \
    --name "My TFS Server" \
    --tf-exe-path "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\Common7\IDE\CommonExtensions\Microsoft\TeamFoundation\Team Explorer\tf.exe" \
    --working-directory "C:\Source\MyProject" \
    --transport http \
    --host 0.0.0.0 \
    --port 8080
```

### Programmatic Usage

```python
from tfs_mcp_server import TFSMcpServer

# Create and configure the server
server = TFSMcpServer(
    name="TFS MCP Server",
    tf_exe_path="tf.exe",
    default_working_directory="/path/to/workspace"
)

# Run with stdio transport (default)
server.run()

# Or run with HTTP transport
server.run(transport="http", host="127.0.0.1", port=8000)
```

## VSCode MCP Integration

The TFS MCP Server can be integrated with VSCode using the Model Context Protocol. Below are two configuration methods for different transport types.

### Method 1: HTTP Transport Configuration

For HTTP transport, configure VSCode MCP settings to use the correct endpoint and headers:

```json
{
  "mcpServers": {
    "tfs-mcp-server": {
      "transport": "http",
      "url": "http://127.0.0.1:8000/mcp",
      "headers": {
        "Accept": "application/json, text/event-stream"
      }
    }
  }
}
```

Start the server with HTTP transport:

```bash
tfs-mcp-server --transport http --host 127.0.0.1 --port 8000
```

### Method 2: STDIO Transport Configuration (Recommended)

For local development, STDIO transport is the most stable and compatible option:

```json
{
  "mcpServers": {
    "tfs-mcp-server": {
      "transport": "stdio",
      "command": "python",
      "args": ["-m", "tfs_mcp_server.main"],
      "cwd": "C:\\Users\\User\\dev\\TFSMcp"
    }
  }
}
```

Or if you have the package installed globally:

```json
{
  "mcpServers": {
    "tfs-mcp-server": {
      "transport": "stdio",
      "command": "tfs-mcp-server",
      "cwd": "/path/to/your/tfs/workspace"
    }
  }
}
```

**Note**: Update the `cwd` path to point to your actual TFS workspace directory.

### Configuration Location

Add the MCP configuration to your VSCode settings:

1. Open VSCode Settings (Ctrl+,)
2. Search for "MCP" or find the MCP extension settings
3. Add the configuration JSON to the appropriate settings field

### Verification

After configuration, you should see the TFS MCP Server appear in your VSCode MCP servers list, providing access to all TFS operations through the MCP interface.

## Available Tools

The TFS MCP Server provides the following tools for TFS operations:

### File Operations

#### `tf_checkout`
Checkout files from TFS for editing.
- **Parameters**: `paths` (list), `lock_type` (optional), `recursive` (bool), `file_type` (optional)
- **Example**: Checkout files for editing with exclusive lock

#### `tf_checkin`  
Checkin files to TFS with comments and work item associations.
- **Parameters**: `paths` (list), `comment` (string), `recursive` (bool), `associate` (list), `resolve` (list), `override_reason` (optional)
- **Example**: Checkin changes with descriptive comment

#### `tf_add`
Add new files to TFS source control.
- **Parameters**: `paths` (list), `recursive` (bool)
- **Example**: Add new files to version control

#### `tf_delete`
Delete files from TFS source control.
- **Parameters**: `paths` (list), `recursive` (bool)  
- **Example**: Remove files from version control

#### `tf_rename`
Rename files in TFS source control.
- **Parameters**: `old_path` (string), `new_path` (string)
- **Example**: Rename a file while maintaining history

#### `tf_undo`
Undo pending changes in TFS.
- **Parameters**: `paths` (list), `recursive` (bool)
- **Example**: Revert uncommitted changes

### Information Operations

#### `tf_status`
Get the status of files in TFS.
- **Parameters**: `paths` (optional list), `recursive` (bool)
- **Example**: Check which files have pending changes

#### `tf_get_latest`
Get the latest version of files from TFS.
- **Parameters**: `paths` (optional list), `recursive` (bool), `force` (bool)
- **Example**: Update local files to latest server version

#### `tf_history`
Get the change history for files or folders.
- **Parameters**: `path` (string), `recursive` (bool), `stopafter` (optional int), `version` (optional), `user` (optional)
- **Example**: View commit history for analysis

### Branch Operations

#### `tf_branch`
Create a new branch in TFS.
- **Parameters**: `source_path` (string), `target_path` (string), `version` (optional)
- **Example**: Create feature branches for development

#### `tf_merge`
Merge changes between branches or paths.
- **Parameters**: `source` (string), `target` (string), `version` (optional), `recursive` (bool), `discard` (bool), `baseless` (bool)
- **Example**: Integrate changes from one branch to another

## Available Resources

### `tfs://workspace/info`
Get information about the current TFS workspace including name, owner, computer, and collection details.

### `tfs://status/{path}`
Get TFS status information for a specific path, showing pending changes and file states.

## Configuration Options

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--name` | Server name | "TFS MCP Server" |
| `--tf-exe-path` | Path to tf.exe executable | "tf" (from PATH) |
| `--working-directory` | Default working directory | Current directory |
| `--transport` | Transport protocol (stdio/http/sse) | "stdio" |
| `--host` | Host address for http/sse | "127.0.0.1" |
| `--port` | Port number for http/sse | 8000 |

### Environment Variables

You can also configure the server using environment variables:

```bash
export TFS_EXE_PATH="/path/to/tf.exe"
export TFS_WORKING_DIR="/path/to/workspace"
export MCP_TRANSPORT="http"
export MCP_HOST="0.0.0.0"  
export MCP_PORT="8080"
```

## Development

### Setup Development Environment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tfs-mcp-server.git
cd tfs-mcp-server
```

2. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

3. Install pre-commit hooks:
```bash
pre-commit install
```

### Running Tests

Run the full test suite:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=tfs_mcp_server --cov-report=html
```

Run specific test files:
```bash
pytest tests/test_server.py
pytest tests/test_tfs_client.py
```

### Type Checking

Run mypy for type checking:
```bash
mypy tfs_mcp_server/
```

### Code Formatting

Format code with black:
```bash
black tfs_mcp_server/ tests/
```

Sort imports with isort:
```bash
isort tfs_mcp_server/ tests/
```

Run flake8 for linting:
```bash
flake8 tfs_mcp_server/ tests/
```

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality. They run automatically on commit, or manually:

```bash
pre-commit run --all-files
```

## Architecture

### Project Structure

```
tfs-mcp-server/
├── tfs_mcp_server/          # Main package
│   ├── __init__.py          # Package initialization
│   ├── main.py              # Entry point and CLI
│   ├── server.py            # FastMCP server implementation
│   ├── tfs_client.py        # TFS command line client
│   ├── types.py             # Type definitions and models
│   └── py.typed             # Type checking marker
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_server.py       # Server tests
│   └── test_tfs_client.py   # Client tests
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── pyproject.toml          # Project configuration
├── .pre-commit-config.yaml # Pre-commit configuration
├── LICENSE                 # MIT license
└── README.md              # This file
```

### Design Principles

1. **Separation of Concerns**: Clear separation between MCP server logic and TFS operations
2. **Type Safety**: Comprehensive type hints for reliability and maintainability
3. **Error Handling**: Robust error handling with detailed error messages
4. **Testability**: Comprehensive test coverage with mocked dependencies
5. **Configurability**: Flexible configuration options for different environments
6. **Documentation**: Extensive documentation for users and developers

## Troubleshooting

### Common Issues

#### TFS Executable Not Found
```
Error: tf.exe not found in PATH
```
**Solution**: Install TFS command line tools or specify the path using `--tf-exe-path`

#### Permission Denied
```
Error: Access denied when executing TFS commands
```
**Solution**: Ensure you have proper TFS permissions and are authenticated with the server

#### Workspace Not Found
```
Error: No workspace found for the current directory
```
**Solution**: Navigate to a directory within a TFS workspace or create/map a workspace

#### Connection Issues
```
Error: Unable to connect to TFS server
```
**Solution**: Check network connectivity, server URL, and authentication credentials

### Debug Mode

Enable debug logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

server = TFSMcpServer(name="Debug TFS Server")
server.run()
```

### Getting Help

- Check the [Issues](https://github.com/yourusername/tfs-mcp-server/issues) page for known problems
- Create a new issue with detailed information about your problem
- Include TFS version, Python version, and operating system information

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes with tests
4. Ensure all tests pass: `pytest`
5. Ensure type checking passes: `mypy tfs_mcp_server/`
6. Format your code: `black tfs_mcp_server/ tests/`
7. Submit a pull request

### Code Standards

- Follow PEP 8 style guidelines
- Add type hints to all functions and methods  
- Write comprehensive docstrings
- Include unit tests for new functionality
- Ensure mypy type checking passes
- Update documentation as needed

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) - The fast, Pythonic way to build MCP servers
- Inspired by the [Model Context Protocol](https://modelcontextprotocol.io/) specification
- Thanks to all contributors and the open source community

## Changelog

### Version 0.1.0 (Initial Release)
- Complete TFS operations support (checkout, checkin, add, delete, rename, undo, status, get latest, branch, merge, history)
- Type-safe implementation with comprehensive type hints
- Async/await support for non-blocking operations  
- Multiple transport protocols (stdio, HTTP, SSE)
- Comprehensive test suite with high coverage
- Modern Python packaging and development tools
- Detailed documentation and examples

---

For more information about the Model Context Protocol, visit [modelcontextprotocol.io](https://modelcontextprotocol.io/) 