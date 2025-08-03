# Design pattern for a tool definition
from mcp.server.fast_mcp import FastMCP
import os

# Initialize the FastMCP server instance
mcp = FastMCP(title="LocalFileSystemServer", version="0.1.0")

@mcp.tool()
def list_directory(path: str) -> list[str]:
    """
    Lists all files and subdirectories within a given local directory path.
    The path should be an absolute path or relative to the user's home directory.
    """
    try:
        # Implementation logic will go here
        expanded_path = os.path.expanduser(path)
        return os.listdir(expanded_path)
    except FileNotFoundError:
        return # Return an empty list if path not found
