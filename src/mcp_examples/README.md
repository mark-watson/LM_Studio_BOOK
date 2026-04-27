# Model Context Protocol Examples

This project provides a simple implementation of an MCP (Model Context Protocol) server using the `fastmcp` library. It exposes multiple tools—such as basic arithmetic, fetching the current time, and a local directory listing service—which can be integrated with LM Studio or other compatible platforms.

**Book Chapter:** [A Technical Introduction to Model Context Protocol and Experiments with LM Studio](https://leanpub.com/read/LMstudio/a-technical-introduction-to-model-context-protocol-and-experiments-with-lm-studio) — *LM Studio In Action* (free to read online).

## Prerequisites
- LM Studio installed.
- Python 3 with `uv` installed for dependency management.
- The `mcp.json` file should be properly configured in LM Studio's tools/MCP settings to connect to this server.

## Installation and Running

Run the example using `uv`:

```bash
uv run server.py
```

*Note: MCP servers are designed to be run as subprocesses by the client (e.g. LM Studio) and communicate over stdio, but you can run it manually for testing and development.*
