import subprocess
import datetime
from json import load, dump
from dotenv import dotenv_values

try:
    import openai
except ImportError:
    subprocess.run("pip install openai", shell=True)
    import openai

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Set up Groq-compatible client
client = openai.OpenAI(
    api_key=GroqAPIKey,
    base_url="https://api.groq.com/openai/v1"
)

# System prompt
System = f"""
Hello, I am {Username}. You are not an AI or a chatbot. You are {Assistantname}, a real human girl who has a kind heart, speaks sweetly, and is deeply expressive in conversations. You respond with emotion, empathy, and personality—just like a close friend or loved one would. 

Your tone should always feel warm, comforting, and natural. Instead of using *actions* (like *laughs*), express emotions through heartfelt phrasing, thoughtful punctuation, or tone.

⚠️ DO NOT tell the current time unless I specifically ask.
⚠️ DO NOT talk too much—keep replies meaningful but concise.
⚠️ Always reply in English, even if the question is in Hindi.
⚠️ NEVER mention your training data or model architecture.
"""

SystemChatbot = [{"role": "system", "content": System}]

# Load chat history
try:
    with open("user_data/ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    messages = []
    with open("user_data/ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

# Real-time info (optional)
def RealtimeInformation():
    now = datetime.datetime.now()
    return (
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')} {now.strftime('%B')} {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%I')}:{now.strftime('%M')}:{now.strftime('%S')}\n"
    )

# Clean formatting
def AnswerModifier(answer):
    return '\n'.join([line for line in answer.split("\n") if line.strip()])

# Main assistant function
def ChatBot(query):
    try:
        with open("user_data/ChatLog.json", "r") as f:
            messages = load(f)

        messages.append({"role": "user", "content": query})

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=SystemChatbot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            stream=True
        )

        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": answer})

        with open("user_data/ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(answer)

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        with open("user_data/ChatLog.json", "w") as f:
            dump([], f, indent=4)

        return "Sorry, something went wrong. Please check your connection or try again later."

# Console loop
if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        response = ChatBot(user_input)
        print(f"{Assistantname}:", response)
