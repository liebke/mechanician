import warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

import whisper
import sounddevice as sd
import numpy as np
import sys
from pprint import pprint


class STT():

    def __init__(self, device_id:int=None):
        # Load the Whisper model, consider using a larger model for better accuracy
        self.model = whisper.load_model("medium")
        self.device_id = device_id
        # Set a fixed sample rate suitable for the model
        self.SAMPLE_RATE = 16000
        # Define a buffer to accumulate audio samples and explicitly set its dtype to float32
        # self.audio_buffer = np.array([], dtype=np.float32)
        self.audio_buffer = self._init_audio_buffer()
        

    def _init_audio_buffer(self):
        return np.array([], dtype=np.float32)

    def process_audio(self, indata, frames, time, status):
        # global audio_buffer
        if status:
            print(f"Status: {status}", file=sys.stderr)

        # Append unfiltered audio data directly to the buffer
        self.audio_buffer = np.concatenate((self.audio_buffer, indata[:, 0].astype(np.float32)))


    def start_recording(self):
        # with sd.InputStream(callback=self.process_audio, dtype='float32', channels=1, samplerate=self.SAMPLE_RATE):
        with sd.InputStream(device=self.device_id, callback=self.process_audio, dtype='float32', channels=1, samplerate=self.SAMPLE_RATE):

            print("Press Enter \u23CE to stop.", file=sys.stderr)
            input()
            # When Enter is pressed, the stream will close and return control


    def transcribe_audio(self):
        # global audio_buffer
        if self.audio_buffer.size > 0:
            # print("Transcribing...", file=sys.stderr)
            result = self.model.transcribe(self.audio_buffer)
            # print("Transcription complete.", file=sys.stderr)
            print(f"> {result['text']}", file=sys.stderr)
            self.audio_buffer = self._init_audio_buffer()
            return result['text']
        else:
            print("No audio recorded.", file=sys.stderr)


    def request_input_device_id(self):
        print("Select an input device to record from.", file=sys.stderr)
        print(self.list_input_devices(), file=sys.stderr)
        self.device_id = int(input("Enter the device id: "))


    def capture_audio(self):
        if self.device_id is None:
            self.request_input_device_id()
        print("Press Enter \u23CE to start.", file=sys.stderr)
        input()
        try:
            self.start_recording()
        except KeyboardInterrupt:
            print("Recording interrupted by user.", file=sys.stderr)
        finally:
            transcription = self.transcribe_audio()
            sd.stop()
            # print("Stopped recording.", file=sys.stderr)
            return transcription
            

    def list_input_devices(self):
        devices = sd.query_devices()
        for device in devices:
            if device['max_input_channels'] > 0:
                print(f"{device['index']}: {device['name']}")


    def get_device(self, query_str:str):
        devices = sd.query_devices()
        for device in devices:
            if query_str in device['name']:
                return device
        return None



if __name__ == "__main__":
    stt = STT()
    # transcript = capture_audio()
    # print(transcript)
    stt.list_devices()
    print("\n-------------------------\n\n")
    query = sys.argv[1]
    pprint(stt.get_device(query))

