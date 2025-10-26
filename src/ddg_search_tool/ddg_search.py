import requests
import json
import sys
import os

# --- Configuration ---
# This is the default LM Studio server endpoint
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

# The model you specified
MODEL_NAME = "mlx-community/gpt-oss-20b"

# LM Studio doesn't typically require a real key,
# but the 'Bearer' prefix is standard for the API format.
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer lm-studio-key"
}

# --- Debugging ---
DEBUG = "--debug" in sys.argv or os.getenv("DDG_SEARCH_DEBUG") == "1"
if "--debug" in sys.argv:
    sys.argv = [arg for arg in sys.argv if arg != "--debug"]


def debug_print(message):
    if DEBUG:
        print(f"[DEBUG] {message}")


# --- Tool Definition ---
# A general-purpose web search tool following the OpenAI tool-use format.
# The tool takes a single 'query' string parameter.
tools = [
    {
        "type": "function",
        "function": {
            "name": "ddg-search",
                "description": "Performs a general web search using DuckDuckGo.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to forward to DuckDuckGo."
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# --- Prompt ---
# A user message designed to trigger the web search tool.
messages = [
    {
        "role": "user",
        "content": "What is the weather in Flagstaff Arizona for today?"
    }
]

# --- Payload ---
# We bundle the model, messages, and tools into the request body.
# "tool_choice": "auto" lets the model decide whether to use the tool.
data = {
    "model": MODEL_NAME,
    "messages": messages,
    "tools": tools,
    "tool_choice": "auto",
    "stream": False # We want a single JSON response, not a stream
}

# --- Main Execution ---
def call_lm_studio():
    """
    Sends the request to LM Studio and prints the tool call response.
    """
    print(f"Sending request to LM Studio at {LM_STUDIO_URL} for model {MODEL_NAME}...")
    debug_print("Debug logging enabled.")

    try:
        # Make the POST request
        if DEBUG:
            debug_print(f"Request payload: {json.dumps(data, indent=2)}")

        response = requests.post(
            LM_STUDIO_URL,
            headers=HEADERS,
            data=json.dumps(data),  # Use json.dumps to serialize the payload
            timeout=60  # Set a reasonable timeout
        )

        debug_print(f"HTTP status received: {response.status_code}")

        # Check for HTTP errors
        response.raise_for_status()

        # Parse the JSON response
        response_json = response.json()

        print("\n--- Full Model Response ---")
        print(json.dumps(response_json, indent=2))

        # --- Check for Tool Call ---
        choice = response_json.get('choices', [])[0]
        message = choice.get('message', {})

        if message.get('tool_calls'):
            print("\n--- Tool Call Detected! ---")
            tool_call = message['tool_calls'][0]
            function_name = tool_call['function']['name']
            function_args_str = tool_call['function']['arguments']

            if DEBUG:
                debug_print(f"Tool call payload: {json.dumps(tool_call, indent=2)}")
            
            print(f"Function Name: {function_name}")
            
            # Parse the arguments string into a JSON object for readability
            try:
                function_args = json.loads(function_args_str)
                print("Function Arguments:")
                print(json.dumps(function_args, indent=2))
            except json.JSONDecodeError:
                print(f"Function Arguments (raw string): {function_args_str}")
        elif message.get('content'):
            debug_print("Model returned direct content without tool call.")
            print("\n--- No Tool Call Detected ---")
            print(f"Model Replied Directly: {message['content']}")
        else:
            debug_print("Response message missing both tool calls and content.")
            print("\n--- Unexpected Response Format ---")
            print("The response did not contain tool calls or message content.")

    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] Connection refused.", file=sys.stderr)
        print("Please ensure your LM Studio server is running at {LM_STUDIO_URL}", file=sys.stderr)
    except requests.exceptions.HTTPError as e:
        print(f"\n[ERROR] HTTP Error: {e.response.status_code} {e.response.reason}", file=sys.stderr)
        print(f"Response Body: {e.response.text}", file=sys.stderr)
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}", file=sys.stderr)
    except (KeyError, IndexError):
        print("\n[ERROR] Failed to parse the response structure.", file=sys.stderr)
        print("Received data did not match expected format.")

if __name__ == "__main__":
    call_lm_studio()
