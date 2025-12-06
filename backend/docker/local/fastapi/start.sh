#!/bin/bash

set -o errexit  # Exit on error
set -o nounset  # Exit on unset variable
set -o pipefail # Exit on pipe error

exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload   # 0.0.0.0 means listen on all available interfaces