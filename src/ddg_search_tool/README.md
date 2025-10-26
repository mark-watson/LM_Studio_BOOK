# DDG Search Tool

This project demos how to invoke an LM Studio hosted model with a DuckDuckGo search function exposed as an OpenAI-style tool. The example prompt asks the model to discover which musical instruments author and consultant Mark Watson plays.

## Running the Example

- Ensure an LM Studio server is listening at `http://localhost:1234` with a compatible chat-completion model (default: `mlx-community/gpt-oss-20b`).
- From this directory run `uv run ddg_search.py` to execute the request and display the model response.
- Enable verbose logging with `uv run ddg_search.py --debug` or by setting `DDG_SEARCH_DEBUG=1` to inspect the payload, response status, and tool-call metadata.

## Code Overview

- `ddg_search.py` constructs the OpenAI-compatible payload, submits it to LM Studio, and prints both the full response and structured tool-call details when present.
- The `tools` definition advertises a single DuckDuckGo function (`ddg-search`) that accepts a `query` string describing the search to run.
- `messages` seeds the conversation with the Mark Watson question; adjust the content or extend the list to experiment with other prompts.
- The `debug_print` helper reports payloads, HTTP status codes, tool-call payloads, and fallback paths when you pass `--debug` or set the environment flag.
