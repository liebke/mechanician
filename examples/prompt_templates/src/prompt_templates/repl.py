import socketio

# Create a Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    print('Connected to the server.')

@sio.event
def disconnect():
    print('Disconnected from the server.')

@sio.on('response')
def on_message(data):
    print('Response from the server:', data)
    # Prompt the user for the next message after receiving a response
    send_message_to_server()

def send_message_to_server():
    message = input("Enter your message: ")
    sio.emit('message', {'data': message})

def main():
    try:
        # Connect to the Socket.IO server
        sio.connect('http://127.0.0.1:5000')
        send_message_to_server()  # Send the initial message
    except Exception as e:
        print("Failed to connect to the server:", e)

if __name__ == '__main__':
    main()
