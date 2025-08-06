# VS Code + TFS MCP Server Usage Example

This document demonstrates how VS Code can properly use the TFS MCP Server with relative paths by passing the workspace directory.

## Problem Scenario

When VS Code opens a workspace at `/workspace/myproject` and the MCP server is running with a different default working directory, relative paths would be resolved incorrectly.

**Example Issue:**
- VS Code workspace: `C:\Projects\MyApp`
- MCP server default: `C:\TFS\DefaultWorkspace`
- Relative path: `src\main.cs`

**Without working_directory parameter:**
- Path resolves to: `C:\TFS\DefaultWorkspace\src\main.cs` ❌ (wrong!)

**With working_directory parameter:**
- Path resolves to: `C:\Projects\MyApp\src\main.cs` ✅ (correct!)

## Solution: Pass working_directory Parameter

All TFS tools now support an optional `working_directory` parameter that VS Code can use to pass its current workspace directory.

### Example Tool Calls

#### 1. Checkout Files
```json
{
  "tool": "tf_checkout",
  "arguments": {
    "paths": ["src/Services/UserService.cs", "tests/UserServiceTests.cs"],
    "working_directory": "C:\\Projects\\MyApp",
    "lock_type": "checkout",
    "recursive": false
  }
}
```

#### 2. Check Status
```json
{
  "tool": "tf_status", 
  "arguments": {
    "paths": ["src/", "tests/"],
    "working_directory": "C:\\Projects\\MyApp",
    "recursive": true
  }
}
```

#### 3. Add New Files
```json
{
  "tool": "tf_add",
  "arguments": {
    "paths": ["src/Models/NewModel.cs"],
    "working_directory": "C:\\Projects\\MyApp",
    "recursive": false
  }
}
```

#### 4. Checkin Changes
```json
{
  "tool": "tf_checkin",
  "arguments": {
    "paths": ["src/Services/UserService.cs", "src/Models/NewModel.cs"],
    "working_directory": "C:\\Projects\\MyApp",
    "comment": "Added new user model and updated service",
    "recursive": false
  }
}
```

## Benefits

### ✅ Correct Path Resolution
- Relative paths are resolved based on the VS Code workspace
- No need to convert paths to absolute paths in VS Code
- Works consistently across different machines/environments

### ✅ Multi-Project Support
- Single MCP server can handle multiple VS Code workspaces
- Each workspace can have its own working directory
- No conflicts between different projects

### ✅ Flexible Deployment
- MCP server location doesn't affect path resolution
- Server can run from any directory
- Works with remote servers

## Implementation Notes

### For VS Code Extension Developers

When calling TFS MCP tools from VS Code:

1. **Always pass working_directory**: Include the current workspace root path
2. **Use relative paths**: Let the server handle absolute path conversion
3. **Handle multiple workspaces**: Pass the correct workspace for each operation

```typescript
// VS Code extension example
const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

await mcpClient.callTool('tf_checkout', {
  paths: ['src/main.ts', 'package.json'],
  working_directory: workspaceRoot,
  lock_type: 'checkout'
});
```

### For MCP Server Administrators

When deploying the TFS MCP server:

1. **Set a reasonable default**: Use `--working-directory` for fallback cases
2. **Document the pattern**: Ensure clients know to pass working_directory
3. **Monitor usage**: Check logs for path resolution issues

```bash
# Start server with default working directory
tfs-mcp-server --working-directory "C:\TFS\DefaultWorkspace" --transport http --port 8000
```

## Backward Compatibility

- Existing tools continue to work without the `working_directory` parameter
- When not provided, the server uses its configured default working directory
- No breaking changes to existing MCP clients 