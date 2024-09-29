import time
import webbrowser
import pyautogui as ui

def play_music_on_spotify(song_name):
    # Open Spotify
    webbrowser.open("https://open.spotify.com/")
    time.sleep(4)  # Wait for Spotify to load

    try:
        # Locate the search box and type the song name
        ui.hotkey("ctrl", "shift", "l")
        time.sleep(0.5)  # Wait for the search box to appear
        ui.write(song_name)
        time.sleep(1)  # Wait for search results to load

        # Click the first result (assuming it's the song you want)
        ui.click(ui.locateCenterOnScreen("spotify_search_result.png"))  # Replace with an actual screenshot of the search result
    except Exception as e:
        print(f"Error: {e}")
        print("Something went wrong. Check if Spotify is open and try again.")

