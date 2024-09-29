import os 
import requests                 # pip install requests
import playsound                # pip install playsound==1.2.2
from typing import Union        # pip install typing

def generate_audio(massage: str,voice :str = "Brian"):
    url: str = f"https://api.streamelements.com/kappa/v2/speech?voice={voice}&text={{{massage}}}"

    headers = {'User-Agent':'Mozilla/5.0(Maciontosh;intel Mac OS X 10_15_7)AppleWebkit/537.36(KHTML,like Gecko)Chrome/119.0.0.0 Safari/537.36'}

    try:
        result = requests.get(url=url, headers=headers)
        return result.content
    except Exception as e:
        return None
    
def speak(massage: str,voice: str = "Brian",folder: str = "",extension: str = ".mp3") -> Union[str,None]:
    try:
        result_content = generate_audio(massage,voice)
        file_path = os.path.join(folder,f"{voice},{extension}") 
        with open(file_path,"wb") as file:
            file.write(result_content)
        playsound.playsound(file_path)
        os.remove(file_path)
        return None
    except Exception as e:
            print(e)

speak("Hello Edith ")
