# Run SerpentAI locally: start services, ensure config, then run serpent
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$SerpentArgs
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

if (-not $SerpentArgs) { $SerpentArgs = @("--help") }

# Start Docker services
if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker compose up -d 2>$null
}

# Ensure config exists (dev_setup)
$ConfigDir = Join-Path $ProjectRoot "config"
if (-not (Test-Path (Join-Path $ConfigDir "config.yml"))) {
    Write-Host "Running dev_setup to create config..."
    poetry run serpent dev_setup
}

# Run serpent with given command
poetry run serpent @SerpentArgs
