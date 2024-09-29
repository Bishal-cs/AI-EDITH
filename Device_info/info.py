import psutil
from TextToSpeech.F_DF_TTS import speak

def get_ram_info():
    ram = psutil.virtual_memory()
    total_ram = ram.total / (1024 ** 3)
    available_ram = ram.available / (1024 ** 3)
    return f"Total RAM:{total_ram:.2f} GB\nAvailable RAM:{available_ram:.2f} GB"
def get_storage_info(drive_latter):
    partition_info = psutil.disk_partitions()
    for partition in partition_info:
        if partition.device.startswith(drive_latter):
            usage = psutil.disk_usage(partition.mountpoint)
            total = usage.total / (1024 ** 3)
            used = usage.used / (1024 ** 3)
            free = usage.free / (1024 ** 3)
            return (f"Drive {drive_latter}:\n"
                    f"Total: {total:.2f} GB\n"
                    f"Used: {used:.2f} GB\n"
                    f"Free: {free:.2f} GB")
    return f"Drive {drive_latter} not found"
def get_info(query):
        if query == "exit":
            print("Exiting...")
            speak("Exiting...")
        elif "device ram" in query:
            print(get_ram_info())
            speak(get_ram_info())
        elif "device storage" in query:
            drive_latter = query.split()[-1].upper()
            print(get_storage_info(drive_latter))
            speak(get_storage_info(drive_latter))
        elif "available space" in query:
            drive_latter = query.split()[-1].upper()
            print(get_storage_info(drive_latter))
            speak(get_storage_info(drive_latter))
        else:
            pass