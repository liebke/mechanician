import asyncio
import websockets
import requests
import json
import ssl
import os
import getpass
import argparse
import sys
from pprint import pprint

class MechanicianClient:

    def __init__(self, host='127.0.0.1', port='8000',
                 username=None, password=None,
                 token=None, root_ca_cert='./certs/rootCA.pem'):
        self.username = username
        self.password = password
        self.ws_url = f'wss://{host}:{port}/ws'
        self.https_base_url = f'https://{host}:{port}'
        self.token_url = f'{self.https_base_url}/token'
        self.root_ca_cert = root_ca_cert
        self.ssl_context = self._setup_ssl_context()
        self.token = token

        if username and password:
            self.token = self._authenticate()
            if self.token:
                self._save_token(self.token)
        else:
            self.token = self._retrieve_token()
        
        self.socket = None
        if not self.token:
            raise Exception("Failed to retrieve JWT token. Exiting program...")


    def _save_token(self, token):
        # Define the path where the token will be stored
        token_dir = os.path.join(os.path.expanduser('~'), '.mechanician')
        token_file = os.path.join(token_dir, 'auth_token')

        # Create the directory if it does not exist
        if not os.path.exists(token_dir):
            os.makedirs(token_dir)

        # Write the token to the file
        with open(token_file, 'w') as file:
            file.write(token)
        print("Token saved successfully.", file=sys.stderr)


    def _retrieve_token(self):
        # Define the path where the token is stored
        token_file = os.path.join(os.path.expanduser('~'), '.mechanician', 'auth_token')

        # Check if the file exists
        if os.path.exists(token_file):
            # Read the token from the file
            with open(token_file, 'r') as file:
                token = file.read().strip()
            return token
        else:
            # Return None if the file does not exist
            print("No token found.", file=sys.stderr)
            return None
        

    def _setup_ssl_context(self):
        if os.path.exists(self.root_ca_cert):
            ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            ssl_context.load_verify_locations(self.root_ca_cert)
        else:
            print(f"Root CA certificate not found at {self.root_ca_cert}", file=sys.stderr)
            ssl_context = ssl.create_default_context()  # Assumes no verification
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        return ssl_context


    def _authenticate(self):
        verify_option = self.root_ca_cert if os.path.exists(self.root_ca_cert) else False
        response = requests.post(self.token_url, data={'username': self.username, 'password': self.password}, verify=verify_option)
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            print(f"Failed to retrieve JWT token. Status code: {response.status_code}", file=sys.stderr)
            return None


    async def _init_web_socket(self, ai_name:str=None, conversation_id:str=None):
        websocket = await websockets.connect(self.ws_url, ssl=self.ssl_context)
        await self._authorize_websocket(ai_name=ai_name, conversation_id=conversation_id, websocket=websocket)
        return websocket


    async def _authorize_websocket(self, ai_name:str=None, conversation_id:str=None, websocket=None):
        if conversation_id is None:
            new_conversation = True
        else:
            new_conversation = False

        req = {"token": self.token, "ai_name": ai_name, "type": 'token', "conversation_id": conversation_id, "new_conversation": new_conversation}
        await websocket.send(json.dumps(req))
        await asyncio.sleep(0)
        response = await websocket.recv()
        fragment = json.loads(response)
        print({k: fragment[k] for k in ["ai_name", "conversation_id"] if k in fragment}, flush=True, file=sys.stderr)
        if fragment.get("role", "") == "system" and not fragment.get("authorized", False):
            print("Unauthorized access. Please check your credentials.\n\n", file=sys.stderr)
            exit(1)


    async def _run_loop(self, socket, ai_name:str, conversation_id:str=None, initial_prompt=None):
        try:
            while True:
                if initial_prompt is None:
                    prompt_text = input("> ").strip()
                else:
                    prompt_text = initial_prompt
                    initial_prompt = None
                response = await self._send_message(socket, ai_name, prompt_text, conversation_id=conversation_id)
                print("\n\n")
        finally:
            await socket.close()
            exit(0)


    async def _send_message(self, socket, ai_name:str, prompt_text:str, conversation_id:str=None, print_stream=True):
        prompt_text = self._process_prompt(prompt_text)
        if prompt_text:
            message = json.dumps({"data": prompt_text, "type": 'prompt', "ai_name": ai_name, "conversation_id": conversation_id})
            await socket.send(message)
            await asyncio.sleep(0)
            complete_response = ""
            try:
                while True:
                    fragment_str = await socket.recv()
                    fragment = json.loads(fragment_str)
                    content = fragment.get("content", None)
                    if content is not None:
                        complete_response += content
                        if print_stream:
                            print(content, end="", flush=True)
                    if fragment.get("finish_reason", "") == "stop":
                        return complete_response
            except websockets.exceptions.ConnectionClosedError:
                print("Connection closed unexpectedly. Please check your network connection.", file=sys.stderr)
                return


    def _process_prompt(self, prompt_text):
        if prompt_text.startswith("/"):
            command = prompt_text.split(" ")[0]
            if command == "/help":
                print("Available commands:")
                print("/help - Display this help message")
                print("/exit - Exit the program")
            elif command == "/exit":
                print("Exiting program...")
                exit(0)
            else:
                print("Invalid command. Type '/help' to see available commands.", file=sys.stderr)
        else:
            return prompt_text


    def get_prompt_template(self, template_name):
        url = f"{self.https_base_url}/prompt_tools/templates/{template_name}"
        verify = self.root_ca_cert if os.path.exists(self.root_ca_cert) else False
        response = requests.get(url, cookies={'access_token': self.token}, verify=verify)
        if response.status_code == 200:
            return response.json()
        else:
            return f"Failed to retrieve prompt template. Status code: {response.status_code}"


    def call_prompt_tool(self, ai_name:str, function_name:str, prompt_template:str, form_data:dict={}):
        url = f"{self.https_base_url}/call_prompt_tool"
        verify = self.root_ca_cert if os.path.exists(self.root_ca_cert) else False
        form_data['function_name'] = function_name
        form_data['prompt_template'] = prompt_template
        form_data['ai_name'] = ai_name
        response = requests.post(url, data=form_data, cookies={'access_token': self.token}, verify=verify)
        if response.status_code == 200:
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                print(f"Failed to parse server response as JSON. Response text: {response.text}")
                return None
        else:
            return f"Failed to retrieve prompt template. Status code: {response.status_code}"


    async def submit_prompt(self, ai_name:str, prompt:str, conversation_id:str=None):
        socket = await client._init_web_socket(ai_name=ai_name, conversation_id=conversation_id)
        await self._send_message(socket, ai_name, prompt, conversation_id=conversation_id, print_stream=True)
        print("\n")
        await socket.close()
        exit(0)


    async def shell(self, ai_name:str, conversation_id:str=None, initial_prompt=None):
        socket = await self._init_web_socket(ai_name=ai_name, conversation_id=conversation_id)
        await self._run_loop(socket, ai_name, conversation_id=conversation_id, initial_prompt=initial_prompt)


    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Mechanician client.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host IP address")
    parser.add_argument("--port", type=str, default="8000", help="Port number")
    parser.add_argument("--username", type=str, help="Username for authentication")
    parser.add_argument("--password", type=str, help="Password for authentication")
    parser.add_argument("--token", type=str, help="Authentication token")
    parser.add_argument("--ai_name", type=str, help="AI name")
    parser.add_argument("--conversation_id", type=str, help="Conversation ID")
    parser.add_argument("--root_ca_cert", type=str, default="./certs/rootCA.pem", help="Path to Root CA certificate")
    parser.add_argument("--interactive", type=bool, default=False, help="Interactive mode (default: False)")
    parser.add_argument('--prompt', nargs='?', help='Prompt text to submit, or "-" for stdin')

    parser.add_argument("--prompt_template", type=str, help="Prompt Template name")
    parser.add_argument("--prompt_tool", type=str, help="Prompt Tool name")
    parser.add_argument("--data", nargs='*', help="Arbitrary form data as key=value pairs (e.g., key1=value1 key2=value2)")

    args = parser.parse_args()

    if args.username and args.password is None:
        args.password = getpass.getpass("Enter password: ")

    interactive = args.interactive
    if args.prompt == '-':
        print("Reading prompt from stdin...", file=sys.stderr)
        prompt = sys.stdin.read().strip()
    elif args.prompt is None:
        interactive = True
    else:
        prompt = args.prompt


    # Convert the list of key=value strings to a dictionary
    form_data = {}
    if args.data:
        for item in args.data:
            key, value = item.split('=')
            form_data[key] = value


    client = MechanicianClient(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password,
        token=args.token,
        root_ca_cert=args.root_ca_cert)

    
    if args.prompt:
        if interactive:
            asyncio.run(client.shell(args.ai_name, conversation_id=args.conversation_id, initial_prompt=prompt))
        else:
            asyncio.run(client.submit_prompt(args.ai_name, prompt, conversation_id=args.conversation_id))
    elif args.prompt_template and args.prompt_tool:
        template = client.get_prompt_template(args.prompt_template)
        prompt = client.call_prompt_tool(args.ai_name, args.prompt_tool, template, form_data=form_data).get("prompt", None)
        if prompt:
            if interactive:
                asyncio.run(client.shell(args.ai_name, conversation_id=args.conversation_id, initial_prompt=prompt))
            else:
                asyncio.run(client.submit_prompt(args.ai_name, prompt, conversation_id=args.conversation_id))
        else:
            print("Failed to retrieve prompt from server.", file=sys.stderr)
    else:
        asyncio.run(client.shell(args.ai_name, conversation_id=args.conversation_id))
    
