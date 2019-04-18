#!/bin/bash

VER="v25"
IMAGE="$SONOSTOOLS_DOCKER_REPO/sonos-tools-${SONOSTOOLS_DOCKER_IMAGE_PREFIX}_frontend:$VER"

docker build -t "$IMAGE" .

if [ "$1" == "push" ]
then
    docker push "$IMAGE"
fi

