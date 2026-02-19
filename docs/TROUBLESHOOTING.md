# Troubleshooting

Common issues and solutions when running SerpentAI locally.

## Config not found

**Error:** `Configuration file not found at: 'config/config.yml'`

**Cause:** The framework loads config relative to the current working directory.

**Fix:**
1. Run from the SerpentAI project root (where `config/` exists)
2. Or run `poetry run serpent dev_setup` to copy config to the project root

## Redis connection refused

**Error:** `ConnectionRefusedError` or `redis.exceptions.ConnectionError` when connecting to Redis

**Cause:** Redis is not running or not reachable on `localhost:6379`.

**Fix:**
1. Start Redis: `docker compose up -d` (if using Docker)
2. Or start Redis manually (Memurai on Windows, `redis-server` on Linux)
3. Verify: `redis-cli ping` should return `PONG`

## Crossbar not starting

**Error:** Crossbar fails to start or WAMP connection fails

**Cause:** Port 9999 in use, or config missing.

**Fix:**
1. Ensure `crossbar.json` exists in project root (run `serpent dev_setup`)
2. Check port 9999 is free: `netstat -an | findstr 9999` (Windows) or `lsof -i :9999` (Linux)
3. If using Docker: `docker compose up -d` starts Crossbar with the correct config

## CUDA not available

**Output:** `sdk_test_cuda` prints "Failure! CUDA cannot be used"

**Causes:**
- No NVIDIA GPU
- NVIDIA drivers not installed or outdated
- CUDA/cuDNN not installed
- PyTorch CPU-only build installed

**Fix:**
- SerpentAI works without CUDA (CPU-only, slower training)
- For GPU: Install [NVIDIA drivers](https://www.nvidia.com/Download/index.aspx), [CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit-archive), and cuDNN
- Reinstall PyTorch with CUDA: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118` (or `cu121` for CUDA 12.1)

## Tesseract not found

**Error:** OCR-related errors, "No Tesseract executable could be found"

**Fix:**
- **Windows:** `poetry run serpent download tesseract` or install from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) and add to PATH
- **Linux:** `sudo apt install tesseract-ocr`

## Poetry install fails

**Error:** Dependency resolution or build failures

**Fix:**
1. Ensure Python 3.8+: `python --version`
2. Update Poetry: `poetry self update`
3. Clear cache: `poetry cache clear pypi --all`
4. On Windows: Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) for compiling native extensions

## Offshoot / plugin discovery

**Error:** Plugins not found, offshoot config errors

**Fix:**
1. Ensure `offshoot.yml` and `offshoot.manifest.json` exist in project root
2. Run `serpent dev_setup` to copy them
3. Plugin directories: `plugins/games`, `plugins/game_agents`, `plugins/rl_agents`

## PyTorch / TensorFlow conflicts

**Error:** Version conflicts or import errors

**Fix:**
- The stack uses PyTorch 1.5 and TensorFlow 2.2. If you hit conflicts, try a fresh Poetry env: `poetry env remove python` then `poetry install`
