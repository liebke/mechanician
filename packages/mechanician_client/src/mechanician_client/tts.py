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
        # queue and playback thread
        self.q = queue.Queue()
        self.playback_thread = threading.Thread(target=self.play_audio, args=(self.q,))
        self.playback_thread.start()


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

