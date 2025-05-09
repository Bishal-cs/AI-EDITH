import subprocess
from groq import Groq
from dotenv import dotenv_values
import os

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

messages = []

SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ['Username']}, You're a content writer. You have to write content like letter"}]

def Content(Topic):
    # This function will open note pad on our system 
    def OpenNotepad(File): 
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=SystemChatBot + messages,
            max_tokens=2048, 
            temperature=0.7, 
            top_p=1, 
            stream=True,
            stop=None 
        )
        
        Answer = "" 

        for chunk in completion:
            if chunk.choices[0].delta.content: 
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer
    
    Topic: str = Topic.replace("Content ", "")
    ContentByAI = ContentWriterAI(Topic)

    with open(rf"user_data\{Topic.lower().replace(' ', '')}.txt", "w", encoding = "utf-8") as file:
        file.write(ContentByAI)
        file.close
    
    OpenNotepad(rf"user_data\{Topic.lower().replace(' ', '')}.txt")
    return True 