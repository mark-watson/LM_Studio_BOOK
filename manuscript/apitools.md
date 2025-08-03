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

This Python code in the file **tool_use/function_calling_library.py** provides a lightweight and flexible framework for integrating external functions as "tools" with a large language model (LLM), such as one hosted locally with a tool like LM Studio. It defines two primary classes: **ToolManager**, which handles the registration and schema generation for available tools, and **ConversationHandler**, which orchestrates the multi-step interaction between the user, the LLM, and the tools. This approach allows the LLM to decide when to call a function, execute it within the Python environment, and then use the result to formulate a more informed and capable response.

```python
import json
import re
import inspect
from openai import OpenAI

class ToolManager:
    """
    Manages the registration and formatting of tools for the LLM.
    """
    def __init__(self):
        """Initializes the ToolManager with empty dictionaries for tools."""
        self.tools_schema = {}
        self.available_tools = {}

    def register_tool(self, func):
        """
        Registers a function as a tool, extracting its schema from the
        docstring and signature.
        
        Args:
            func (function): The function to be registered as a tool.
        """
        tool_name = func.__name__
        self.available_tools[tool_name] = func

        # Extract description from docstring
        description = "No description found."
        docstring = inspect.getdoc(func)
        if docstring:
            description = docstring.strip().split('\n\n')[0]

        # Extract parameters from function signature
        sig = inspect.signature(func)
        parameters = []
        for name, param in sig.parameters.items():
            param_type = "string" # Default type
            if param.annotation is not inspect.Parameter.empty:
                # A simple way to map Python types to JSON schema types
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
            
            # Simple docstring parsing for parameter descriptions (assumes "Args:" section)
            param_description = ""
            if docstring:
                arg_section = re.search(r'Args:(.*)', docstring, re.DOTALL)
                if arg_section:
                    param_line = re.search(rf'^\s*{name}\s*\(.*?\):\s*(.*)',
                                           arg_section.group(1), re.MULTILINE)
                    if param_line:
                        param_description = param_line.group(1).strip()

            parameters.append({
                "name": name,
                "type": param_type,
                "description": param_description
            })

        self.tools_schema[tool_name] = {
            "tool_name": tool_name,
            "description": description,
            "parameters": parameters
        }

    def get_tools_for_prompt(self):
        """
        Formats the registered tools' schemas into a JSON string for the system prompt.

        Returns:
            str: A JSON string representing the list of available tools.
        """
        if not self.tools_schema:
            return "No tools available."
        return json.dumps(list(self.tools_schema.values()), indent=4)

class ConversationHandler:
    """
    Handles the conversation flow, including making API calls and executing tools.
    """
    def __init__(self, client: OpenAI, tool_manager: ToolManager,
                 model: str = "local-model", temperature: float = 0.1):
        """
        Initializes the ConversationHandler.

        Args:
            client (OpenAI): The OpenAI client instance.
            tool_manager (ToolManager): The ToolManager instance with registered tools.
            model (str): The model name to use (ignored by LM Studio).
            temperature (float): The sampling temperature for the model.
        """
        self.client = client
        self.tool_manager = tool_manager
        self.model = model
        self.temperature = temperature

    def _create_system_prompt(self):
        """Creates the system prompt with tool definitions."""
        return f"""
You are a helpful assistant with access to the following tools.
To use a tool, you must respond with a JSON object with two keys: "tool_name" and "parameters".

Here are the available tools:
{self.tool_manager.get_tools_for_prompt()}

If you decide to use a tool, your response MUST be only the JSON object.
If you don't need a tool, answer the user's question directly.
"""

    def run(self, user_prompt: str, verbose: bool = True):
        """
        Runs the full conversation loop for a single user prompt.

        Args:
            user_prompt (str): The user's question or command.
            verbose (bool): If True, prints detailed steps of the conversation.
        """
        system_prompt = self._create_system_prompt()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        if verbose:
            print("--- User Question ---")
            print(user_prompt)

        # --- First API Call: Check for tool use ---
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )
        response_message = completion.choices[0].message.content

        # --- Parse for Tool Call ---
        tool_call = self._parse_tool_call(response_message)

        if tool_call and tool_call.get("tool_name") in self.tool_manager.available_tools:
            tool_name = tool_call["tool_name"]
            tool_params = tool_call.get("parameters", {})
            
            if verbose:
                print("\n--- Tool Call Detected ---")
                print(f"Tool: {tool_name}")
                print(f"Parameters: {tool_params}")

            # --- Execute the Tool ---
            function_to_call = self.tool_manager.available_tools[tool_name]
            try:
                function_response = function_to_call(**tool_params)
            except Exception as e:
                function_response = f"Error executing tool: {e}"

            if verbose:
                print("\n--- Tool Response ---")
                print(function_response)

            # --- Second API Call: Summarize the result ---
            messages.append({"role": "assistant", "content": json.dumps(tool_call, indent=4)})
            messages.append({"role": "tool", "content": str(function_response)})
            
            messages.append({
                "role": "user", 
                "content": "Based on the result from the tool, please formulate a final answer to the original user question."
            })

            if verbose:
                print("\n--- Final Response from Model ---")
            
            final_completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7, # Higher temp for more natural language
            )
            final_response = final_completion.choices[0].message.content
            print(final_response)
        else:
            # --- No Tool Call Detected ---
            if verbose:
                print("\n--- Assistant Response (No Tool) ---")
            print(response_message)

    def _parse_tool_call(self, response_message: str) -> dict | None:
        """
        Parses the model's response to find and decode a JSON tool call.

        Args:
            response_message (str): The raw response content from the model.

        Returns:
            dict or None: A dictionary representing the tool call, or None if not found.
        """
        json_str = None
        # Use regex to find JSON within ```json ... ``` or ``` ... ```
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_message, re.DOTALL)
        if match:
            json_str = match.group(1)
        # If no markdown block, check if the whole message is a JSON object
        elif response_message.strip().startswith('{'):
            json_str = response_message

        if json_str:
            try:
                # Clean up the JSON string before parsing
                cleaned_json_str = json_str.strip()
                return json.loads(cleaned_json_str)
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e} in string '{cleaned_json_str}'")
                return None
        return None
```

