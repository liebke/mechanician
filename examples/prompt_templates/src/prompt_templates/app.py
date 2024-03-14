from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import os
from mechanician_openai import OpenAIChatConnector


class DMApp:
    def __init__(self):
        # Initialize class variables
        self.app = Flask(__name__, template_folder='../../templates')
        self.socketio = SocketIO(self.app, cors_allowed_origins='*')
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = os.getenv("OPENAI_MODEL_NAME")
        self.ai_connectors = {}

        # Setup routes and Socket.IO events
        self.setup_routes()
        self.setup_socketio_events()


    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')


    def setup_socketio_events(self):

        @self.socketio.on('connect')
        def handle_connect():
            print('Client connected')


        @self.socketio.on('disconnect')
        def handle_disconnect():
            print('Client disconnected')


        @self.socketio.on('message')
        def handle_message(message):
            print(message)
            sid = request.sid
            ai_connector = self.get_ai_connector(sid)
            input_text = message['data']
            try:
                for chunk in ai_connector.get_stream(input_text):
                    # Assuming chunk.choices[0].delta.content exists and is the desired text content
                    if hasattr(chunk, 'choices') and chunk.choices:
                        content = chunk.choices[0].delta.content
                        if content:  # Ensuring content is not None or empty
                            # Emit serialized content
                            emit('response', {'data': content}, room=sid)
                            self.socketio.sleep(0)  # Yielding to the event loop
            except Exception as e:
                print(f"Error processing AI response: {e}")
                # Handle error or notify client as needed


    def get_ai_connector(self, sid):
        # If there's no AI connector for the current session, create one
        if sid not in self.ai_connectors:
            self.ai_connectors[sid] = self.create_ai_connector()
        return self.ai_connectors[sid]
    

    def create_ai_connector(self):
        return OpenAIChatConnector(api_key=self.api_key, model_name=self.model_name)



    def run(self, host='0.0.0.0', port=5001, debug=True):
        self.socketio.run(self.app, host=host, port=port, debug=debug)

# To run the application
if __name__ == '__main__':
    my_flask_app = DMApp()
    my_flask_app.run()




#######################
# # Make sure to import the request object
# from flask import Flask, render_template, request
# from flask_socketio import SocketIO, emit
# from mechanician_openai import OpenAIChatConnector
# from dotenv import load_dotenv
# import os

# app = Flask(__name__, template_folder='../../templates')
# socketio = SocketIO(app, cors_allowed_origins='*')

# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")
# model_name = os.getenv("OPENAI_MODEL_NAME")

# # Function to create a new AI connector for each session
# def create_ai_connector():
#     return OpenAIChatConnector(api_key=api_key, model_name=model_name)

# # Dictionary to store AI connectors by session ID (sid)
# ai_connectors = {}

# @app.route('/')
# def index():
#     return render_template('index.html')

# def get_ai_connector(sid):
#     # If there's no AI connector for the current session, create one
#     if sid not in ai_connectors:
#         ai_connectors[sid] = create_ai_connector()
#     return ai_connectors[sid]


# @socketio.on('message')
# def handle_message(message):
#     sid = request.sid
#     ai_connector = get_ai_connector(sid)
#     input_text = message['data']
#     try:
#         for chunk in ai_connector.get_stream(input_text):
#             # Assuming chunk.choices[0].delta.content exists and is the desired text content
#             if hasattr(chunk, 'choices') and chunk.choices:
#                 content = chunk.choices[0].delta.content
#                 if content:  # Ensuring content is not None or empty
#                     # Emit serialized content
#                     emit('response', {'data': content}, room=sid)
#                     socketio.sleep(0)  # Yielding to the event loop
#     except Exception as e:
#         print(f"Error processing AI response: {e}")
#         # Handle error or notify client as needed


# if __name__ == '__main__':
#     socketio.run(app, debug=True)
