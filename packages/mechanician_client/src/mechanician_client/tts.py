import threading
import queue
import sounddevice as sd
from openai import OpenAI
import sys
import numpy as np

from dotenv import load_dotenv
from pprint import pprint

# Audio format parameters
# FORMAT = 'int16'  # This is not directly used in sd.OutputStream, instead, use subtype='PCM_16'
CHANNELS = 1
RATE = 22050

class TTS():

    def __init__(self, openai_client:'OpenAI', output_device_id:int=None):

        self.client = openai_client
        self.output_device_id = output_device_id
        # Global queue and playback thread
        self.q = queue.Queue()
        self.playback_thread = threading.Thread(target=self.play_audio, args=(self.q,))
        self.playback_thread.start()

        # self.lock = threading.Lock()


    def tts_stream(self, text_input):
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text_input,
            response_format="pcm"
        )

        content = response.content
        for i in range(0, len(content), 4096):
            chunk = content[i:i+4096]
            self.q.put(np.frombuffer(chunk, dtype=np.int16))  # Convert bytes to int16


    def play_audio(self, q):
        try:
            with sd.OutputStream(samplerate=RATE, channels=CHANNELS, dtype=np.int16, device=self.output_device_id) as stream:
                while True:
                    chunk = q.get()
                    if chunk is None:
                        break
                    stream.write(chunk)
        except Exception as e:
            print(f"Error in audio playback: {str(e)}", file=sys.stderr)


    def request_output_device_id(self):
        print("Select an output device to play response.", file=sys.stderr)
        print(self.list_output_devices(), file=sys.stderr)
        self.output_device_id = int(input("Enter the device id: "))


    def list_output_devices(self):
        devices = sd.query_devices()
        for device in devices:
            if device['max_output_channels'] > 0:
                print(f"{device['index']}: {device['name']}")


    def speak_fragment(self, text):
        if text:
            tts_thread = threading.Thread(target=self.tts_stream, args=(text,))
            tts_thread.start()
            tts_thread.join()
                
    # def speak_fragment(self, text):
    #     if text:
    #         tts_thread = threading.Thread(target=self.tts_stream, args=(text, self.lock))
    #         tts_thread.daemon = True  # Set the thread as a daemon thread
    #         tts_thread.start()


    def list_audio_devices(self):
        print(f"Number of devices: {len(sd.query_devices())}")
        for device in sd.query_devices():
            print(f"Device id {device['index']}, name {device['name']}")


    def close_audio(self):
        self.q.put(None)
        self.playback_thread.join()


if __name__ == "__main__":
    load_dotenv()
    # Initialize OpenAI client
    client = OpenAI()

    # list_audio_devices()
    tts = TTS(openai_client=client)
    tts.speak_fragment("Hello world")
    from time import sleep
    sleep(1)
    tts.close_audio()
    exit(0)


# import threading
# import queue
# import sounddevice as sd
# from openai import OpenAI
# import numpy as np

# from dotenv import load_dotenv

# load_dotenv()
# # Initialize OpenAI client
# client = OpenAI()

# # Audio format parameters
# RATE = 22050

# # Create a global queue accessible throughout the module
# q = queue.Queue()

# # Function to handle streaming TTS and put audio data into a queue
# def tts_stream(text_input):
#     response = client.audio.speech.create(
#         model="tts-1",
#         voice="nova",
#         input=text_input,
#         response_format="pcm"
#     )

#     # Download the entire response content
#     content = response.content

#     # Split the content into chunks and put them into the queue
#     chunk_size = 4096 * 10  # Use a larger chunk size
#     for i in range(0, len(content), chunk_size):
#         chunk = content[i:i+chunk_size]
#         q.put(chunk)
#     q.put("END_OF_AUDIO")  # Signal end of this text's audio

