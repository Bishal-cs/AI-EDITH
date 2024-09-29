import pyttsx3                                                  #For text to speech download "pip install pyttsx3"


def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(text)
    engine.runAndWait()

speak("Hello edith how are you?")