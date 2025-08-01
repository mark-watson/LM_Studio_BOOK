# Tool Use / Function Calling

The key to effective tool use with local models that aren't specifically fine-tuned for it is to guide them with a very structured prompt. You, dear reader, essentially create a "template" that the model learns to fill in. Alternatively some combinations of models and client API libraries provide built-in functionality that we implement explicitly in this chapter.

The advantage of "building it ourselves" is the flexibility of being able to use most models and libraries.

## An Initial Example: a Tool That is a Simple Python Function

The first example in this chapter can be found in the file **LM_Studio_BOOK/src/tool_use/weather_tool.py** and uses these steps:

- Define the Tools: First, I need to define the functions that the AI can "call." These are standard Python functions. For this example, I'll create a simple get_weather function.
- Create the Prompt Template: This is the most critical step for local models. I need to design a prompt that clearly explains the concept of tools, lists the available tools with their descriptions and parameters, and provides a format for the model to use when it wants to call a tool. The prompt should instruct the model to output a specific, parseable format, like JSON.
- Set up the LM Studio Client: I'll use the openai Python library, configured to point to the local LM Studio server. This allows for a familiar and standardized way to interact with the local model.
- Process User Input: The user's query is inserted into the prompt template.
- Send to Model & Get Response: The complete prompt is sent to the Gemma model running in LM Studio.
- Parse and Execute: Check the model's response. If it contains the special JSON format for a tool call, then we parse it, execute the corresponding Python function with the provided arguments, and then feed the result back to the model for a final, natural language response. If the initial response from the model doesn't contain a tool call, then we just use the response.

```python
from openai import OpenAI
import json
import re

def get_weather(city: str, unit: str = "celsius"):
    """
    Get the current weather for a given city.
    
    Args:
        city (str): The name of the city.
        unit (str): The temperature unit, 'celsius' or 'fahrenheit'.
    """
    # In a real application, you would call a weather API here.
    # For this example, we'll just return some mock data.
    if "chicago" in city.lower():
        return json.dumps({"city": "Chicago", "temperature": "12", "unit": unit})
    elif "tokyo" in city.lower():
        return json.dumps({"city": "Tokyo", "temperature": "25", "unit": unit})
    else:
        return json.dumps({"error": "City not found"})


# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# A dictionary to map tool names to actual functions
available_tools = {
    "get_weather": get_weather,
}

def run_conversation(user_prompt: str):
    # System prompt that defines the rules and tools for the model
    system_prompt = """
    You are a helpful assistant with access to the following tools.
    To use a tool, you must respond with a JSON object with two keys: "tool_name" and "parameters".
    
    Here are the available tools:
    {
        "tool_name": "get_weather",
        "description": "Get the current weather for a given city.",
        "parameters": [
            {"name": "city", "type": "string", "description": "The city name."},
            {"name": "unit", "type": "string", "description": "The unit for temperature, either 'celsius' or 'fahrenheit'."}
        ]
    }
    
    If you decide to use a tool, your response MUST be only the JSON object.
    If you don't need a tool, answer the user's question directly.
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    print("--- User Question ---")
    print(user_prompt)

    completion = client.chat.completions.create(
        model="local-model", # This will be ignored by LM Studio
        messages=messages,
        temperature=0.1, # Lower temperature for more predictable, structured output
    )

    response_message = completion.choices[0].message.content

    # More robustly find and extract the JSON from the model's response
    json_str = None
    tool_call = {}
    
    # Use regex to find JSON within ```json ... ``` or ``` ... ```
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_message, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # If no markdown block, maybe the whole message is the JSON
        if response_message.startswith('{'):
            json_str = response_message

    if json_str:
        try:
            tool_call = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(e)
             
    # Check if the model wants to call a tool
    try:
        tool_name = tool_call.get("tool_name")
        
        if tool_name in available_tools:
            print("\n--- Tool Call Detected ---")
            print(f"Tool: {tool_name}")
            print(f"Parameters: {tool_call.get('parameters')}")
            
            # Execute the function
            function_to_call = available_tools[tool_name]
            tool_params = tool_call.get("parameters", {})
            function_response = function_to_call(**tool_params)
            
            print("\n--- Tool Response ---")
            print(function_response)
            
            # (Optional) Send the result back to the model for a final summary
            messages.append({"role": "assistant", "content": response_message})
            messages.append({"role": "tool", "content": function_response})
            
            print("\n--- Final Response from Model ---")
            final_completion = client.chat.completions.create(
                model="local-model",
                messages=messages,
                temperature=0.7,
            )
            print(final_completion.choices[0].message.content)
            
        else:
            # The JSON doesn't match our tool schema
            print("\n--- Assistant Response (No Tool) ---")
            print(response_message)

    except json.JSONDecodeError:
        # The response was not JSON, so it's a direct answer
        print("\n--- Assistant Response (No Tool) ---")
        print(response_message)


# --- Run Examples ---
run_conversation("What's the weather like in Tokyo in celsius?")
print("\n" + "="*50 + "\n")
run_conversation("What is the capital of France?")
```

The output using LM Studio with the model **google/gemma-3n-e4b** looks like:

```console
$ uv run weather_tool.py
--- User Question ---
What's the weather like in Tokyo in celsius?

--- Tool Call Detected ---
Tool: get_weather
Parameters: {'city': 'Tokyo', 'unit': 'celsius'}

--- Tool Response ---
{"city": "Tokyo", "temperature": "25", "unit": "celsius"}

--- Final Response from Model ---
The weather in Tokyo is 25 degrees Celsius.

==================================================

--- User Question ---
What is the capital of France?

--- Assistant Response (No Tool) ---
Paris is the capital of France.
```

We started with a simple example so you understand the low-level process of supporting tool calling/function calling. In the next section we will generalize this example into a separate library and an example that uses this example.

## Creating a General Purpose Tools/Function Calling Library

