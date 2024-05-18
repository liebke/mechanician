import threading
import queue
import pyaudio
from openai import OpenAI
import sys

from dotenv import load_dotenv

load_dotenv()
# Initialize OpenAI client
client = OpenAI()

# Audio format parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22050

# Initialize PyAudio
p = pyaudio.PyAudio()

# Function to handle streaming TTS and put audio data into a queue
def tts_stream(q, text_input):
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text_input,
        response_format="pcm"
    )

    # Download the entire response content
    content = response.content

    # Split the content into chunks and put them into the queue
    for i in range(0, len(content), 4096):
        chunk = content[i:i+4096]
        q.put(chunk)

# Function to play audio from the queue
def play_audio(q):
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True)
    
    while True:
        chunk = q.get()
        if chunk is None:
            break
        stream.write(chunk)
    
    stream.stop_stream()
    stream.close()

# Function to continuously read stdin and submit each line to TTS
def read_and_speak():
    q = queue.Queue()

    # Start audio playback thread
    playback_thread = threading.Thread(target=play_audio, args=(q,))
    playback_thread.start()

    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if line:
                # Start TTS streaming thread for the current line
                tts_thread = threading.Thread(target=tts_stream, args=(q, line))
                tts_thread.start()
                tts_thread.join()
    finally:
        # Properly signal the end of the stream after all lines are processed
        q.put(None)
        playback_thread.join()
        p.terminate()

# USED IN MECHANICIAN CLIENT
# Global queue and playback thread
q = queue.Queue()
playback_thread = threading.Thread(target=play_audio, args=(q,))
playback_thread.start()

def speak_fragment(text):
    if text:
        # Start TTS streaming thread for the given text
        tts_thread = threading.Thread(target=tts_stream, args=(q, text))
        tts_thread.start()
        tts_thread.join()

def close_audio():
    # Properly signal the end of the stream
    q.put(None)
    playback_thread.join()
    p.terminate()

if __name__ == "__main__":
    read_and_speak()

