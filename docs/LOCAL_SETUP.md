# Local Setup Guide

Step-by-step guide to run SerpentAI locally on Windows and Linux.

## Prerequisites

- **Python 3.8+** (3.10 recommended)
- **Poetry** – [Install Poetry](https://python-poetry.org/docs/#installation)
- **Redis** – Required for frame buffers and analytics
- **Crossbar** – WAMP router for real-time messaging
- **CUDA** (optional) – For GPU-accelerated training (NVIDIA GPU)

## Option A: Docker (Recommended)

The easiest way to run Redis and Crossbar is via Docker Compose.

### 1. Install Docker

- **Windows:** [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Linux:** `sudo apt install docker.io docker-compose-plugin` (Ubuntu/Debian)

### 2. Clone and Install

```bash
git clone https://github.com/SerpentAI/SerpentAI.git
cd SerpentAI
poetry install
```

### 3. Start Services

```bash
docker compose up -d
```

This starts:
- **Redis** on `localhost:6379`
- **Crossbar** on `localhost:9999`

### 4. Setup SerpentAI

```bash
poetry run serpent setup
poetry run serpent dev_setup
```

`dev_setup` copies `config/config.yml` and `config/config.plugins.yml` to the project root so the framework finds them when you run commands from the repo.

### 5. SDK Setup (for plugin development)

From a project directory where you want to develop plugins:

```bash
poetry run serpent sdk_setup
```

### 6. Verify

```bash
poetry run serpent --help
poetry run serpent sdk_test_cuda   # Check CUDA availability
```

## Option B: Manual Redis and Crossbar

### Redis

**Windows:**
- [Memurai](https://www.memurai.com/) – Redis-compatible, installs as a Windows service
- Or run Redis in WSL2 or a Linux VM

**Linux:**
```bash
sudo apt install redis-server   # Ubuntu/Debian
sudo systemctl start redis
```

### Crossbar

Crossbar is installed with SerpentAI via Poetry. Run it from the project root (after `dev_setup`):

```bash
crossbar start
```

Ensure `crossbar.json` exists in the project root (created by `dev_setup`).

## Project Structure After Setup

```
SerpentAI/
├── config/
│   ├── config.yml          # Main config (Redis, Crossbar, etc.)
│   └── config.plugins.yml   # Plugin-specific config
├── crossbar.json           # WAMP router config
├── offshoot.yml            # Plugin discovery
├── offshoot.manifest.json
└── ...
```

## Data Directory

- **Windows:** `%APPDATA%\Serpent.AI`
- **Linux:** `~/.serpent`

Contains `plugins/games`, `plugins/game_agents`, `plugins/rl_agents`, and `config.json`.

## Optional: Tesseract (OCR)

For OCR in game agents:

**Windows:**
```bash
poetry run serpent download tesseract
```

**Linux:**
```bash
sudo apt install tesseract-ocr
```

## Optional: CUDA

For GPU training, install:
- NVIDIA drivers
- CUDA Toolkit
- cuDNN

PyTorch with CUDA is included in the default install. Run `poetry run serpent sdk_test_cuda` to verify.
