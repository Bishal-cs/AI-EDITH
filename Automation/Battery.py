import time
import psutil # pip install psutil
import threading
from Alert import Alert
from TextToSpeech.F_DF_TTS import speak

battery = psutil.sensors_battery()

def battery_Alert():
    while True:
        time.sleep(3)
        percentage = int(battery.percent)
        if percentage == 100:
            t1 = threading.Thread(target=Alert,args=("100% Charged",))
            t2 = threading.Thread(target=speak,args=("100% Charged. Please Unplug Your Device",))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
        elif percentage <= 20:
            t1 = threading.Thread(target=Alert,args=("your battery is low 20%",))
            t2 = threading.Thread(target=speak,args=("Sir Please Charge Your Device 20% remaining",))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
        elif percentage <= 10:
            t1 = threading.Thread(target=speak,args=("Sir Please Charge Me or i am shutting down remaining 10%",))
            t1.start()
            t1.join()
        time.sleep(10)

def chekc_Percentage():
    battery = psutil.sensors_battery()
    percentage = int(battery.percent)
    t2 = threading.Thread(target=speak,args=(f"Battery Charge Remaining {percentage}% ",))
    t2.start()
    t2.join()