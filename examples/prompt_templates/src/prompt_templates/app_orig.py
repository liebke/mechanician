# from flask import Flask, request, Response
from mechanician_openai import OpenAIChatConnector
from dotenv import load_dotenv
import os

from flask import Flask, render_template, Response, request
from flask_socketio import SocketIO, emit


# app = Flask(__name__)
app = Flask(__name__, template_folder='../../templates')

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
model_name = os.getenv("OPENAI_MODEL_NAME")
ai_connector = OpenAIChatConnector(api_key=api_key, model_name=model_name)


###############################################################################

# @app.route('/chat', methods=['GET'])
# def chat():
#     message = request.args.get('message')
#     def generate():
#         stream = ai_connector.get_stream(message)
#         for chunk in ai_connector.process_stream(stream):
#             print(chunk)
#             yield chunk
#     return Response(generate(), mimetype='text/event-stream')


###############################################################################

socketio = SocketIO(app, host='0.0.0.0', cors_allowed_origins='*')


@app.route('/')
def index():
    return render_template('index.html')


def stream_response_to_client(input_text, sid):
    for chunk in ai_connector.get_stream(input_text):
        if hasattr(chunk, 'choices') and chunk.choices:
            content = chunk.choices[0].delta.content
            print(content)
            if content:  # Check that content is neither None nor empty
                socketio.emit('response', {'data': content}, room=sid)
                socketio.sleep(0)
            else:
                # Handle null or empty content gracefully, e.g., by not sending it
                pass

@socketio.on('message')
def handle_message(message):
    sid = request.sid
    # Start streaming the response back to the client
    stream_response_to_client(message['data'], sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)