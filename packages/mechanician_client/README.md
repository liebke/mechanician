# Daring mechanician_client.mechanician Client


## Example Usage


```bash
python3 -m mechanician_client.mecha --interactive --username liebke --no_ssl_verify
python3 -m mechanician_client.mecha --interactive --username liebke --root_ca_cert ../../examples/studio_demo/certs/rootCA.pem
python3 -m mechanician_client.mecha --interactive --username liebke --ai_name "Notepad Only AI" --conversation_id "20240511120705" --root_ca_cert ../../examples/studio_demo/certs/rootCA.pem
python3 -m mechanician_client.mecha --interactive --username liebke --ai_name "Notepad Only AI" # FAILS becuase of SSL verification
python3 -m mechanician_client.mecha --interactive --ai_name "Notepad Only AI"
echo "please write a limerick about Frodo Baggins" | python3 -m mechanician_client.mecha --username liebke --ai_name "Notepad Only AI" --prompt - --root_ca_cert ../../examples/studio_demo/certs/rootCA.pem
echo "please write a limerick about Frodo Baggins" | python3 -m mechanician_client.mecha --ai_name "Notepad Only AI" --root_ca_cert ../../examples/studio_demo/certs/rootCA.pem --prompt -
echo "please write a limerick about Frodo Baggins" | python3 -m mechanician_client.mecha --ai_name "Notepad Only AI" --no_ssl_verify --prompt -
python3 -m mechanician_client.mecha --ai_name "Notepad Only AI" --root_ca_cert ../../examples/studio_demo/certs/rootCA.pem --prompt "please write a limerick about Frodo Baggins"

echo "what is an ETF?" | python3 -m mechanician_client.mecha --ai_name "Contracts Copilot AI" --prompt -
echo "what does FX stand for?" | python3 -m mechanician_client.mecha --ai_name "Contracts Copilot AI" --prompt -
python3 -m mechanician_client.mecha --interactive --ai_name "Contracts Copilot AI"

python3 -m mechanician_client.mecha --username liebke --prompt_template event_invite.md --root_ca_cert ../../examples/studio_demo/certs/rootCA.pem
python3 -m mechanician_client.mecha --interactive --username liebke --ai_name "Notepad Only AI" --prompt_template event_invite.md --prompt_tool event_invite --data contact=Lobelia event=Eleventy-first --root_ca_cert ../../examples/studio_demo/certs/rootCA.pem

{ echo "Write a concise Git commit message summarizing the following `git diff` \n--------"; git diff; }| python3 -m mechanician_client.mecha --ai_name "Notepad Only AI" --root_ca_cert ../../examples/studio_demo/certs/rootCA.pem --prompt -

# Generate a commit message based on the staged changes
{ echo "Write a concise Git commit message summarizing the following `git diff --cached`\n--------"; git diff; }| python3 -m mechanician_client.mecha --ai_name "Notepad Only AI" --root_ca_cert ../../examples/studio_demo/certs/rootCA.pem --prompt -

# Generate a commit message based on the changes since a specific commit
{ echo "Write a concise Git commit message summarizing the following `git diff 3b455fd98ccf75aa79ca16b83baab8608faed29c`\n--------"; git diff; }| python3 -m mechanician_client.mecha --ai_name "Notepad Only AI" --root_ca_cert ../../examples/studio_demo/certs/rootCA.pem --prompt -

```

```bash
{ echo "Write a concise Git commit message summarizing the following `git diff 3b455fd98ccf75aa79ca16b83baab8608faed29c`\n--------"; git diff; }| python3 -m mechanician_client.mecha --ai_name "Notepad Only AI" --root_ca_cert ./certs/rootCA.pem --prompt - | ../../packages/mechanician_client/scripts/tts

echo "hello David, how are you doing this morning?" | ../../packages/mechanician_client/scripts/tts



echo "please write a limerick about Frodo Baggins" | python3 -m mechanician_client.mecha --ai_name "Notepad Only AI" --no_ssl_verify --prompt - | tee /dev/tty | ../../packages/mechanician_client/scripts/tts

echo "please write an epic poem about Samwise Gamgee" | python3 -m mechanician_client.mecha --ai_name "Notepad Only AI" --no_ssl_verify --prompt - | tee /dev/tty | ../../packages/mechanician_client/scripts/tts

echo "What was the first movie that the star of the upcoming movie Furiosa starred in?" | python3 -m mechanician_client.mecha --ai_name "TMDB AI" --no_ssl_verify --prompt - | tee /dev/tty | ../../packages/mechanician_client/scripts/tts
```


