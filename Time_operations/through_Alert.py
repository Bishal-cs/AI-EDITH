import os
import time
import threading
from os import getcwd
from Alert import Alert
from TextToSpeech.F_DF_TTS import speak

# Function to ensure the user_data directory and files exist
def ensure_files_exist(file_path):
    user_data_dir = os.path.dirname(file_path)
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)  # Create the user_data directory if it doesn't exist
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:  # Create the file if it doesn't exist
            file.write("")  # Write an empty string to initialize the file

def load_schedule(file_path):
    schedule = {}
    try:
        ensure_files_exist(file_path)  # Ensure the file exists
        with open(file_path, 'r') as file:
            for line in file:
                if '=' in line:
                    line_time, activity = line.strip().split(' = ')
                    schedule[line_time.strip()] = activity.strip()
    except Exception as e:
        print(f"Error loading schedule: {e}")
    return schedule

def check_schedule(file_path):
    ensure_files_exist(file_path)
    last_modified = 0
    while True:
        current_time = time.strftime("%I:%M%p")
        try:
            # Check file modification time
            modified = os.path.getmtime(file_path)
            if modified != last_modified:
                last_modified = modified
                schedule = load_schedule(file_path)
            
            if current_time in schedule:
                text = schedule[current_time]
                t1 = threading.Thread(target=Alert, args=(text,))
                t2 = threading.Thread(target=speak, args=(text,))
                t1.start()
                t2.start()
                t1.join()
                t2.join()
        
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(60)

def load_AlamTime(file_path):
    schedule = {}
    try:
        ensure_files_exist(file_path)  # Ensure the file exists
        with open(file_path, 'r') as file:
            schedule = file.read()
    except Exception as e:
        print(f"Error loading schedule: {e}")
    return schedule

Alam_path = r"user_data\Alarm_Data.txt"

def check_Alam(Alam_path):
    ensure_files_exist(Alam_path)
    last_modified = 0
    while True:
        current_time = time.strftime("%I:%M%p")
        try:
            # Check file modification time
            modified = os.path.getmtime(Alam_path)
            if modified != last_modified:
                last_modified = modified
                schedule = load_AlamTime(Alam_path)
            
            if current_time in schedule:
                text = "Sir it's time to wake up"
                t1 = threading.Thread(target=Alert, args=(text,))
                t2 = threading.Thread(target=speak, args=(text,))
                t1.start()
                t2.start()
                t1.join()
                t2.join()
        
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(10)