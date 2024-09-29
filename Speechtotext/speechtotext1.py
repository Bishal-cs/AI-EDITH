import os
import threading
import speech_recognition as sr                             # For use speech recognition download "pip install SpeechRecognition"
from mtranslate import translate                            # For translate download "pip install mtranslate"
from colorama import init,Fore,Style                        #for colorama download "pip install colorama"

init(autoreset=True)
def print_loop():
    while True:
            print(Fore.GREEN + "Listening...",end="",flush=True)
            print(Style.RESET_ALL, end="", flush=True)

def translate_Hindi_text(text):
    english_text = translate(text, 'en-in')
    return english_text

def listen():
    r = sr.Recognizer()
    r.dynamic_energy_threshold = False
    r.energy_threshold = 34000
    r.dynamic_energy_adjustment_damping = 0.010
    r.dynamic_energy_ratio = 1.0
    r.pause_threshold = 0.3
    r.operation_timeout = None
    r.pause_threshold = 0.2
    r.non_speaking_duration = 0.2

    with sr.Microphone() as source:                             #for couldn't find pyaudio error download "pip install pyaudio"
        r.adjust_for_ambient_noise(source)
        while True:
            print(Fore.GREEN + "Listening...",end="",flush=True)
            try:
                audio = r.listen(source,timeout=None)
                print("\r"+ Fore.LIGHTBLACK_EX + "Recognizing...",end="",flush=True)
                recognizer_text = r.recognize_google(audio).lower()
                if recognizer_text:
                    tr_text = translate_Hindi_text(recognizer_text)  #tr_text= Trancela_Text 
                    print("\r" + Fore.BLUE + "User: " + tr_text)
                    return tr_text
                else:
                    return ""
            except sr.UnknownValueError:
                recognizer_text = ""
            finally:
                print("\r",end="",flush=True)

            os.system('cls' if os.name == 'nt' else 'clear')

        stt_thread = threading.Thread(target=speech_to_text)
        print_thread = threading.Thread(target=print_loop)
        stt_thread.start()
        print_loop.start()
        stt_thread.join()
        print_loop.join()

listen()