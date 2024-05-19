# import warnings
# import whisper
# import pyaudio
# import numpy as np
# import sys
# from pprint import pprint

# # Suppress warnings about FP16 on CPU
# warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# # Load the Whisper model
# model = whisper.load_model("medium")

# # Constants for the audio stream
# SAMPLE_RATE = 16000
# CHANNELS = 1
# FORMAT = pyaudio.paFloat32

# # Create a PyAudio object
# p = pyaudio.PyAudio()

# # Buffer to hold audio data
# audio_buffer = np.array([], dtype=np.float32)

# def process_audio(in_data, frame_count, time_info, status):
#     global audio_buffer
#     audio_data = np.frombuffer(in_data, dtype=np.float32)
#     audio_buffer = np.concatenate((audio_buffer, audio_data))
#     return (in_data, pyaudio.paContinue)

# def start_recording():
#     stream = p.open(format=FORMAT, channels=CHANNELS, rate=SAMPLE_RATE, input=True,
#                     stream_callback=process_audio)
#     print("Recording... Press Enter to stop recording.", file=sys.stderr)
#     input()
#     stream.stop_stream()
#     stream.close()

# def transcribe_audio():
#     global audio_buffer
#     if audio_buffer.size > 0:
#         print("Transcribing...", file=sys.stderr)
#         result = model.transcribe(audio_buffer)
#         print("Transcription complete.", file=sys.stderr)
#         print(result['text'], file=sys.stderr)
#         return result['text']
#     else:
#         print("No audio recorded.", file=sys.stderr)

# def capture_audio():
#     print("Press Enter to start recording.", file=sys.stderr)
#     input()
#     try:
#         start_recording()
#     except KeyboardInterrupt:
#         print("Recording interrupted by user.", file=sys.stderr)
#     finally:
#         transcription = transcribe_audio()
#         p.terminate()
#         print("Stopped recording.", file=sys.stderr)
#         return transcription

# def list_devices():
#     info = p.get_host_api_info_by_index(0)
#     num_devices = info.get('deviceCount')
#     # List all available devices
#     for i in range(0, num_devices):
#         if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
#             print(p.get_device_info_by_host_api_device_index(0, i))

# def get_device(query_str:str):
#     info = p.get_host_api_info_by_index(0)
#     num_devices = info.get('deviceCount')
#     for i in range(0, num_devices):
#         device_info = p.get_device_info_by_host_api_device_index(0, i)
#         if query_str in device_info.get('name'):
#             return device_info
#     return None

# if __name__ == "__main__":
#     list_devices()
#     print("\n-------------------------\n\n")
#     query = sys.argv[1]
#     pprint(get_device(query))


import warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

import whisper
import sounddevice as sd
import numpy as np
import sys
from pprint import pprint

# Load the Whisper model, consider using a larger model for better accuracy
model = whisper.load_model("medium")

# Set a fixed sample rate suitable for the model
SAMPLE_RATE = 16000

# Define a buffer to accumulate audio samples and explicitly set its dtype to float32
audio_buffer = np.array([], dtype=np.float32)

def process_audio(indata, frames, time, status):
    global audio_buffer
    if status:
        print(f"Status: {status}", file=sys.stderr)

    # Append unfiltered audio data directly to the buffer
    audio_buffer = np.concatenate((audio_buffer, indata[:, 0].astype(np.float32)))

def start_recording():
    with sd.InputStream(callback=process_audio, dtype='float32', channels=1, samplerate=SAMPLE_RATE):
    # with sd.InputStream(device=0, callback=process_audio, dtype='float32', channels=1, samplerate=SAMPLE_RATE):

        print("Recording... Press the Enter key again to stop recording.", file=sys.stderr)
        input()
        # When Enter is pressed, the stream will close and return control

def transcribe_audio():
    global audio_buffer
    if audio_buffer.size > 0:
        print("Transcribing...", file=sys.stderr)
        result = model.transcribe(audio_buffer)
        print("Transcription complete.", file=sys.stderr)
        print(result['text'], file=sys.stderr)
        return result['text']
    else:
        print("No audio recorded.", file=sys.stderr)

def capture_audio():
    print("Press the Enter key to start recording.", file=sys.stderr)
    input()
    try:
        start_recording()
    except KeyboardInterrupt:
        print("Recording interrupted by user.", file=sys.stderr)
    finally:
        transcription = transcribe_audio()
        sd.stop()
        print("Stopped recording.", file=sys.stderr)
        return transcription
        

def list_devices():
    pprint(sd.query_devices())


def get_device(query_str:str):
    devices = sd.query_devices()
    for device in devices:
        if query_str in device['name']:
            return device
    return None

if __name__ == "__main__":
    # transcript = capture_audio()
    # print(transcript)
    list_devices()
    print("\n-------------------------\n\n")
    query = sys.argv[1]
    pprint(get_device(query))