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
