# Daring mechanician_client.mechanician Client


## Example Usage


```bash
python3 -m mechanician_client.mecha --interactive True --username liebke
python3 -m mechanician_client.mecha --interactive True --username liebke --ai_name "Notepad Only AI" --conversation_id "20240511120705" --root_ca_cert ../../examples/studio_demo/certs/rootCA.pem
python3 -m mechanician_client.mecha --interactive True --username liebke --ai_name "Notepad Only AI"
python3 -m mechanician_client.mecha --interactive True --ai_name "Notepad Only AI"
echo "please write a limerick about Frodo Baggins" | python3 -m mechanician_client.mecha --username liebke --ai_name "Notepad Only AI" --prompt - --root_ca_cert ../../examples/studio_demo/certs/rootCA.pem
echo "please write a limerick about Frodo Baggins" | python3 -m mechanician_client.mecha --ai_name "Notepad Only AI" --root_ca_cert ../../examples/studio_demo/certs/rootCA.pem --prompt -
python3 -m mechanician_client.mecha --ai_name "Notepad Only AI" --root_ca_cert ../../examples/studio_demo/certs/rootCA.pem --prompt "please write a limerick about Frodo Baggins"

echo "what is an ETF?" | python3 -m mechanician_client.mecha --ai_name "Contracts Copilot AI" --prompt -
echo "what does FX stand for?" | python3 -m mechanician_client.mecha --ai_name "Contracts Copilot AI" --prompt -
python3 -m mechanician_client.mecha --interactive True --ai_name "Contracts Copilot AI"

python3 -m mechanician_client.mecha --username liebke --prompt_template event_invite.md --root_ca_cert ../../examples/studio_demo/certs/rootCA.pem
python3 -m mechanician_client.mecha --interactive true --username liebke --ai_name "Notepad Only AI" --prompt_template event_invite.md --prompt_tool event_invite --data contact=Lobelia event=Eleventy-first --root_ca_cert ../../examples/studio_demo/certs/rootCA.pem

{ echo "Write a concise Git commit message summarizing the following `git diff`\n--------"; git diff; }| python3 -m mechanician_client.mecha --ai_name "Notepad Only AI" --root_ca_cert ../../examples/studio_demo/certs/rootCA.pem --prompt -

{ echo "Write a concise Git commit message summarizing the following `git diff --cached`\n--------"; git diff; }| python3 -m mechanician_client.mecha --ai_name "Notepad Only AI" --root_ca_cert ../../examples/studio_demo/certs/rootCA.pem --prompt -


{ echo "Write a concise Git commit message summarizing the following `git diff 3b455fd98ccf75aa79ca16b83baab8608faed29c`\n--------"; git diff; }| python3 -m mechanician_client.mecha --ai_name "Notepad Only AI" --root_ca_cert ../../examples/studio_demo/certs/rootCA.pem --prompt -

```

