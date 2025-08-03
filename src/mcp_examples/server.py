from fastmcp import FastMCP

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

# To run the server (e.g., via stdio for local development)
if __name__ == "__main__":
    app.run()