# # Function to play audio from the queue
# def play_audio():
#     buffer = b''
#     while True:
#         chunk = q.get()
#         if chunk == "END_OF_AUDIO":  # Check if it's an end-of-audio signal
#             if buffer:
#                 data = np.frombuffer(buffer, dtype='int16')
#                 sd.play(data, samplerate=RATE)
#                 sd.wait()
#                 buffer = b''  # Clear buffer after playing
#             continue
#         elif chunk is None:  # Check for program end signal
#             break  # Exit the loop to end the thread
#         buffer += chunk
#         if len(buffer) > 4096 * 20:  # Play when buffer has enough data
#             data = np.frombuffer(buffer, dtype='int16')
#             sd.play(data, samplerate=RATE)
#             sd.wait()
#             buffer = b''

# # Start the global playback thread
# playback_thread = threading.Thread(target=play_audio)
# playback_thread.start()

# def speak_fragment(text):
#     if text:
#         # Start TTS streaming thread for the given text
#         tts_thread = threading.Thread(target=tts_stream, args=(text,))
#         tts_thread.start()
#         tts_thread.join()  # Wait for thread to finish processing this text

# def close_audio():
#     # Properly signal the end of the stream
#     q.put(None)  # Signal to end the play_audio thread
#     playback_thread.join()

# if __name__ == "__main__":
#     try:
#         text = input("Enter text to speak: ")
#         while text.lower() != 'exit':
#             speak_fragment(text)
#             text = input("Enter text to speak: ")
#         close_audio()  # Ensure resources are cleaned up properly
#     except KeyboardInterrupt:
#         close_audio()




# import threading
# import queue
# import pyaudio
# from openai import OpenAI
# import sys

# from dotenv import load_dotenv
# from pprint import pprint

# load_dotenv()
# # Initialize OpenAI client
# client = OpenAI()

# # Audio format parameters
# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 22050

# # Initialize PyAudio
# p = pyaudio.PyAudio()

# # Function to handle streaming TTS and put audio data into a queue
# def tts_stream(q, text_input):
#     response = client.audio.speech.create(
#         model="tts-1",
#         voice="nova",
#         input=text_input,
#         response_format="pcm"
#     )

#     # Download the entire response content
#     content = response.content

#     # Split the content into chunks and put them into the queue
#     for i in range(0, len(content), 4096):
#         chunk = content[i:i+4096]
#         q.put(chunk)

# # Function to play audio from the queue
# def play_audio(q):
#     #stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, output_device_index=0)
#     stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True)
    
#     while True:
#         chunk = q.get()
#         if chunk is None:
#             break
#         stream.write(chunk)
    
#     stream.stop_stream()
#     stream.close()

# # Function to continuously read stdin and submit each line to TTS
# def read_and_speak():
#     q = queue.Queue()

#     # Start audio playback thread
#     playback_thread = threading.Thread(target=play_audio, args=(q,))
#     playback_thread.start()

#     try:
#         while True:
#             line = sys.stdin.readline()
#             if not line:
#                 break
#             line = line.strip()
#             if line:
#                 # Start TTS streaming thread for the current line
#                 tts_thread = threading.Thread(target=tts_stream, args=(q, line))
#                 tts_thread.start()
#                 tts_thread.join()
#     finally:
#         # Properly signal the end of the stream after all lines are processed
#         q.put(None)
#         playback_thread.join()
#         p.terminate()

# # USED IN MECHANICIAN CLIENT
# # Global queue and playback thread
# q = queue.Queue()
# playback_thread = threading.Thread(target=play_audio, args=(q,))
# playback_thread.start()

# def speak_fragment(text):
#     if text:
#         # Start TTS streaming thread for the given text
#         tts_thread = threading.Thread(target=tts_stream, args=(q, text))
#         tts_thread.start()
#         tts_thread.join()

# def list_audio_devices():
#     # List all audio output devices
#     print(f"Number of devices: {p.get_device_count()}")
#     for i in range(p.get_device_count()):
#         device_info = p.get_device_info_by_index(i)
#         print(f"Device id {device_info['index']}, name {device_info['name']}")
#     close_audio()
#     exit(0)


# def close_audio():
#     # Properly signal the end of the stream
#     q.put(None)
#     playback_thread.join()
#     p.terminate()

# if __name__ == "__main__":
#     # read_and_speak()
#     list_audio_devices()

