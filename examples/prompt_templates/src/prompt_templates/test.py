import requests
import sys

# Get the prompt from the command line arguments
prompt = sys.argv[1] if len(sys.argv) > 1 else "Please write a limerick about Frodo Baggins' journey!"

response = requests.get('http://127.0.0.1:5000/chat', 
                        params={'message': prompt}, 
                        stream=True)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
