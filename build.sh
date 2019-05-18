#!/bin/bash

VER=$1

build() {
    echo "Building docker image \"$1\" version \"${VER}\""
    IMAGE="${SONOSTOOLS_DOCKER_REPO}/sonos-tools-${SONOSTOOLS_DOCKER_IMAGE_PREFIX}_$1:${VER}"
    docker build -t "${IMAGE}" "src/$1"
    docker push "${IMAGE}"
}

build "base_images"
build "frontend"
build "api.tts"

