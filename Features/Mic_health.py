import pyaudio
import numpy as np
import time
from TextToSpeech.F_DF_TTS import speak

def get_mic_health(second = 5, initial_threshold = 500):
    CHUNK = 1024 # Audio chunk size
    FORMAT  = pyaudio.paInt16  # 16 bit audio
    CHANNELS = 1 # MONO audio
    RATE = 44100 # Sample rate

# initialize PyAudio
    audio = pyaudio.PyAudio()

    # open stream
    stream = audio.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK)

    print(f"Recording for {second} seconds...")
    time.sleep(1) # small delay

    # initialize variables
    sound_count = 0
    total_sample = 0
    noice_floor = 0 # Ambient noise level
    Clapping_count = 0
    signal_sum = 0 # Sum of sound level 
    noice_sum = 0 # Sum of the background noise level(Below threshold)
    freq_analysis = [] # Frequency analysis

    for _ in range(0,int(RATE/CHUNK*second)):
        data = np.frombuffer(stream.read(CHUNK),dtype=np.int16)
        volume = np.linalg.norm(data)

        # frequency analysis(FFT)
        freqs = np.fft.fftfreq(len(data))
        fft_spectrum = np.abs(np.fft.fft(data))
        freq_analysis.append(fft_spectrum)

        # update ambient noise level
        noice_floor = max(noice_floor, np.mean(np.abs(data)) * 1.5)

        # Dynamic threshold based on ambient noise level
        dynamic_threshold = max(initial_threshold, noice_floor)

        # check for sound detection 
        if volume > dynamic_threshold: # sound detected
            sound_count += 1
            signal_sum += volume
        else: # no sound detected 
            noice_sum += volume
        
        # check for clapping detection
        if np.max(np.abs(data)) >= 32767:
            Clapping_count += 1

        total_sample += 1
    
    # Calculate metrics
    mic_health = (sound_count / total_sample) * 100
    avg_signal = signal_sum /max(1, sound_count)
    avg_noice = noice_sum /max(1, total_sample - sound_count)
    snr = 10 * np.log10(avg_signal /max(10,avg_noice)) # Signal to noise ratio
    avg_clapping = (Clapping_count / total_sample) * 100

    # frequency analysis
    avg_fft_spectrum = np.mean(freq_analysis, axis=0)
    freq_range_coverage = np.sum(avg_fft_spectrum > np.median(avg_fft_spectrum)) * 100

    # close stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # output metrics
    health_report ={
        'Microphone Health (%)': mic_health,
        'Average Signal Level (dB)': snr,
        'Clapping percentage (%)': avg_clapping,
        'Frequency Range Coverage (%)': freq_range_coverage
    }

    return health_report

def mic_health():
    health_matrics = get_mic_health(second=5)
    for matric, value in health_matrics.items():
        print(f"{matric}: {value:.2f}")    
        speak(f"{matric}: {value:.2f}")