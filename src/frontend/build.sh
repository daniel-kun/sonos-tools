#!/bin/bash

VER="v3"
IMAGE="$SONOSTOOLS_DOCKER_REPO/sonos-tools_frontend:$VER"

docker build -t "$IMAGE" .

if [ "$1" == "push" ]
then
    docker push "$IMAGE"
fi

