import subprocess
try:
    import pyttsx3                                                  #For text to speech download "pip install pyttsx3"
except ModuleNotFoundError:
    subprocess.run("pip install pyttsx3")

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":   
    speak("Hello edith how are you?")