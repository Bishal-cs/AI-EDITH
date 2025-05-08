import time
import sys
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os

# Website details and language configuration
WEBSITE_URL = "https://speechtotext-by-nethytech.netlify.app/"
LANGUAGE = "en-IN"

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
chrome_options.add_argument("--headless=new")

# Initialize WebDriver
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 15)

def stream(content: str):
    sys.stdout.write("\033[96m\rUser Speaking: \033[93m")
    sys.stdout.flush()
    for char in content:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.05)
    sys.stdout.write("\033[0m\n")

def get_text() -> str:
    try:
        return driver.find_element(By.ID, "convert_text").text
    except Exception:
        return ""

def select_language():
    try:
        driver.execute_script(
            f"""
            var select = document.getElementById('language_select');
            select.value = '{LANGUAGE}';
            var event = new Event('change');
            select.dispatchEvent(event);
            """
        )
    except Exception as e:
        print(f"Error selecting language: {e}")

def verify_language_selection() -> bool:
    try:
        language_select = driver.find_element(By.ID, "language_select")
        selected_language = language_select.find_element(By.CSS_SELECTOR, "option:checked").get_attribute("value")
        return selected_language == LANGUAGE
    except Exception:
        return False

def main() -> str:
    try:
        driver.get(WEBSITE_URL)
        wait.until(EC.presence_of_element_located((By.ID, "language_select")))
        select_language()

        if not verify_language_selection():
            print(f"Error: Language selection failed. Expected: {LANGUAGE}")
            return ""

        driver.find_element(By.ID, "click_to_record").click()
        print("\n\033[94mListening...\033[0m", flush=True)

        wait.until(EC.presence_of_element_located((By.ID, "is_recording")))

        last_text = ""
        stable_text = ""

        while True:
            current_text = get_text()
            if current_text and current_text != last_text:
                stream(current_text)
                last_text = current_text

            if current_text != stable_text:
                stable_text = current_text

            try:
                is_recording = driver.find_element(By.ID, "is_recording").text
                if "Recording: False" in is_recording:
                    break
            except Exception:
                break

            time.sleep(0.5)

        return stable_text
    except Exception as e:
        print(f"Error in main function: {e}")
        return ""

def listen():
    try:
        while True:
            result = main()
            if result:
                with open("input.txt", "w") as f:
                    f.write(result.strip())
                print(f"\n\033[92mFinal Recognized Text:\033[0m {result}")
                return result
    except KeyboardInterrupt:
        print("\nListening interrupted.")
        return ""

if __name__ == "__main__":
    listen()
