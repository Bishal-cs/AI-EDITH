""" Speech to text using selenium and chrome browser and another way. This is an online version"""
import time  # For delays and timing operations
import sys  # For system-related functions like standard output
import subprocess  # For executing shell commands (e.g., installing modules)
from selenium import webdriver  # For browser automation
from selenium.webdriver.chrome.options import Options  # For configuring Chrome options
from selenium.webdriver.common.by import By  # For locating web elements
from selenium.webdriver.support import expected_conditions as EC  # For defining wait conditions
from selenium.webdriver.support.ui import WebDriverWait  # For explicit waits

# Function to install required modules
def install_modules():
    try:
        import selenium
    except ModuleNotFoundError:
        subprocess.run("pip install selenium")

# Website details and language configuration
WEBSITE_URL = "https://speechtotext-by-nethytech.netlify.app/"  # URL of the speech-to-text service
LANGUAGE = "en-IN"  # Language code for speech recognition

# Configure Chrome options
chrome_options = Options()  # Create a Chrome options object
chrome_options.add_argument("--use-fake-ui-for-media-stream")  # Allow fake audio streams for speech input
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
)  # Set a custom user-agent string for browser identification
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)

# Initialize WebDriver with Chrome options
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)  # Set up an explicit wait with a timeout of 10 seconds

def stream(content: str):
    """
    Displays streaming text with animation on a single line.
    """
    sys.stdout.write("\033[96m\rUser Speaking: \033[93m")  # Set color and prepare to overwrite the same line
    sys.stdout.flush()  # Ensure the text is written immediately
    for char in content:
        sys.stdout.write(char)  # Print each character one by one
        sys.stdout.flush()  # Ensure immediate output
        time.sleep(0.05)  # Add a delay for the animation effect
    sys.stdout.write("\033[0m")  # Reset text color

def get_text() -> str:
    """
    Retrieves text from the speech-to-text web interface.
    """
    try:
        # Locate the element containing the converted text and return its content
        return driver.find_element(By.ID, "convert_text").text
    except Exception:
        # Return an empty string if the element is not found or an error occurs
        return ""

def select_language():
    """
    Selects the desired language in the web interface.
    """
    try:
        # Use JavaScript to select the desired language from the dropdown
        driver.execute_script(
            f"""
            var select = document.getElementById('language_select');  // Locate the dropdown
            select.value = '{LANGUAGE}';  // Set the value to the desired language
            var event = new Event('change');  // Create a change event
            select.dispatchEvent(event);  // Dispatch the event to apply the change
            """
        )
    except Exception as e:
        # Print an error message if language selection fails
        print(f"Error selecting language: {e}")

def verify_language_selection() -> bool:
    """
    Verifies if the correct language has been selected.
    """
    try:
        # Locate the language dropdown
        language_select = driver.find_element(By.ID, "language_select")
        # Find the currently selected option and retrieve its value
        selected_language = language_select.find_element(By.CSS_SELECTOR, "option:checked").get_attribute("value")
        # Check if the selected language matches the desired one
        return selected_language == LANGUAGE
    except Exception:
        # Return False if verification fails
        return False

def main() -> str:
    """
    Main function to process speech-to-text.
    """
    try:
        driver.get(WEBSITE_URL)  # Open the speech-to-text website
        wait.until(EC.presence_of_element_located((By.ID, "language_select")))  # Wait for the language dropdown to load
        select_language()  # Select the desired language

        if not verify_language_selection():
            # Print an error if language selection fails
            print(f"Error: Language selection failed. Expected: {LANGUAGE}")
            return ""

        driver.find_element(By.ID, "click_to_record").click()  # Click the record button
        print("\n\033[94mListening...\033[0m", flush=True)  # Notify the user that recording has started

        wait.until(EC.presence_of_element_located((By.ID, "is_recording")))  # Wait until recording starts

        last_text = ""  # Variable to store the previous recognized text
        stable_text = ""  # Variable to store the stable (final) text

        while True:
            current_text = get_text()  # Get the current recognized text
            if current_text != last_text:
                stream(current_text)  # Stream the updated text
                last_text = current_text  # Update the last text

            if current_text != stable_text:
                stable_text = current_text  # Update the stable text

            is_recording = driver.find_element(By.ID, "is_recording").text  # Check the recording status
            if "Recording: False" in is_recording:  # Stop if recording has ended
                break
            time.sleep(0.5)  # Pause briefly before checking again

        return stable_text  # Return the stable recognized text
    except Exception as e:
        # Print an error message and return an empty string
        print(f"Error in main function: {e}")
        return ""

def listen():
    """
    Listens for user input and processes the speech recognition.
    """
    try:
        while True:
            result = main()  # Call the main function to process speech
            if result:  # Exit the loop if valid text is recognized
                return result
    except KeyboardInterrupt:
        # Handle user interruption
        print("\nListening interrupted.")
        return ""

if __name__ == "__main__":
    while True:
        listen()
