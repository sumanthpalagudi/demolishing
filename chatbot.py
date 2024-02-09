import re
import subprocess
import openai

# Set your OpenAI API key
conversation_history = []
def send_message_to_gpt3(user_input):
    """
    Send the user's input message to GPT-3.5 Turbo and receive the generated response.
    """
    # Define the prompt with user input
    conversation_history.append({"role": "user", "content": user_input})
    # Send the prompt to GPT-3.5 Turbo
    prompt = ""
    for message in conversation_history:
        prompt += f"{message['role'].capitalize()}: {message['content']}\n"
    response = openai.chat.completions.create(   
        model= "gpt-3.5-turbo", # Choose the GPT-3.5 Turbo engine
        messages=[{"role":"system","content":"you are expert in git,based on what they ask you have give them with commands that they should run on command line,and also don't use master use main,and also don't give examples for the commands"},  # The chat history between User and GPT-3.5
        {"role": "user", "content": prompt}]
    )
    conversation_history.append({"role": "system", "content": response.choices[0].message.content})
    # Extract and return the generated response
    git_commands = extract_git_commands(response.choices[0].message.content)
    

    git_responses=execute_git_commands(git_commands)
    for git_command, git_response in git_responses.items():
            conversation_history.append({"role": "system", "content": git_response})
    return response.choices[0].message.content
def extract_git_commands(response):
    """
    Extract Git commands from the GPT-3.5 Turbo response.
    """
    # Simple example: Extracting Git commands using a simple keyword search
    git_commands = [command.strip() for command in response.splitlines() if "git" in command.lower()]
    
    # Further filter out non-Git commands
    git_commands = [command for command in git_commands if command.startswith("git")]
    
    return git_commands

def execute_git_commands(git_commands):
    """
    Execute Git commands and prompt for necessary details.
    """
    print(git_commands)
    git_responses = {}
    for command in git_commands:
        try:
            # Prompt the user for relevant details
            placeholder_values = {}
            for placeholder in re.findall(r'<(.*?)>', command):
                placeholder_values[placeholder] = input(f"Enter {placeholder}: ")

            # Replace placeholders with user input
            formatted_command = command.format(**placeholder_values)
            print(formatted_command)
            if "git commit" in command.lower():
                # If it's a commit command, prompt the user for the commit message
                commit_message = input("Enter commit message: ")
                # Replace the commit message placeholder with the user input
                formatted_command = command.replace("Your commit message", commit_message)
            # Execute Git command using subprocess and capture output
            completed_process = subprocess.run(formatted_command, shell=True, capture_output=True, text=True)
            git_responses[formatted_command] = completed_process.stdout.strip()
            print(git_responses[formatted_command])
        except subprocess.CalledProcessError as e:
            git_responses[formatted_command] = f"Error executing Git command: {e}"
            continue
    return git_responses
def chatbot():
    """
    Simple chatbot function that interacts with the user.
    """
    print("Chatbot: Hello! I'm your chatbot assistant. How can I help you today?")

    while True:
        user_input = input("User: ")

        if user_input.lower() == 'exit':
            print("Chatbot: Goodbye!")
            break

        # Send user input to GPT-3.5 Turbo and get the response
        bot_response = send_message_to_gpt3(user_input)

        print("Chatbot:", bot_response)

if __name__ == "__main__":
    # Start the chatbot
    chatbot()
