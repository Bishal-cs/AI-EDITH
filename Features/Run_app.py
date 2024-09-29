import psutil 

def get_app_running_info():
    try:
        # get a list of all running processes
        processes = [proc.name() for proc in psutil.process_iter(['name'])]
        return list(set(processes))  # remove duplicates
    except Exception as e:
        return f"Error: {e}"
    
# display the list of running processes
def check_running_app():
    running_app = get_app_running_info()
    print("Runnuing App : ")
    for app in running_app:
        print(app) 