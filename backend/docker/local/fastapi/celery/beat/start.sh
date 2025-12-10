#!/bin/bash

set -o errexit  # Exit on error
set -o nounset  # Exit on unset variable
set -o pipefail # Exit on pipe error


exec watchfiles --filter python celery.__main__.main --args '-A backend.app.core.celery_app beat -l INFO'