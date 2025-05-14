import os
import pygame
import asyncio
import edge_tts
import threading

Voice = "en-US-JennyNeural"  # Choose your voice
Output_File = "user_data/speech.wav"  # Single point to control file path

def remove_file(file_path):
    try:
        with open(file_path, "wb"):
            pass
        os.remove(file_path)
    except Exception as e:
        print("Error removing file:", e)

async def amain(text, rate="+10%", pitch="+0Hz") -> None:
    try:
        communicate = edge_tts.Communicate(
            text=text,
            voice=Voice,
            rate=rate,
            pitch=pitch
        )
        await communicate.save(Output_File)

        playback_thread = threading.Thread(target=play_audio)
        playback_thread.start()
        playback_thread.join()

    except Exception as e:
        print("Error in amain:", e)
    finally:
        remove_file(Output_File)

def play_audio():
    try:
        pygame.init()
        pygame.mixer.init()
        sound = pygame.mixer.Sound(Output_File)
        sound.play()
        while pygame.mixer.get_busy():
            pygame.time.Clock().tick(10)
        pygame.quit()
    except Exception as e:
        print("Error playing audio:", e)

def speak(text, rate="+10%", pitch="+0Hz"):
    try:
        asyncio.run(amain(text, rate, pitch))
    except Exception as e:
        print("Error in speak:", e)

if __name__ == "__main__":
    while True:
        x = input("Enter the text: ")
        if x.lower() in ["exit", "q"]:
            break
        speak(x, rate="+15%", pitch="+0Hz")  # Customize here if needed
