# API Introduction Example

This project demonstrates the basics of interacting with local Large Language Models using LM Studio. It includes examples of using the native `lmstudio` SDK for Python, as well as accessing the LM Studio local inference server using the OpenAI-compatible API.

**Book Chapter:** [Introduction to LM Studio's Local Inference API](https://leanpub.com/read/LMstudio/introduction-to-lm-studios-local-inference-api) — *LM Studio In Action* (free to read online).

## Prerequisites
- LM Studio installed and running.
- A model downloaded in LM Studio.
- For the OpenAI compatibility example, the LM Studio local server must be started.
- `uv` installed for dependency management.

## Installation and Running

Run the examples using `uv`:

```bash
uv run lmstudio_simple.py
uv run lmstudio_library_example.py
uv run openai_cmpatibility.py
```
