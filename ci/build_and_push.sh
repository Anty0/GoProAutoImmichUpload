#!/usr/bin/env bash
set -euo pipefail

# This script builds and pushes Docker images with multiple tags.
# It is intended to be invoked by GitLab CI and requires Docker to be available.

IMAGE="${DOCKERHUB_REPO}"

# Base tag with short SHA
TAGS=("${IMAGE}:sha-${CI_COMMIT_SHORT_SHA}")

# Tag for git tag
if [[ -n "${CI_COMMIT_TAG:-}" ]]; then
  TAGS+=("${IMAGE}:${CI_COMMIT_TAG}")
fi

# Tags for default branch
if [[ "${CI_COMMIT_BRANCH:-}" == "${CI_DEFAULT_BRANCH:-}" ]]; then
  TAGS+=("${IMAGE}:latest")
  # Optional VERSION file tag
  if [[ -f VERSION ]]; then
    VERSION_TAG="$(tr -d $'\n\r' < VERSION | xargs)"
    if [[ -n "${VERSION_TAG}" ]]; then
      TAGS+=("${IMAGE}:${VERSION_TAG}")
    else
      echo "WARNING: VERSION file is empty; skipping version tag." >&2
    fi
  else
    echo "WARNING: VERSION file not found; skipping version tag." >&2
  fi
fi

echo "Will push tags: ${TAGS[*]}"

docker build \
  --file Dockerfile \
  $(printf -- ' -t %q' "${TAGS[@]}") \
  --push \
  .
