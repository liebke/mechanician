<img src="../../docs/images/dm_templates_1600x840.png" alt="Daring Mechanician Notepads"  style="max-width: 100%; height: auto float: right;">

<p style="clear: both; margin-top: 0; font-family: 'Tratatello', serif; color: darkgrey;">


# Daring Mechanician Prompt Templates & Tools Example Project


## Install

Create a virtual environment and install the requirements.

```bash
conda create -n dm_prompt_template_env python=3.11
conda activate dm_prompt_template_env
```

Install the example project using pip:

```bash
pip install -e .
```

#### Run the interactive TAG AI shell:

```bash
./scripts/run.sh
```

### Run the AI-Driven tests:

```bash
./scripts/test.sh
```


## Exit the Virtual Environment and Clean Up

```bash
conda deactivate
conda remove --name dm_prompt_template_env --all
```