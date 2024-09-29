import pyautogui

def scroll_up():
    pyautogui.press('up')
    pyautogui.press('up')
    pyautogui.press('up')
    pyautogui.press('up')
    pyautogui.press('up')

def scroll_down():
    pyautogui.press('down')
    pyautogui.press('down')
    pyautogui.press('down')
    pyautogui.press('down')
    pyautogui.press('down')

def scroll_to_top():
    pyautogui.hotkey('home')

def scroll_to_bottom():
    pyautogui.hotkey('end')

def perform_scroll_action(text):
    if "scroll up" in text or "upar scroll karo" in text:  # Scroll up
        scroll_up()
    elif "scroll down" in text or "neeche scroll karo" in text:  # Scroll down
        scroll_down()
    elif "scroll to top" in text or "shuruaat mein scroll karo" in text:  # Scroll to top
        scroll_to_top()
    elif "scroll to bottom" in text or "ant tak scroll karo" in text:  # Scroll to bottom
        scroll_to_bottom()
    else:
        pass
