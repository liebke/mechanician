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
echo "please write a limerick about Frodo Baggins" | python3 -m mechanician_client.mecha --ai_name "Notepad Only AI" --prompt -
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

