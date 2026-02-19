#!/usr/bin/env bash
# Start Redis and Crossbar via Docker Compose for local SerpentAI development
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

if ! command -v docker &> /dev/null; then
    echo "Docker is required. Install Docker Engine." >&2
    exit 1
fi

docker compose up -d
echo "Redis and Crossbar started. Redis: localhost:6379, Crossbar: localhost:9999"
