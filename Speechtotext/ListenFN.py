
#  import speech_recognition as sr
# from os import getcwd

# save_file = f'{getcwd()}\\input.txt'

# def listen():
#     # Initialize recognizer
#     recognizer = sr.Recognizer()

#     # Use the microphone as the source for input
#     with sr.Microphone() as source:
#         print("Adjusting for ambient noise... Please wait.")
#         recognizer.adjust_for_ambient_noise(source, duration=2)  # Reduce noise adjustment time

#         print("Start speaking... (Press Ctrl+C to stop)")

#         try:
#             while True:
#                 print("Listening...")

#                 # Capture audio in small chunks
#                 audio = recognizer.listen(source, phrase_time_limit=5)  # Adjust phrase time limit

#                 try:
#                     # Convert speech to text using Google Web Speech API
#                     text = recognizer.recognize_google(audio)
#                     print(f"Detected Text: {text}")

#                     # Open the file in write mode to overwrite the previous text
#                     with open(save_file, 'w') as file:
#                         file.write(text)  # Write the latest recognized text
#                         file.flush()  # Ensure text is written to the file immediately

#                 except sr.UnknownValueError:
#                     print("Google Speech Recognition could not understand the audio.")
#                 except sr.RequestError as e:
#                     print(f"Could not request results from Google Speech Recognition service; {e}")

#         except KeyboardInterrupt:
#             print("Real-time speech recognition stopped.")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from os import getcwd

# Setting up Chrome options with specific arguments
chrome_options = Options()
chrome_options.add_argument("--headless=old")  # Remove this if you want to see the browser UI
chrome_options.add_argument("--use-fake-ui-for-media-stream")

# Manually set the path to the ChromeDriver executable
service = Service(ChromeDriverManager().install())

# Setting up the Chrome driver with the service and options
driver = webdriver.Chrome(service=service, options=chrome_options)

# Creating the URL for the website using the current working directory
website = "https://allorizenproject1.netlify.app/"

# Opening the website in the Chrome browser
driver.get(website)

Recog_File = f"{getcwd()}\\input.txt"

def listen():
    try:
        start_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'startButton')))
        start_button.click()
        print("Listening...")
        output_text = ""
        is_second_click = False
        while True:
            output_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'output')))
            current_text = output_element.text.strip()
            if "Start Listening" in start_button.text and is_second_click:
                if output_text:
                    is_second_click = False
            elif "Listening..." in start_button.text:
                is_second_click = True
            if current_text != output_text:
                output_text = current_text
                with open(Recog_File, "w") as file:
                    file.write(output_text.lower())
                    print("User:", output_text)
    except KeyboardInterrupt:
        print("Process interrupted by user.")
    except Exception as e:
        print("An error occurred:", e)
    finally:
        driver.quit()