The first class, **ToolManager**, serves as a registry for the functions you want to expose to the LLM. Its core method, `register_tool`, uses Python's `inspect` module to dynamically analyze a function's signature and docstring. It extracts the function's name, its parameters (including their type hints), and their descriptions from the "Args" section of the docstring. This information is then compiled into a JSON schema that describes the tool in a machine-readable format. This automated process is powerful because it allows a developer to make a standard Python function available to the LLM simply by adding it to the manager, without manually writing complex JSON schemas.

The second class, **ConversationHandler**, is the engine that drives the interaction. When its `run` method is called, it first constructs a detailed **system prompt**. This special prompt instructs the LLM on how to behave and includes the JSON schemas for all registered tools, informing the model of its capabilities. The user's question is then sent to the LLM. The model's first task is to decide whether to answer directly or to use one of the provided tools. If it determines a tool is necessary, it is instructed to respond *only* with a JSON object specifying the `tool_name` and the `parameters` needed to run it.

The process concludes with a crucial **two-step execution logic**. If the `ConversationHandler` receives a valid JSON tool call from the LLM, it executes the corresponding Python function with the provided parameters. The return value from that function is then packaged into a new message with the role "tool" and sent back to the LLM in a second API call. This second call prompts the model to synthesize the tool's output into a final, natural-language answer for the user. If the model's initial response was not a tool call, the system assumes no tool was needed and simply presents that response directly to the user. This conditional, multi-step approach enables the LLM to leverage external code to answer questions it otherwise couldn't.


