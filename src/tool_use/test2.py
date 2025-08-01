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
