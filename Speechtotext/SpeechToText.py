import os
import subprocess
try:
    import mtranslate as mt
except ModuleNotFoundError:
    subprocess.run("pip install mtranslate")
    import mtranslate as mt

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options   
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

Username = env_vars.get("Username")

InputLanguage = "en-IN"

HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

with open(r"user_data\Voice.html", "w") as f:
    f.write(HtmlCode)

current_dir = os.getcwd()

Link = f"{current_dir}/user_data/Voice.html"

chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = [
    "how", "what", "who", "where", "when", "why", "which", "whom", "whose", "can you", "what's", "where's", "how's", "can you", "what is", "who is", "where is"
    ]

    if any(word + ' ' in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + '?'
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + '.'
        else:
            new_query += "."

    return new_query

def UnivarsalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

def listen():
    driver.get("file:///" + Link)
    driver.find_element(by=By.ID, value="start").click()

    old_text = ""
    
    while True:
        try:
            Text = driver.find_element(by=By.ID, value="output").text

            if Text and Text != old_text:
                old_text = Text  # Update old text so same result doesn't repeat

                driver.find_element(by=By.ID, value="end").click()

                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    with open(r"user_data\input.txt", "w") as file:
                        file.write(Text.lower())
                    print(QueryModifier(Text))
                else:
                    print(QueryModifier(UnivarsalTranslator(Text)))

                # Restart listening
                driver.find_element(by=By.ID, value="start").click()

        except Exception as e:
            pass


if __name__ == "__main__":
    listen()