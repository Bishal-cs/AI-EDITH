import os
import threading
from os import getcwd
from Vision.PC_Cam import *
from Features.Run_app import *
from Brain.brain import ChatBot
from Device_info.info import get_info
from Features.Brightness_set import *
from Features.control_volume import *
from TextToSpeech.F_DF_TTS import speak
from Features.Mic_health import mic_health
from Features.create_file import create_file
from Speechtotext.ListenFN import listen
from Whatsapp_automation.wa import send_msg_wa
from Weather_check.Check__weather import get_weather_by_address
from Time_operations.Brain import input_manage,input_manage_Alam
from Automation.automation_brain import Auto_main_brain,clear_file
from Features.content_write import Content

numbers = ["1:","2:","3:","4:","5:","6:","7:","8:","9:"]
spl_numbers = ["11:","12:"]

def check_inputs():
    output_text = ""
    while True:
        with open("user_data/input.txt","r") as file:
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

            elif output_text.startswith("hey") or "edit" in output_text or output_text.startswith("hi"):
                response = ChatBot(output_text)
                print(response)
                speak(response)

            elif output_text.startswith("create"):
                if "file" in output_text:
                    create_file(output_text)
                    
            elif "what is this" in output_text or "tell me about this" in output_text:
                        image_path = "user_data/captured_image.png"
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

            elif "send message on whatsapp" in output_text or "send a whatsapp message" in output_text:
                send_msg_wa()
            
            elif 'exit' in output_text:
                speak("Goodbye")
                os._exit(1)

            elif "write a content" in output_text or "write content" in output_text:
                query = output_text.replace("write a content","")
                query = query.strip()
                Content(query)
                speak("lets see the content..!")

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
