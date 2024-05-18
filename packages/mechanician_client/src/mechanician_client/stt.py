import warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

import whisper
import sounddevice as sd
import numpy as np
import sys

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
        

if __name__ == "__main__":
    transcript = capture_audio()
    print(transcript)