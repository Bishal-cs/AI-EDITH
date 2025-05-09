from Brain.brain import ChatBot
from Speechtotext.STT_5 import listen
from TextToSpeech.F_DF_TTS import speak

def speech():
    print("🎤 Speak mode active. Say 'exit' or 'q' to quit.\n")
    while True:
        try:
            user_input = listen().strip().lower().strip(".")
            if user_input in ["q", "exit"]:
                break
            print("You:", user_input)
            response = ChatBot(user_input)
            print("RAI:", response, "\n")
            if response:
                speak(response)
        except Exception as e:
            print(f"[Error in speech mode]: {e}")

def text():
    print("💬 Text mode active. Type 'exit' or 'q' to quit.\n")
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["q", "exit"]:
                break
            response = ChatBot(user_input)
            print("RAI:", response, "\n")
            if response:
                speak(response)
        except Exception as e:
            print(f"[Error in text mode]: {e}")

def main():
    print("Welcome to RAI 🧠")
    print("Choose input method:\n - Press 's' for Speech\n - Press 't' for Text\n")
    while True:
        ip = input("Your choice (s/t): ").lower()
        if ip == "s":
            speech()
        elif ip == "t":
            text()
        else:
            print("❌ Invalid input. Please press 's' or 't'.\n")

if __name__ == "__main__":
    main()
