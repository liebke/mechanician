import asyncio
import websockets
import json
import sys

async def client():
    uri = "ws://127.0.0.1:8000/ws"  # Replace with the URL of your web app
    async with websockets.connect(uri) as websocket:
        # Get input from the command line arguments
        message = ' '.join(sys.argv[1:])

        # Send the input to the server
        await websocket.send(json.dumps({"data": message}))

        # Receive and print messages from the server
        async for message in websocket:
            # Print the server's message, preserving newline characters
            print(message, end='', flush=True)

# Run the client
asyncio.run(client())