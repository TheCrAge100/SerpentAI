#!/usr/bin/env bash
# Run SerpentAI locally: start services, ensure config, then run serpent
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

if [ $# -eq 0 ]; then COMMAND=("--help"); else COMMAND=("$@"); fi

# Start Docker services
if command -v docker &> /dev/null; then
    docker compose up -d 2>/dev/null || true
fi

# Ensure config exists (dev_setup)
if [[ ! -f "$PROJECT_ROOT/config/config.yml" ]]; then
    echo "Running dev_setup to create config..."
    poetry run serpent dev_setup
fi

# Run serpent with given command
poetry run serpent "${COMMAND[@]}"
