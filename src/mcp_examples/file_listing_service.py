# Design pattern for a tool definition
from fastmcp import FastMCP
import os

# Initialize the MCP server
app = FastMCP("my-mcp-server")

@app.tool()
def list_directory(path: str = ".") -> list[str]:
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
