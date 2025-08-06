#!/usr/bin/env python3
"""
Installation script for TFS MCP Server.

This script helps users set up the TFS MCP Server development environment.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"Error running command: {command}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        sys.exit(1)
    
    return result


def main() -> None:
    """Main installation function."""
    print("TFS MCP Server Installation")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 10):
        print("Error: Python 3.10 or higher is required")
        sys.exit(1)
    
    print(f"Python version: {sys.version}")
    
    # Create virtual environment if it doesn't exist
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("\nCreating virtual environment...")
        run_command(f"{sys.executable} -m venv .venv")
    else:
        print("\nVirtual environment already exists")
    
    # Determine activation script based on OS
    if os.name == 'nt':  # Windows
        activate_script = ".venv\\Scripts\\activate"
        python_exe = ".venv\\Scripts\\python.exe"
        pip_exe = ".venv\\Scripts\\pip.exe"
    else:  # Unix-like
        activate_script = ".venv/bin/activate"
        python_exe = ".venv/bin/python"
        pip_exe = ".venv/bin/pip"
    
    # Install dependencies
    print("\nInstalling dependencies...")
    run_command(f"{pip_exe} install --upgrade pip")
    run_command(f"{pip_exe} install -r requirements.txt")
    
    # Install development dependencies if requested
    install_dev = input("\nInstall development dependencies? (y/N): ").lower().startswith('y')
    if install_dev:
        print("Installing development dependencies...")
        run_command(f"{pip_exe} install -r requirements-dev.txt")
        run_command(f"{pip_exe} install -e .")
        
        # Install pre-commit hooks
        print("Installing pre-commit hooks...")
        run_command(f"{python_exe} -m pre_commit install", check=False)
        
        print("\nDevelopment environment ready!")
        print("You can now run:")
        print(f"  {activate_script}")
        print("  make test")
        print("  make lint")
        print("  make type-check")
    else:
        print("\nBasic installation complete!")
        print("You can now run:")
        print(f"  {activate_script}")
        print(f"  {python_exe} -m tfs_mcp_server.main --help")
    
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    main() 