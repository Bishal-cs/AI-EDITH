from Brain.brain import ChatBot
from Speechtotext.SpeechToText import SpeechRecognition
from TextToSpeech.F_DF_TTS import speak

def main():
    while True:
        print("Listening...")
        speech = SpeechRecognition()
        print("User:", speech)
        response = ChatBot(speech)
        print("AI:",response, "\n")
        speak(response)
main()


# def trancationg_input():
#     with open("Data/input.txt","w") as file:
#         file.truncate(0)

# def check_inputs():
#     output_text = ""
#     while True:
#         with open("Data/input.txt","r") as file:
#             input_text = file.read().lower() 
#         if input_text != output_text:
#             output_text = input_text
#             if "edit" in output_text or "hey edit" in output_text: 
#                 response = ChatBot(output_text)
#                 print("AI:",response)
#                 speak(response)
#                 trancationg_input()
#             else:
#                 pass
#         else:
#             pass

# def main():
#     t1 = threading.Thread(target = check_inputs)
#     t2 = threading.Thread(target = listen)
#     t1.start()
#     t2.start()
#     t1.join()
#     t2.join()

# main()