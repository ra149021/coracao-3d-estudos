#!/usr/bin/env bash
set -euo pipefail
coracao_project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$coracao_project_dir/scripts/serve_heart.py" --open
