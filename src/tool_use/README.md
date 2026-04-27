# Tool Use Example

This project illustrates how to implement function calling (tool use) using local models via LM Studio's OpenAI-compatible API. It provides a generic tool-calling framework and includes practical examples such as a mock weather API tool and a Python code execution tool to solve math problems.

**Book Chapter:** [Tool Use / Function Calling](https://leanpub.com/read/LMstudio/tool-use--function-calling) — *LM Studio In Action* (free to read online).

## Prerequisites
- LM Studio installed and running with local server enabled.
- A tool-capable model loaded in LM Studio.
- `uv` installed for dependency management.

## Installation and Running

Run the examples using `uv`:

```bash
uv run weather_tool.py
uv run test1.py
```
