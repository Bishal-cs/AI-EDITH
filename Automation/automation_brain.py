import time
import threading
import pywhatkit
from os import getcwd
import pyautogui as gui 
from TextToSpeech import F_DF_TTS
from TextToSpeech.F_DF_TTS import speak
from Automation.open_app import open_app, close_app
from Automation.Battery import chekc_Percentage
from Automation.play_music_yt import play_music_youtube
from Automation.scroll_system import perform_scroll_action
from Automation.tab_automation import perform_browser_action
from Automation.youtube_playback import perform_video_control
from Automation.play_music_soprtify import play_music_on_spotify

INPUT_FILE_PATH = 'user_data/input.txt'

def play():
    gui.press("space")

def sleep_dev():
    gui.hotkey('win', 'x')
    gui.press('u')
    time.sleep(1)
    gui.press('s')

def search_google(text):
    pywhatkit.search(text)

def search(text):
    gui.press('/')
    time.sleep(0.3)
    gui.write(text)

# for opening applications and websites if the app not found
def open_brain(app):
    app = app.replace("open", "").strip()
    t2 = threading.Thread(target=open_app, args=(app,))
    t1 = threading.Thread(target=speak, args=(f"Navigating {app}",))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

# close applications only if the app found
def close_application(apps):
    apps = apps.replace("close", "").strip()
    t2 = threading.Thread(target=close_app, args=(apps,))
    t1 = threading.Thread(target=speak, args=(f"Closing {apps}",))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

def clear_file():
    with open(INPUT_FILE_PATH, "w") as file:
        file.truncate(0)

def Auto_main_brain(text):
    if text.startswith("open"):
        open_brain(text)
    
    elif text.startswith("close"):
        close_application(text)

    elif "play music" in text or "play music on youtube" in text:
        F_DF_TTS.speak("Which song do you want to play,sir?")
        output_text = ""
        clear_file()
        while True:
            with open(INPUT_FILE_PATH, "r") as file:
                input_text = file.read().lower()
            if input_text != output_text:
                output_text = input_text
                if output_text.endswith("song"):
                    play_music_youtube(output_text)
                    break

    elif "play some music" in text or "play music on spotify" in text:
        F_DF_TTS.speak("Which song do you want to play, sir?")
        # Clears the content of the input file
        output_text = ""
        clear_file()
        while True:
            with open(INPUT_FILE_PATH, "r") as file:
                input_text = file.read().lower()
            if input_text != output_text:
                output_text = input_text
                if output_text.endswith("song"):
                    play_music_on_spotify(output_text)
                    break

    elif "check battery" in text or "battery percentage" in text:
        chekc_Percentage()

    elif text.startswith("search"):
        text = text.replace("search", "").strip()
        t1 = threading.Thread(target=speak, args=(f"doing research about {text}",))
        t2 = threading.Thread(target=search, args=(text,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        gui.press('enter')

    elif "search in google" in text:
        text = text.replace("search in google", "").strip()
        t1 = threading.Thread(target=speak, args=(f"Performing search in {text} ",))
        t2 = threading.Thread(target=search_google, args=(text,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    elif "stop this" in text or "resume this" in text:
        play()

    elif "go sleep" in text or "go sleep mode" in text:
        sleep_dev()
        
    else:
        perform_browser_action(text)
        perform_video_control(text)
        perform_scroll_action(text)

if __name__ == "__main__":
    while True:
        text = input("User> ")
        open_brain(text)