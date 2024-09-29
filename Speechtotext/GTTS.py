import speech_recognition as sr

def transcribe_audio():
    while True:
        # Initialize the recognizer
        r = sr.Recognizer()

        # Read the input.txt file
        with open('input.txt', 'r') as f:
            text_to_speak = f.read().strip()

        # Use microphone as audio source
        with sr.Microphone() as source:
            print("Please say something:")
            audio = r.listen(source)

        try:
            # Convert speech to text
            result = r.recognize_google(audio)
            print(f"You said: {result}")

            # Compare the spoken words with the text in input.txt
            if result.lower() == text_to_speak.lower():
               pass
        except sr.UnknownValueError:
            pass

transcribe_audio()