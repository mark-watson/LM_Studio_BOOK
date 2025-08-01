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
