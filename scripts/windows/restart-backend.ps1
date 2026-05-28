$ErrorActionPreference = "Stop"

docker compose -f (Join-Path (Get-Location) "docker-compose.yml") restart webui-backend