### First example Using Function Calling Library: Generate Python and Execute to Answer User Questions

This Python script in the file **tool_use/test1.py** demonstrates a practical implementation of the **function_calling_library** by creating a specific tool designed to solve mathematical problems. It defines a function, solve_math_problem, that can execute arbitrary Python code in a secure, isolated process. The main part of the script then initializes the ToolManager and ConversationHandler from the library, registers the new math tool, and runs two example conversations: one that requires complex calculation, thereby triggering the tool, and another that is a general knowledge question, which the LLM answers directly.


```python
import os
import subprocess
import json
from openai import OpenAI
from function_calling_library import ToolManager, ConversationHandler

# --- Define the Custom Tool ---

def solve_math_problem(python_code: str):
    """
    Executes a given string of Python code to solve a math problem and returns the output.
    The code should be a complete, runnable script that prints the final result to standard output.

    Args:
        python_code (str): A string containing the Python code to execute.
    """
    temp_filename = "temp.py"
    
    # Ensure any previous file is removed
    if os.path.exists(temp_filename):
        os.remove(temp_filename)

    try:
        # Write the code to a temporary file
        with open(temp_filename, "w") as f:
            f.write(python_code)
        
        # Execute the python script as a separate process
        result = subprocess.run(
            ['python', temp_filename], 
            capture_output=True, 
            text=True, 
            check=True, # This will raise CalledProcessError if the script fails
            timeout=10 # Add a timeout for safety
        )
        
        # The output from the script's print() statements
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        # If the script has a runtime error, return the error message
        error_message = f"Error executing the Python code:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        return error_message
    except Exception as e:
        return f"An unexpected error occurred: {e}"
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)


# --- Main Execution Logic ---

if __name__ == "__main__":
    # Point to the local LM Studio server
    client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
    
    # 1. Initialize the ToolManager
    tool_manager = ToolManager()
    
    # 2. Register the custom tool
    tool_manager.register_tool(solve_math_problem)
    
    # 3. Initialize the ConversationHandler with the client and tools
    handler = ConversationHandler(client, tool_manager)
    
    # 4. Define a user prompt that requires the tool
    user_prompt = "Can you please calculate the area of a circle with a radius of 7.5 and also find the 20th number in the Fibonacci sequence? Please provide the Python code to do this."
    
    # 5. Run the conversation
    handler.run(user_prompt)

    print("\n" + "="*50 + "\n")

    # Example of a question that should NOT use the tool
    non_tool_prompt = "What is the most popular programming language?"
    handler.run(non_tool_prompt)
```

The core of this script is the `solve_math_problem` function, which serves as the custom tool. It's designed to safely execute a string of Python code passed to it by the LLM. To avoid security risks associated with `eval()` or `exec()`, it writes the code to a temporary file (`temp.py`). It then uses Python's `subprocess` module to run this file as an entirely separate process. This sandboxes the execution, and the `capture_output=True` argument ensures that any output printed by the script (e.g., the result of a calculation) is captured. The function includes robust error handling, returning any standard error from the script if it fails, and a `finally` block to guarantee the temporary file is deleted, maintaining a clean state.

Please note that code generated my the LLM is not fully sandboxed and this approach is tailored to personal development environments. For production consider running the generated code in a container.

The main execution block, guarded by `if __name__ == "__main__"`, orchestrates the entire demonstration. It begins by configuring the `OpenAI` client to connect to a local server, such as LM Studio. It then instantiates the `ToolManager` and registers the `solve_math_problem` function as an available tool. With the tool ready, it creates a `ConversationHandler` to manage the flow. The script then showcases the system's decision-making ability by running two different prompts. The first asks for two distinct mathematical calculations, a task that perfectly matches the `solve_math_problem` tool's purpose. The second prompt is a general knowledge question that requires no calculation, demonstrating the LLM's ability to differentiate between tasks and answer directly when a tool is not needed.

Sample output:

