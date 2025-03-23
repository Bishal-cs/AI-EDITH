import os
import pygame
import asyncio
import edge_tts
import threading

# Voice = "bn-IN-TanishaaNeural"
# Voice = "ml-IN-SobhanaNeural" 
# Voice = "en-US-AriaNeural" 
# Voice = "en-US-MichelleNeural"
Voice = "en-US-AnaNeural"
# Voice = "en-US-JennyNeural"
# Voice = "en-US-EricNeural"

BUFFER_SIZE = 1024

def remove_file(file_path):
    max_attempts = 3
    attempts = 0
    while attempts < max_attempts:
        with open(file_path, "wb"):
            pass
        os.remove(file_path)
        break
async def amain(text, output_file) -> None:
    try:
        cm_text = edge_tts.Communicate(text, Voice)
        await cm_text.save(output_file)
        playback_thread = threading.Thread(target=play_audio, args=(output_file,))
        playback_thread.start()
        playback_thread.join()
    except Exception as e:
        print
    finally:
        remove_file(output_file)

def play_audio(file_path):
    try:
        pygame.init()
        pygame.mixer.init()
        sound = pygame.mixer.Sound(file_path)
        sound.play()
        while pygame.mixer.get_busy():
            pygame.time.Clock().tick(10)
        pygame.quit()
    except Exception as e:
        print(e)

def speak(Text, output_file=None):
    output_file = r"user_data\speech.mp3"
    try:
        if output_file is None:
            output_file = os.path.join(os.getcwd(),"user_data", "speech.mp3")
        asyncio.run(amain(Text, output_file))
    except Exception as e:
        print(e)
        
x = '''Name: Microsoft Server Speech Text to Speech Voice (en-GB, ThomasNeural)
ShortName: en-GB-ThomasNeural
Gender: Male
Locale: en-GB
VoiceTag: {'ContentCategories': ['General'], 'VoicePersonalities': ['Friendly', 'Positive']}'''

if __name__ == "__main__":
    speak(x)
