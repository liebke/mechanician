

<img src="../../docs/images/dm_studio_1600x840.png" alt="Daring Mechanician Studio"  style="max-width: 100%; height: auto float: right;">

<p style="clear: both; margin-top: 0; font-family: 'Tratatello', serif; color: darkgrey;">


# Daring Mechanician Studio


## Install

Create a virtual environment and install the requirements.

```bash
conda create -n studio_demo_env python=3.11
conda activate studio_demo_env
```

Install the example project using pip:

```bash
pip install -e .
```

or

```bash
./scripts/dev_install.sh
```


## SSL Certificates for Local Development: mkcert

https://github.com/FiloSottile/mkcert

```bash
brew install mkcert
```

```bash
mkcert -install
```

```bash
mkdir certs
```

```bash
mkcert -key-file ./certs/key.pem -cert-file ./certs/cert.pem localhost 127.0.0.1 ::1
```

```bash
uvicorn.run("mechanician_studio.main:app", host="127.0.0.1", port=8000, ssl_keyfile="./certs/key.pem", ssl_certfile="./certs/cert.pem")
```


#### Run the Mechanician Studio:

```bash
./scripts/run.sh
```


## Exit the Virtual Environment and Clean Up

```bash
conda deactivate
conda remove --name studio_demo_env --all
```