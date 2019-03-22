#!/bin/bash

if [ $1 -n "--skip" ]
then
	pip3 install -r src/frontend/requirements.txt
	pip3 install -r src/api.tts/requirements.txt
	pushd .
	cd src/frontend/js && npm install
	popd
fi

screen -c dev_start.screen
