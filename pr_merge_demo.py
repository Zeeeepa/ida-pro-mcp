import os

# Function to load text from prompt.py in the same directory
def load_prompt_from_file():
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to prompt.py
    prompt_path = os.path.join(current_dir, 'prompt.py')
    
    # Check if the file exists
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Prompt file not found at {prompt_path}")
    
    # Read the file content
    with open(prompt_path, 'r') as file:
        content = file.read()
    
    # Try to extract PROMPT_TEXT if it exists
    try:
        # This is a simple way to extract a variable from the file
        # It's not as robust as using importlib but works for simple cases
        import re
        match = re.search(r'PROMPT_TEXT\s*=\s*[\'"](.+?)[\'"]', content, re.DOTALL)
        if match:
            return match.group(1)
        else:
            return content
    except:
        # If any error occurs, just return the whole content
        return content

# Load the prompt text from prompt.py
prompt_text = load_prompt_from_file()
print(f"Loaded prompt: {prompt_text}")

# This is where you would use the prompt with the Codegen Agent
print("\nIn your actual script, you would then use this prompt with the Codegen Agent like this:")
print("agent = Agent(org_id='323', token='your-token')")
print("task = agent.run(prompt_text)")

