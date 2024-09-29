import os 
import tempfile
import threading
import subprocess
from playsound import playsound                 # pip install playsound==1.2.2

def speak(text:str,voice: str='en-US-JennyNeural')->None:
    try:
        with tempfile.NamedTemporaryFile(delete=False,suffix='.mp3') as tempfile:
            output_file = tempfile.name

            command = f'edge-tts --voice {voice} --text "{text}" --write-media {output_file}'

            subprocess.run(command,shell=True,check=True)

            threading.Thread(target=playsound,args=(output_file,)).start()

    except Exception as e:
        print(e)


