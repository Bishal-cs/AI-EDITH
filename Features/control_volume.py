from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
from TextToSpeech.F_DF_TTS import speak
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume # pip install pycaw

def get_volume_window():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    current_volume = volume.GetMasterVolumeLevelScalar() * 100
    speak(f"The Device running on + {int(round(current_volume, 2))} Volume")

def set_volume(percentage):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(percentage / 100, None)
    print(f"Volume set to {percentage}%")
