import time
import subprocess
import pyautogui as gui  # pip install pyautogui

def open_app(text):
    try:      
        subprocess.run(text)
    except Exception as e:
        gui.press("win")
        time.sleep(0.2)
        gui.write(text)
        time.sleep(0.2)
        gui.press("enter")