```bash
python3 -m mechanician_client.stt


python3 -m mechanician_client.stt | cat


python3 -m mechanician_client.stt | python3 -m mechanician_client.mecha --username liebke --ai_name "Notepad Only AI" --no_ssl_verify --prompt - | tee /dev/tty | ../../packages/mechanician_client/scripts/tts


python3 -m mechanician_client.stt | python3 -m mechanician_client.mecha --username liebke --ai_name "TMDB AI" --no_ssl_verify --prompt - | tee /dev/tty | ../../packages/mechanician_client/scripts/tts

# Is Harrison Ford going to star in any upcoming movies?


python3 -m mechanician_client.mecha --username liebke --ai_name "TMDB AI" --no_ssl_verify --input voice | tee /dev/tty | ../../packages/mechanician_client/scripts/tts


python3 -m mechanician_client.mecha --ai_name "TMDB AI" --no_ssl_verify --input voice --output voice --interactive
# Is Harrison Ford going to star in any upcoming movies?
# Is there going to be a new Star Wars movie coming out?

python3 -m mechanician_client.mecha --ai_name "Contracts Copilot AI" --no_ssl_verify --prompt input --output voice --interative
# What does FX stand for?
# What does SSPP stand for?
# 1.	What is an out of contract (OOC) vessel charged on a volume discount agreement (VDA) contract?
# 2.	What vessels does the VDA discount apply to?
# 3.	What are the Wholesale Partner VDA re-commitment options on 36 and 60month plans?
# 4.	And what are the re-commitment options on the 1, 6 and 12month plans?
# 5.	What happens if a partner does not complete the hardware buy-in for Y1 of their VDA?
# 6.	How much does the XpressSwitch Incentive deduct from the signed TCV over 36m?
# 7.	How is a Downgrade Fee (DF) calculated?
# 8.	In the FX Hardware Incentive how many free antennas does a partner receive for a bulk order of 13 units?
# 9.	An OOC vessel on a legacy 36 month FX plan downgrades to a Pivot 36month plan. Which statement is true?
#    a.	DF applies and a new 36month contract period starts automatically.
#    b.	DF applies and vessel remains OOC.
#    c.	No DF applies and a new 36 month contract period starts automatically.
#    d.	No DF applies and vessel remains OOC.
# 10.	My vessel has 6 months contract remaining and moves from legacy to Pivot, to a higher ARPU plan. What else do I need to do to prevent a DF?


```



## Usage Instructions

To use the Mechanician Client, you can execute commands in the terminal. Here's a breakdown of the command structure:

```bash
python3 -m mechanician_client.mecha [options]
```

### Common Options

- `--interactive`: Launches the client in interactive mode.
- `--username [name]`: Specifies the username for the session.
- `--ai_name [AI name]`: Selects the specific AI to interact with.
- `--no_ssl_verify`: Disables SSL certificate verification.
- `--root_ca_cert [path]`: Specifies the path to the root CA certificate for SSL verification.
- `--prompt [text]`: Sends a direct text prompt to the AI.
- `--prompt_template [file]`: Specifies a prompt template file.
- `--prompt_tool [tool]`: Specifies the tool to use with the prompt.
- `--data [key=value]`: Provides data for the prompt in key-value pairs.
- `--conversation_id [id]`: Specifies a conversation ID to resume a session.


### Examples

1. **Interactive Mode:**

    ```bash
    python3 -m mechanician_client.mecha --interactive --username liebke
    ```

2. **SSL Verification with a Root CA Certificate:**

    ```bash
    python3 -m mechanician_client.mecha --username liebke --root_ca_cert path/to/cert.pem
    ```

3. **Sending a Prompt to an AI:**

    ```bash
    echo "please write a limerick about Frodo Baggins" | python3 -m mechanician_client.mecha --ai_name "Notepad Only AI" --prompt -
    ```

4. **Using Prompt Templates and Tools:**

    ```bash
    python3 -m mechanician_client.mecha --interactive --username liebke --ai_name "Notepad Only AI" --prompt_template event_invite.md --prompt_tool event_invite --data contact=Lobelia event=Eleventy-first
    ```

5. **Generating Git Commit Messages:**

    ```bash
    { echo "Write a concise Git commit message summarizing the following `git diff`\n--------"; git diff; } | python3 -m mechanician_client.mecha --ai_name "Notepad Only AI" --prompt -
    ```

### Troubleshooting

If you encounter issues with SSL verification failures, ensure that you are using the correct path to the root CA certificate or try running the client with the `--no_ssl_verify` option.