```console
$ uv run test1.py              
--- User Question ---
Can you please calculate the area of a circle with a radius of 7.5 and also find the 20th number in the Fibonacci sequence? Please provide the Python code to do this.

--- Tool Call Detected ---
Tool: solve_math_problem
Parameters: {'python_code': 'import math\nradius = 7.5\narea = math.pi * radius**2\nprint(area)\n\ndef fibonacci(n):\n  if n <= 0:\n    return 0\n  elif n == 1:\n    return 1\n  else:\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n      a, b = b, a + b\n    return b\n\nprint(fibonacci(20))'}

--- Tool Response ---
176.71458676442586
6765

--- Final Response from Model ---
The area of a circle with a radius of 7.5 is approximately 176.7146, and the 20th number in the Fibonacci sequence is 6765.


==================================================

--- User Question ---
What is the most popular programming language?

--- Assistant Response (No Tool) ---
Python is generally considered the most popular programming language.
```

TBD

### Second example Using Function Calling Library: Stub of Weather API

This script in the file **tool_use/test2.py** provides another clear example of how the **function_calling_library** can be used to extend an LLM's capabilities, this time by simulating an external data fetch from a weather API. It defines a simple get_weather function that returns mock data for specific cities. The main execution logic then sets up the ConversationHandler, registers this new tool, and processes two distinct user prompts to demonstrate the LLM's ability to intelligently decide when to call the function and when to rely on its own knowledge base.


```python
import json
from openai import OpenAI
from function_calling_library import ToolManager, ConversationHandler

# --- Define the Custom Tool ---

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

# --- Main Execution Logic ---

if __name__ == "__main__":
    # Point to the local LM Studio server
    client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
    
    # 1. Initialize the ToolManager
    tool_manager = ToolManager()
    
    # 2. Register the custom tool
    tool_manager.register_tool(get_weather)
    
    # 3. Initialize the ConversationHandler with the client and tools
    handler = ConversationHandler(client, tool_manager)
    
    # 4. Define a user prompt that requires the tool
    user_prompt = "What's the weather like in Tokyo in celsius?"
    
    # 5. Run the conversation
    handler.run(user_prompt)

    print("\n" + "="*50 + "\n")

    # Example of a question not using tool calling:
    another_prompt = "What do Chicago and Tokyo have in common? Provide a fun answer."
    handler.run(another_prompt)
```

The custom tool in this example is the `get_weather` function. It is defined with clear parameters, `city` and `unit`, and includes type hints and a docstring that the `ToolManager` will use to automatically generate its schema. Instead of making a live call to a weather service, this function contains simple conditional logic to return hardcoded JSON strings for "Chicago" and "Tokyo," or an error if another city is requested. This mock implementation is a common and effective development practice, as it allows you to build and test the entire function-calling logic without depending on external network requests or API keys. The function's return value is a JSON string, which is a standard data interchange format easily understood by both the Python environment and the LLM.

The main execution block follows the same clear, step-by-step pattern as the previous example. It configures the client, initializes the `ToolManager`, and registers the `get_weather` function. After setting up the `ConversationHandler`, it runs two test cases that highlight the system's contextual awareness. The first prompt, "What's the weather like in Tokyo in celsius?", directly maps to the functionality of the `get_weather` tool, and the LLM correctly identifies this and generates the appropriate JSON tool call. The second prompt, which asks for commonalities between the two cities, is a conceptual question outside the tool's scope. In this case, the LLM correctly bypasses the tool-calling mechanism and provides a direct, creative answer from its own training data, demonstrating the robustness of the overall approach.

Sample output:

```console
$ uv run test2.py
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
What do Chicago and Tokyo have in common? Provide a fun answer.

--- Assistant Response (No Tool) ---
Chicago and Tokyo both have amazing food scenes! Chicago is famous for deep-dish pizza, while Tokyo is known for its incredible sushi and ramen. Both cities are culinary adventures! 🍕🍜
```

