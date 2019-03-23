#!/bin/bash

VER="v3"
IMAGE="$SONOSTOOLS_DOCKER_REPO/sonos-tools-${SONOSTOOLS_DOCKER_IMAGE_PREFIX}_api.tts:$VER"

docker build -t "$IMAGE" .

if [ "$1" == "push" ]
then
    docker push "$IMAGE"
fi

