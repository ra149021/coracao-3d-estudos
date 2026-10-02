#!/usr/bin/env bash
set -euo pipefail
pecas_project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$pecas_project_dir/scripts/serve_heart.py" --port 8891 --page specimens.html --open
