import subprocess 
try:
    from groq import Groq
except ImportError:
    subprocess.run("pip install groq")
    from groq import Groq
from json import load, dump
import datetime

# Change Your name 
Username = "Bishal"
# Change Your Assistant name
Assistantname = "EDITH"
GroqAPIKey = "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"

client = Groq(api_key=GroqAPIKey)

messages = []

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatbot = [
    {"role": "system", "content": System}
]

try: 
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")      
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%I")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Please use this rea;-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours : {minute} minutes : {second} seconds\n"

    return data

def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    
    return modified_answer

def ChatBot(Query):
    """This function send the user's query to the chatbot and returns the AI's response."""
    try:
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)
        
        messages.append({"role": "user", "content": f"{Query}"})
        
        completion = client.chat.completions.create(
            model = "llama3-70b-8192",
            messages = SystemChatbot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature = 0.7,
            top_p = 1,
            stream=True,
            stop=None
        )

        Answer = ""

        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        
        Answer = Answer.replace("</s>", "")

        messages.append({"role": "assistant", "content": Answer})

        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer=Answer)

    except Exception as e:
        print(f"Error: {e}")
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return ChatBot(Query)

if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        print(ChatBot(user_input))