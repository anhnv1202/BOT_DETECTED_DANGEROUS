#!/usr/bin/env bash
set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
NONE='\033[0m'

# Load .env if exists (for DOCKER_USERNAME/DOCKER_PASSWORD/IMAGE_NAME)
if [ -f .env ]; then
  # shellcheck disable=SC1091
  source .env
fi

MODE="prod"

# Defaults
DOCKER_USERNAME=${DOCKER_USERNAME:-}
DOCKER_PASSWORD=${DOCKER_PASSWORD:-}
IMAGE_NAME=${IMAGE_NAME:-xdynamic-api}

if [ -z "${DOCKER_USERNAME}" ] || [ -z "${DOCKER_PASSWORD}" ]; then
  echo -e "[${RED}ERROR${NONE}] Missing DOCKER_USERNAME or DOCKER_PASSWORD env vars (.env)." >&2
  exit 1
fi

REPO="${DOCKER_USERNAME}/${IMAGE_NAME}"

echo -e "[${GREEN}START${NONE}] Building ${MODE} image for ${REPO}"

echo "Logging in to Docker Hub..."
echo "${DOCKER_PASSWORD}" | docker login --username "${DOCKER_USERNAME}" --password-stdin

echo -e "[${GREEN}Building image...${NONE}]"
docker build -t "${REPO}:cpu" . -f Dockerfile

echo -e "[${GREEN}Pushing image...${NONE}]"
docker push "${REPO}:cpu"

echo -e "[${GREEN}DONE${NONE}] Image pushed: ${REPO}:cpu"


