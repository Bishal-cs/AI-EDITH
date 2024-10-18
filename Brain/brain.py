import os
import time 
from webscout import PhindSearch

history_file = r"C:\Users\bisha\Desktop\AI-EDITH\chat_history.txt"

def load_history():
    if os.path.exists(history_file):
        with open(history_file, 'r') as file:
            return file.read()
    return ""

def save_history(history):
    with open(history_file, 'w') as file:
        file.write(history)

# Load existing history
conversation_history = load_history()

ai = PhindSearch(
    is_conversation=True,
    max_tokens=800,
    timeout=30,
    intro= None,
    filepath= None,
    update_file= False, 
    proxies={},
    history_offset=10250,
    act=None,
)

def Main_Brain(text):
    conversation_history = load_history()
    # Append the prompt to the conversation history
    conversation_history += f"\nUser: {text}"
    
    # Generate the full prompt including the conversation history
    full_prompt = conversation_history + "\nAI:"
    
    # Get the AI's response
    response_chunks = []
    for chunk in ai.chat(full_prompt):
        response_chunks.append(chunk)
        
    # Combine the response chunks into a single response
    response_text = "".join(response_chunks)
    
    # Append the AI's response to the conversation history
    conversation_history += f"\nAI: {response_text}"
    
    # Check if the user input contains "remember this"
    if "remember this" in text.lower():
        # Save the updated conversation history
        save_history(conversation_history)
    return response_text