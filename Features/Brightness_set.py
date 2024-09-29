import wmi
from TextToSpeech.F_DF_TTS import speak

def set_brightness_windows(percentage):
    try:
        w = wmi.WMI(namespace='wmi')
        brightness_methods = w.WmiMonitorBrightnessMethods()[0]
        brightness_methods.WmiSetBrightness(int(percentage), 0)
        speak(f"Brightness set to {percentage}%")
    except Exception as e:
        speak(f"Error: {e}")

def get_brightness_windows():
    try:
        w = wmi.WMI(namespace='wmi')
        brightness_methods = w.WmiMonitorBrightness()
        brightness_percentage = brightness_methods[0].CurrentBrightness
        return brightness_percentage
    except Exception as e:
        return f"Error: {e}"

def check_br_persentage():
    brightness = get_brightness_windows()
    speak(f"Current Brightness: {brightness}%")
