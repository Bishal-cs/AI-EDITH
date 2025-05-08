from Brain.brain import ChatBot
from Speechtotext.ListenFN import listen
from TextToSpeech.F_DF_TTS import speak

def speech():
    while True:
        speech = listen()
        speech = speech.strip().lower().strip(".")
        if speech == "q" or speech == "exit":
            break
        print("User:", speech)
        response = ChatBot(speech)
        print("AI:",response, "\n")
        speak(response)

def Text():
    while True:
        print("Type to start the conversation")
        Text = input("Bot> ")
        if Text == "q" or Text == "exit":
            break
        response = ChatBot(Text)
        print("AI:",response, "\n")
        speak(response)

def main():
    while True:
        ip = input("Press s to speak and press t to text ").lower()
        if ip == "s":
            speech()
        elif ip == "t":
            Text()
        else:
            print("Invalid input")
main()