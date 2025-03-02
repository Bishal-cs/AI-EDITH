import os 
import requests
import subprocess
try:
    from playsound import playsound
except ModuleNotFoundError:
    subprocess.run("pip install playsound==1.2.2")
    from playsound import playsound

voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

url = "https://ttsmp3.com/makemp3_ai.php"

payload = {
    "msg": "It seems like you want to watch a movie, but you're not sure what to watch. Let me suggest some popular action movies that are currently trending:\n\n1. Ant-Man and the Wasp: Quantumania (2023)\n2. Creed III (2023)\n3. Shazam! Fury of the Gods (2023)\n\nWould you like more suggestions or would you like me to recommend something based on a specific actor or genre?",
    "lang": voices[4],
    "speed": "1.0",
    "source": "ttsmp3"
}

response = requests.post(url, data=payload)

if response.status_code == 200:
    data = response.json()

    url = data["URL"]

    response = requests.get(url)

    file_name = os.path.basename(url)

    with open(file_name, "wb") as f:
        f.write(response.content)

    playsound(file_name)
    os.remove(file_name)

else:
    print("Error:", response.status_code)