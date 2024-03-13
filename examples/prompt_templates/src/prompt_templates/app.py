# Make sure to import the request object
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from mechanician_openai import OpenAIChatConnector
from dotenv import load_dotenv
import os

app = Flask(__name__, template_folder='../../templates')
socketio = SocketIO(app, cors_allowed_origins='*')

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
model_name = os.getenv("OPENAI_MODEL_NAME")

# Function to create a new AI connector for each session
def create_ai_connector():
    return OpenAIChatConnector(api_key=api_key, model_name=model_name)

# Dictionary to store AI connectors by session ID (sid)
ai_connectors = {}

@app.route('/')
def index():
    return render_template('index.html')

def get_ai_connector(sid):
    # If there's no AI connector for the current session, create one
    if sid not in ai_connectors:
        ai_connectors[sid] = create_ai_connector()
    return ai_connectors[sid]


@socketio.on('message')
def handle_message(message):
    sid = request.sid
    ai_connector = get_ai_connector(sid)

    input_text = message['data']
    try:
        for chunk in ai_connector.get_stream(input_text):
            # Assuming chunk.choices[0].delta.content exists and is the desired text content
            if hasattr(chunk, 'choices') and chunk.choices:
                content = chunk.choices[0].delta.content
                if content:  # Ensuring content is not None or empty
                    # Emit serialized content
                    emit('response', {'data': content}, room=sid)
                    socketio.sleep(0)  # Yielding to the event loop
    except Exception as e:
        print(f"Error processing AI response: {e}")
        # Handle error or notify client as needed


if __name__ == '__main__':
    socketio.run(app, debug=True)
