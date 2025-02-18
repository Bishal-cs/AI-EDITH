import random
import threading
from os import getcwd
from Alert import Alert                                                 # for giving notification 
from co_brain import Edith                                              # for calling brain 
from internet_check import is_Online                                    
from TextToSpeech.F_DF_TTS import speak                                 # for Speaking modules 
from Data.DLG_Data import online_dlg,offline_dlg                        # for a massage online,ofline 
from Time_operations.through_Alert import check_schedule,check_Alam

Alam_path = r"C:\Users\bisha\Desktop\AI-EDITH\Data\Alarm_Data.txt"
file_path = r"C:\Users\bisha\Desktop\AI-EDITH\Data\schedule.txt"

ran_online_dlg = random.choice(online_dlg)
ran_offline_dlg =random.choice(offline_dlg)

def wish():
        t1 = threading.Thread(target=speak,args=(ran_online_dlg,))
        t2 = threading.Thread(target=Alert,args=(ran_online_dlg,))
        print(ran_online_dlg)
        t1.start()
        t2.start() 
        t1.join()
        t2.join()

def main():
    if is_Online():
        wish()
        t3 = threading.Thread(target=check_schedule,args=(file_path,))
        t4 = threading.Thread(target=Edith)
        t5 = threading.Thread(target=check_Alam,args=(Alam_path,))
        t3.start()
        t4.start()
        t5.start()
        t3.join()
        t4.join()
        t5.join()
    else:
        print(ran_offline_dlg)
        Alert(ran_offline_dlg)

main() 