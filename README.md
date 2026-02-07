# ServerSeeker

High‑performance internet server discovery & rescanning platform, built around a Rust scanner backend, PostgreSQL storage, and a live Python Streamlit WebUI.

> **Based on:** Funtimes909’s ServerSeekerV2
> [https://github.com/Funtimes909/ServerSeekerV2/](https://github.com/Funtimes909/ServerSeekerV2/)

This project is a fork/derivative with architectural tweaks, Docker support, and a live web interface.

---

## Contents

- [Features](#features)
- [Setup](#setup)
  - [Prerequisites](#prerequisites)
- [Config](#config)
  - [Masscan configuration](#masscan-configuration)
  - [Country detection (IP geolocation)](#country-detection-ip-geolocation)
  - [Database credentials](#database-credentials)
  - [Shared buffers tuning](#shared-buffers-tuning)
- [WebUI](#webui)
- [Configuration files](#configuration-files)
  - [Main configs](#main-configs)
  - [Dockerfiles](#dockerfiles)
- [Credits](#credits)
- [License](#license)

---

## Features

* ⚡ Rust‑based high‑speed scanner
* 📦 Full Docker + docker‑compose deployment
* 🌐 Live Streamlit WebUI
* 🗄 PostgreSQL backend
* 🔁 Discovery + Rescanner modes
* 🌍 Region detection via IPInfo API
* 🐧 Tested on Linux

---

# Setup

### Prerequisites
- [Docker](https://www.docker.com/get-started/)
- [Git](https://github.com/git-guides/install-git)
- [IPInfo API Key](https://ipinfo.io/dashboard)

```bash
git clone https://github.com/sensoorr/ServerSeeker.git
cd ServerSeeker

docker compose build
docker compose up -d
```

Then open:

```
http://localhost:8501
```

## Config

### Masscan configuration

Recommended values for `scanner/masscan.conf -> rate`:

* `1000` – very stable
* `2500` – stable
* `5000` – common default
* `10000` – works, but potential for packet loss

Note: Values above 10,000 may cause significant packet loss on home connections.


### Country detection (IP Geolocation)

To enable server country detection:

1. Create an account at:

```
https://ipinfo.io/dashboard
```

2. Generate an API key

3. Add it to:

* `./scanner/config.toml`

```toml
ipinfo_token = ""
```

## Database credentials

Credentials are defined in *multiple locations* and must be kept in sync:

You will typically need to edit:

* `docker-compose.yml` (Postgres service)
* `./scanner/config.toml`
* `./webui/app.py`

Look for:

* Database name
* Username
* Password
* Host
* Port

Note: Mismatched credentials will cause connection failures.

### Shared buffers tuning

You may want to tune PostgreSQL memory usage in `docker-compose.yml -> db`:

```yaml
command: postgres -c synchronous_commit=off -c fsync=off -c shared_buffers=4GB
```

**Rule of thumb (community guideline, not official PostgreSQL recommendation):**

* `shared_buffers ≈ 15–25% of your system's RAM ($$$)`

Example:

* 16GB RAM -> 4GB
* 32GB RAM -> 8GB

---

## WebUI

Streamlit interface is available at:

```
http://localhost:8501
```

Provides:
- Live view of database content
- Searching by MOTD or IP
- Filtering by minimum online players
- Filtering by server software
- Filtering by server version

---

## Configuration files

### Main configs

* `./docker-compose.yml`
* `./webui/app.py`
* `./scanner/config.toml`
* `./scanner/masscan.conf`

### Dockerfiles

* `./webui/Dockerfile`
* `./scanner/Dockerfile`

---

## Credits

* Original project:
  **Funtimes909 – ServerSeekerV2**
  [https://github.com/Funtimes909/ServerSeekerV2/](https://github.com/Funtimes909/ServerSeekerV2/)

* SQL schema source:
  [https://github.com/fuuuuuuuuuuuuuuck/ServerSeekerV2-guide](https://github.com/fuuuuuuuuuuuuuuck/ServerSeekerV2-guide)

---

## License

GNU GPLv3 (inherited from ServerSeekerV2)

Modified by **Sensoorr**, 2026
