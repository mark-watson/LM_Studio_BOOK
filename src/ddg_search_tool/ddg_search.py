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

def perform_ddg_search(query: str) -> str:
    """
    Performs a search using DuckDuckGo's Instant Answer API and returns a formatted result.
    """
    debug_print(f"Performing DDG search for: {query}")
    search_url = f"https://api.duckduckgo.com/?q={query}&format=json"
    
    try:
        response = requests.get(search_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return json.dumps(data)

    except requests.exceptions.RequestException as e:
        debug_print(f"DDG search failed: {e}")
        return f"Error performing search for '{query}': {e}"
    except json.JSONDecodeError:
        debug_print("Failed to decode JSON from DDG API.")
        return f"Error decoding search results for '{query}'."


# --- Main Execution ---
def call_lm_studio():
    """
    Sends the request to LM Studio, handles tool calls, and prints the final response.
    """
    print(f"Sending request to LM Studio at {LM_STUDIO_URL} for model {MODEL_NAME}...")
    debug_print("Debug logging enabled.")

    messages = [
        {
            "role": "user",
            "content": "Perform a web search to check what is the population of Flagstaff Arizona?"
        }
    ]

    data = {
        "model": MODEL_NAME,
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
        "stream": False
    }

    try:
        if DEBUG:
            debug_print(f"Initial request payload: {json.dumps(data, indent=2)}")

        response = requests.post(LM_STUDIO_URL, headers=HEADERS, data=json.dumps(data), timeout=60)
        response.raise_for_status()
        response_json = response.json()

        print("\n--- Initial Model Response ---")
        print(json.dumps(response_json, indent=2))

        choice = response_json.get('choices', [])[0]
        message = choice.get('message', {})
        
        messages.append(message)

        if message.get('tool_calls'):
            print("\n--- Tool Call Detected! ---")
            tool_call = message['tool_calls'][0]
            function_name = tool_call['function']['name']
            function_args_str = tool_call['function']['arguments']
            
            try:
                function_args = json.loads(function_args_str)
                query = function_args.get("query")

                if function_name == "ddg-search" and query:
                    search_result = perform_ddg_search(query)
                    print(f"\n--- Search Result ---\n{search_result}")

                    tool_message = {
                        "role": "tool",
                        "tool_call_id": tool_call['id'],
                        "content": search_result
                    }
                    messages.append(tool_message)

                    print("\n--- Sending search result back to the model... ---")
                    
                    follow_up_data = {
                        "model": MODEL_NAME,
                        "messages": messages,
                        "stream": False
                    }
                    
                    if DEBUG:
                        debug_print(f"Follow-up request payload: {json.dumps(follow_up_data, indent=2)}")

                    final_response = requests.post(LM_STUDIO_URL, headers=HEADERS, data=json.dumps(follow_up_data), timeout=60)
                    final_response.raise_for_status()
                    final_response_json = final_response.json()

                    print("\n--- Final Model Response ---")
                    print(json.dumps(final_response_json, indent=2))
                    
                    final_message = final_response_json.get('choices', [])[0].get('message', {})
                    if final_message.get('content'):
                        print("\n--- Final Answer ---")
                        print(final_message['content'])

            except json.JSONDecodeError:
                print(f"\n--- Could not decode tool call arguments: {function_args_str} ---")

        elif message.get('content'):
            debug_print("Model returned direct content without tool call.")
            print("\n--- No Tool Call Detected ---")
            print(f"Model Replied Directly: {message['content']}")

    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] Connection refused.", file=sys.stderr)
        print(f"Please ensure your LM Studio server is running at {LM_STUDIO_URL}", file=sys.stderr)
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
