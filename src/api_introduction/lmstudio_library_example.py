import lmstudio as lms

# --- Main Execution ---
def get_llm_response_with_sdk(prompt):
    """
    Loads a model and gets a response using the lmstudio-python SDK.
    """
    # Before running this, make sure you have:
    # 1. Downloaded and installed LM Studio.
    # 2. Started the LM Studio application. The SDK communicates directly
    #    with the running application; you don't need to manually start the server.

    try:
        # Load a model by its repository ID from the Hugging Face Hub.
        # The SDK will communicate with LM Studio to use the model.
        # If the model isn't downloaded, LM Studio might handle that,
        # but it's best to have it downloaded first.
        #
        # Replace this with the identifier of a model you have downloaded.
        # e.g., "gemma-2-9b-it-gguf"
        print("Loading model...")
        model = lms.llm("google/gemma-3n-e4b")

        # Send a prompt to the loaded model.
        print("Sending prompt to the model...")
        response = model.respond(
            [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt},
            ]
        )

        # The 'response' object contains the full API response.
        # The text content is in response.text
        return response.text

    except Exception as e:
        print(f"\nAn error occurred:")
        print("Please ensure the LM Studio application is running and the model identifier is correct.")
        print(f"Error details: {e}")


if __name__ == "__main__":
    print("--- Local LLM Interaction via lmstudio-python SDK ---")
    print("\n--- Model Response ---")
    print(get_llm_response_with_sdk("Explain the significance of the Rosetta Stone in one paragraph."))
