from openai import OpenAI

# --- Configuration ---
# Point the client to your local LM Studio server
# The default base_url is "http://localhost:1234/v1"
# You can leave the api_key as a placeholder; it's not required for local servers.
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# --- Main Execution ---
def get_local_llm_response():
    """
    Sends a request to the local LLM and prints the response.
    """
    # Before running this, make sure you have:
    # 1. Downloaded and installed LM Studio.
    # 2. Downloaded a model from the LM Studio hub.
    # 3. In the "Local Server" tab (the '<->' icon), selected your model
    #    at the top and clicked "Start Server".

    # The "model" parameter should be a placeholder, as the model is
    # selected and loaded in the LM Studio UI. The server will use
    # whichever model is currently loaded.
    try:
        completion = client.chat.completions.create(
            model="local-model",  # This field is ignored by LM Studio but is required by the API.
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": "What is the capital of France?"}
            ],
            temperature=0.7,
        )

        # Extracting and printing the response content
        response_message = completion.choices[0].message.content
        print("\nResponse from local model:")
        print(response_message)

    except Exception as e:
        print(f"\nAn error occurred:")
        print(f"It's likely the LM Studio server is not running or the model is not loaded.")
        print(f"Please ensure the server is active and a model is selected.")
        print(f"Error details: {e}")


if __name__ == "__main__":
    print("--- Local LLM Interaction via OpenAI Compatibility ---")
    get_local_llm_response()
