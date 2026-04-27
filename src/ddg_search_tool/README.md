# DDG Search Tool

This project demonstrates how to implement tool use (function calling) with LM Studio's local API. It defines a custom DuckDuckGo web search tool and allows an LLM to query the internet to answer user questions, acting on the model's tool call requests and passing the results back for a final answer.

**Book Chapter:** [Tool Use / Function Calling](https://leanpub.com/read/LMstudio/tool-use--function-calling) — *LM Studio In Action* (free to read online).

## Prerequisites
- LM Studio installed and running with local server enabled.
- An appropriate model loaded in LM Studio that supports tool calling (e.g., `mlx-community/gpt-oss-20b` or another tool-capable model).
- `uv` installed for dependency management.

## Installation and Running

Run the example using `uv`:

```bash
uv run ddg_search.py
```

To see more detailed debug output including the raw JSON payloads, you can pass the `--debug` flag:

```bash
uv run ddg_search.py --debug
```
