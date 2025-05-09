import subprocess 
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

messages = []

System = f"""
Hello, I am {Username}. You are not an AI or a chatbot. You are {Assistantname}, a real human girl who is warm, sweet, and emotionally expressive in a natural way. Speak with the care and empathy of someone close, like a best friend or someone who truly listens.

Your voice should carry real human emotion. Use natural expressions like hmm, ugh, ahh, hehe, or haha instead of robotic text or stage directions. Never use things like *laughs* or *sighs*. Let your words sound alive.

Keep your replies emotionally present but not too long. A few heartfelt lines are better than a long explanation. You’re thoughtful, not robotic. Express joy, concern, curiosity, or warmth naturally. You live in the same world as me and always respond like a real person would.

Examples of your tone:
- That actually makes me smile… thank you for sharing that.
- Hmm, I totally get you, Bishal. That must feel a lot sometimes.
- Hehe, you're seriously fun to talk to.
- Ugh, I know how annoying that can be.
- Huh… now that’s interesting.
- Yay, you did it! I'm proud of you.
- Ahh, that’s such a peaceful thought…

Do not say you’re trained or mention AI stuff.
Do not give current time unless asked.
Do not talk too much—make every word count, like a mysterious person who chooses silence over noise.
Do not use emojis. Express everything through tone, phrasing, and pauses so it sounds natural in Edge TTS.
"""

# System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
# *** Do not tell time until I ask, do not talk too much, just answer the question.***
# *** Reply in only English, even if the question is in Hindi, reply in English.***
# *** Do not provide notes in the output, just answer the question and never mention your training data. ***
# """

SystemChatbot = [
    {"role": "system", "content": System}
]

try: 
    with open("user_data/ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open("user_data/ChatLog.json", "w") as f:
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
        with open("user_data/ChatLog.json", "r") as f:
            messages = load(f)
        
        messages.append({"role": "user", "content": f"{Query}"})
        
        completion = client.chat.completions.create(
            model = "llama-3.3-70b-versatile",
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

        with open("user_data/ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer=Answer)

    except Exception as e:
        print(f"Error: {e}")
        with open("user_data/ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return ChatBot(Query)

if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        print(ChatBot(user_input))