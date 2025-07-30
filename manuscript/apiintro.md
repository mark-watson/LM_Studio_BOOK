# Introduction to LM Studio's Local Inference API

Dear reader, we will start with two simple examples, one using the OpenAI AI compatibility features of LM Studio and the other using the Python **lmstudio** package. First, make sure you hit the green icon on the left menu area:

![Enable The API in "developer's mode using the slider in the upper left corner of the app. You should see "Status: Running" ](images/ui_dev_api_server.jpg)

When you installed LM Studio you were asked if you wanted "developer mode" enabled. That prompt during installation can be a bit misleading. You haven't been locked out of any features.

"Developer Mode" in LM Studio is simply a UI setting that you can toggle at any time. It's not a permanent choice made during installation.

Here’s how to enable it:

Look at the very bottom of the LM Studio window. You will see three buttons: **User**, **Power User**, and **Developer**.

Just click on **Developer** to switch to that mode. This will expose all the advanced configuration options and developer-focused features throughout the application, including more detailed settings in the Local Server tab.

When using the LM Studio inference APIs using Python scripts, you can't set the model, or even load a model. Instead, you must use the LM Studio application UI to choose and manually load a model. For Python applications I work on that require switching between different models, I don't use LM Studio, rather I then use Ollama ([read my Ollama book online](https://leanpub.com/ollama/read)).

For the examples in this chapter I manually selected and loaded the small but very capable model **google/gemma-3n-e4b**.

## Using the Python OpenAI Compatibility APIs

You can find the Python script examples for this book in the GitHub repository [https://github.com/mark-watson/LM_Studio_BOOK](https://github.com/mark-watson/LM_Studio_BOOK) in the **src** directory. The example we now use is in the file **src/api_introduction/openai_cmpatibility.py**:

```python
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
            model="local-model",  # This field is ignored by LM Studio
                                  #but is required by the API.
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
```

This Python script uses the official openai library to connect to a local AI model running in LM Studio, not OpenAI's servers.

It sends the question "What is the capital of France?" to your local model and prints its response to the console. The key is the base_url="http://localhost:1234/v1" line, which redirects the API request to the LM Studio server.

In the next chapter we will cover "tool use" which also reffered to as "function calling" (i.e., we write Python functions, configure API calls to inform a model the names and required arguments for tools/functions).
