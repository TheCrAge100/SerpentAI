# Start Redis and Crossbar via Docker Compose for local SerpentAI development
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is required. Install Docker Desktop or Docker Engine."
    exit 1
}

docker compose up -d
Write-Host "Redis and Crossbar started. Redis: localhost:6379, Crossbar: localhost:9999"
