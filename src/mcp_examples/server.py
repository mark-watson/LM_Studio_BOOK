from fastmcp import FastMCP
import os

# Initialize the MCP server
app = FastMCP("my-mcp-server")

@app.tool()
def add_numbers(a: int, b: int) -> int:
    """Adds two numbers together."""
    return a + b

@app.tool()
def get_current_time_for_mark() -> str:
    """Returns the current time."""
    import datetime
    return datetime.datetime.now().strftime("%H:%M:%S")

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
    

# To run the server (e.g., via stdio for local development)
if __name__ == "__main__":
    app.run()
