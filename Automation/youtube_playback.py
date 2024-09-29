import pyautogui

def volume_up():
    pyautogui.press('up')

def volume_down():
    pyautogui.press('down')

def seek_forward():
    pyautogui.press('right')

def seek_backward():
    pyautogui.press('left')

def seek_forward_10s():
    pyautogui.press('l')

def seek_backward_10s():
    pyautogui.press('j')

def seek_backward_frame():
    pyautogui.press(',')

def seek_forward_frame():
    pyautogui.press('.')

def seek_to_beginning():
    pyautogui.press('home')

def seek_to_end():
    pyautogui.press('end')

def seek_to_previous_chapter():
    pyautogui.hotkey('ctrl', 'left')

def seek_to_next_chapter():
    pyautogui.hotkey('ctrl', 'right')

def decrease_playback_speed():
    pyautogui.hotkey('shift', ',')

def increase_playback_speed():
    pyautogui.hotkey('shift', '.')

def move_to_next_video():
    pyautogui.hotkey('shift', 'n')

def move_to_previous_video():
    pyautogui.hotkey('shift', 'p')

def perform_video_control(text):
    if "volume up" in text or "volume badhao" in text:  # Increase volume
        volume_up()
    elif "volume down" in text or "volume ghatao" in text:  # Decrease volume
        volume_down()
    elif "seek forward" in text or "aage badhao" in text:  # Seek forward
        seek_forward()
    elif "seek backward" in text or "piche le jao" in text:  # Seek backward
        seek_backward()
    elif "seek forward 10 seconds" in text or "10 second aage badhao" in text:  # Seek forward 10s
        seek_forward_10s()
    elif "seek backward 10 seconds" in text or "10 second piche le jao" in text:  # Seek backward 10s
        seek_backward_10s()
    elif "seek forward frame" in text or "frame aage badhao" in text:  # Seek forward frame
        seek_forward_frame()
    elif "seek backward frame" in text or "frame piche le jao" in text:  # Seek backward frame
        seek_backward_frame()
    elif "seek to beginning" in text or "shuruaat mein le jao" in text:  # Seek to beginning
        seek_to_beginning()
    elif "seek to end" in text or "ant mein le jao" in text:  # Seek to end
        seek_to_end()
    elif "seek to previous chapter" in text or "pichle chapter mein jao" in text:  # Previous chapter
        seek_to_previous_chapter()
    elif "seek to next chapter" in text or "agle chapter mein jao" in text:  # Next chapter
        seek_to_next_chapter()
    elif "decrease playback speed" in text or "playback speed kam karo" in text:  # Decrease speed
        decrease_playback_speed()
    elif "increase playback speed" in text or "playback speed badhao" in text:  # Increase speed
        increase_playback_speed()
    elif "move to next video" in text or "agli video par jao" in text:  # Next video
        move_to_next_video()
    elif "move to previous video" in text or "pichli video par jao" in text:  # Previous video
        move_to_previous_video()
    else:
        pass
