import random
import threading
from Vision.PC_Cam import *
from Features.Run_app import *
from Brain.brain import Main_Brain
from Device_info.info import get_info
from Features.control_volume import *
from TextToSpeech.F_DF_TTS import speak
from Features.Mic_health import mic_health
from Features.create_file import create_file
from Speechtotext.NetHyTech_STT import listen
from Whatsapp_automation.wa import send_msg_wa
from Features.AI_Image_gen import generate_image
from Features.Brightness_set import *
from Features.speaker_test import speaker_health_test
from Weather_check.Check__weather import get_weather_by_address
from Features.check_internet_speed import get_internet_speed
from Time_operations.Brain import input_manage,input_manage_Alam
from Automation.automation_brain import Auto_main_brain,clear_file


numbers = ["1:","2:","3:","4:","5:","6:","7:","8:","9:"]
spl_numbers = ["11:","12:"]

def check_inputs():
    output_text = ""
    while True:
        with open("input.txt","r") as file:
            input_text = file.read().lower() 
        if input_text != output_text:
            output_text = input_text
            if output_text.startswith("tell me"):
                output_text = output_text.replace(" p.m.","PM")
                output_text = output_text.replace(" a.m.","AM")
                if "11:" in output_text or "12:" in output_text:
                    input_manage(output_text)
                    clear_file()
                else:
                    for number in numbers:
                        if number in output_text:
                           output_text = output_text.replace(number,f"0{number}")
                           input_manage(output_text)
                           clear_file()

            elif output_text.startswith("set alarm"):
                output_text = output_text.replace(" p.m.","PM")
                output_text = output_text.replace(" a.m.","AM")
                if "11:" in output_text or "12:" in output_text:
                    input_manage_Alam(output_text)
                    clear_file()
                else:
                    for number in numbers:
                        if number in output_text:
                           output_text = output_text.replace(number,f"0{number}")
                           input_manage_Alam(output_text)
                           clear_file()

            elif "check internet speed" in output_text:
                speak("checking your internet speed")
                speed = get_internet_speed()
                speak(f"the device is running on {speed} Mbps internet speed")
                print(f"the device is running on {speed} Mbps internet speed")

            elif "edit" in output_text or "hey edit" in output_text or "edith" in output_text:
                response = Main_Brain(output_text)
                speak(response)

            elif output_text.startswith("create"):
                if "file" in output_text:
                    create_file(output_text)
                    
            elif "what is this" in output_text or "tell me about this" in output_text:
                        image_path = "captured_image.png"
                        if capture_image_and_save(image_path):
                            encoded_image = encode_image_to_base64(image_path)
                            answer = Vbrain(encoded_image)
                            speak(answer) 
            elif "mike health" in output_text or "check mike health" in output_text or "check microphone" in output_text:
                mic_health()

            elif "check volume" in output_text:
                x = get_volume_window()
                speak(x)

            elif "set volume" in output_text:
                set = output_text.replace("set volume","")
                set_volume(int(set))

            elif "check brightness percentage" in output_text:
                check_br_persentage()

            elif "brightness set" in output_text:
                set = output_text.replace("brightness set","")
                set_brightness_windows(int(set))

            elif "check weather" in output_text:
                    weather_report = get_weather_by_address("Westbengal Hooghly")
                    print(weather_report)
                    speak(weather_report)
            
            elif "generate image" in output_text:
                 text = output_text.replace("generate image","")
                 text = text.strip()
                 generate_image(text)
                 speak("image generated successfully")

            elif "send message on whatsapp" in output_text or "send a whatsapp message" in output_text:
                send_msg_wa()

            else:
                Auto_main_brain(output_text)
                get_info(output_text)
                
def Edith():
    clear_file()
    t1 = threading.Thread(target = listen)
    t2 = threading.Thread(target = check_inputs)
    t1.start()
    t2.start()
    t1.join()
    t2.join()