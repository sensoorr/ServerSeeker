# ServerSeeker

High-performance internet server discovery & rescanning platform, built around a Rust scanner backend, PostgreSQL storage, and a live Python Streamlit WebUI.

> **Based on:** Funtimes909’s ServerSeekerV2
> [https://github.com/Funtimes909/ServerSeekerV2/](https://github.com/Funtimes909/ServerSeekerV2/)

This project is a fork/derivative with architectural tweaks, Docker support, and a live web interface.

---

## Contents

* [Features](#features)
* [Setup](#setup)
  * [Prerequisites](#prerequisites)
  * [Initial configuration (required)](#initial-configuration-required)
  * [Build & run](#build--run)
* [Config](#config)
  * [Masscan configuration](#masscan-configuration)
  * [Database credentials](#database-credentials)
  * [Shared buffers tuning](#shared-buffers-tuning)
* [WebUI](#webui)
* [Configuration files](#configuration-files)
* [Credits](#credits)
* [License](#license)

---

## Features

* ⚡ Rust-based high-speed scanner
* 📦 Full Docker + docker-compose deployment
* 🌐 Live Streamlit WebUI
* 🗄 PostgreSQL backend
* 🔁 Discovery + Rescanner modes
* 🌍 Region detection via IPInfo API
* 🐧 Tested on Linux

---

# Setup

### Prerequisites

* [Docker](https://www.docker.com/get-started/)
* [Git](https://github.com/git-guides/install-git)
* [IPInfo API Key](https://ipinfo.io/dashboard)

---

### Initial configuration (required)


#### 1. Clone the repository

```bash
git clone https://github.com/sensoorr/ServerSeeker.git
cd ServerSeeker
```

#### 2. Add your IPInfo API key

Create an account at:

```
https://ipinfo.io/dashboard
```

Navigate to `./scanner/config.toml` and add your IPInfo token:

```toml
ipinfo_token = "YOUR_API_KEY_HERE"
```

---

## Build & run

After configuration is complete:

```bash
docker compose build
docker compose up -d
```

Then open:

[`http://localhost:8501`](http://localhost:8501)

Note: Initial startup may take a few minutes while IP data is collected.

---

## Config

### Masscan configuration

Recommended values for `scanner/masscan.conf -> rate`:

* `1000` – very stable
* `2500` – stable
* `5000` – common default
* `10000` – works, but potential for packet loss

> Values above 10,000 may cause significant packet loss on home connections.

---

## Database credentials

Credentials are defined in **multiple locations** and must be kept in sync:

* `docker-compose.yml` (Postgres service)
* `./scanner/config.toml`
* `./webui/app.py`

Ensure consistency for:

* Database name
* Username
* Password
* Host
* Port

> Mismatched credentials will cause connection failures.

---

### Shared buffers tuning

PostgreSQL memory tuning in `docker-compose.yml -> db`:

```yaml
command: postgres -c synchronous_commit=off -c fsync=off -c shared_buffers=4GB
```

Guideline:

* `shared_buffers ≈ 15–25% of system RAM`

Examples:

* 16GB RAM → 4GB
* 32GB RAM → 8GB

---

## WebUI

Streamlit interface:

```
http://localhost:8501
```

Features:

* Live database view
* Search by MOTD or IP
* Filter by online players
* Filter by server software
* Filter by server version

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

**Original project:**
Funtimes909 – ServerSeekerV2
[https://github.com/Funtimes909/ServerSeekerV2/](https://github.com/Funtimes909/ServerSeekerV2/)

**SQL schema source:**
[https://github.com/fuuuuuuuuuuuuuuck/ServerSeekerV2-guide](https://github.com/fuuuuuuuuuuuuuuck/ServerSeekerV2-guide)

---

## License

GNU GPLv3 (inherited from ServerSeekerV2)

Modified by **Sensoorr**, 2026
