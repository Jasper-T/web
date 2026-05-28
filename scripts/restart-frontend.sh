#!/usr/bin/env bash
set -euo pipefail

docker compose -f "$(pwd)/docker-compose.yml" restart webui-frontend
