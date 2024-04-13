
<img src="../../docs/images/dm_chroma_1600x840.png" alt="Daring Mechanician Chroma Resource Connector"  style="max-width: 100%; height: auto float: right;">

# Daring Mechanician-Chroma

This package provides **Daring Mechanician** `ResourceConnector` for interacting with Chroma Embedding database.

See [Daring Mechanician Github Repo](https://github.com/liebke/mechanician) for more information.


## Run Chroma in Docker (without persistence)

```bash
docker run -p 8080:8000 chromadb/chroma
```


## Run Chroma in Docker (with persistence)

```bash
git clone https://github.com/chroma-core/chroma.git
cd chroma
docker compose up --build
```