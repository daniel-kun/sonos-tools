#!/bin/bash

if [ -z "$SONOSTOOLS_GCP_API_KEY" ]
then
    echo "Error: env var \$SONOSTOOLS_GCP_API_KEY is not set."
fi

if [ -z "$SONOSTOOLS_MONGODB_CONNECTURI" ]
then
    echo "Error: env var \$SONOSTOOLS_MONGODB_CONNECTURI is not set."
fi

if [ "$1" != "--skip" ]
then
	pip3 install -r src/frontend/requirements.txt
	pip3 install -r src/api.tts/requirements.txt
	pushd .
	cd src/frontend/js && npm install
	popd
fi

if [ "$1" = "--cleandb" ] || [ "$2" = "--cleandb" ]
then
    echo "Cleaning DB..."
    mongo "$SONOSTOOLS_MONGODB_CONNECTURI" dev_start.cleandb.js
fi

SONOSTOOLS_FLASK_SECRET_KEY="JUST_SOME_RANDOM_BYTES" \
SONOSTOOLS_GOOGLE_AUTH_CLIENT_ID="XXX_GOOGLE_AUTH_CLIENT" \
SONOSTOOLS_API_TTS_ROOT="http://localhost:5001" \
SONOSTOOLS_SONOSAPI_APPKEY="XXX_SONOS_APPKEY" \
SONOSTOOLS_SONOSAPI_SECRET="XXX_SONOS_SECRET" \
SONOSTOOLS_SONOSAPI_ENDPOINT="http://localhost:5500" \
SONOSTOOLS_SONOSAPI_ENDPOINT_WS="http://localhost:5500" \
SONOSTOOLS_REDIRECT_ROOT="http://localhost:5000" \
SONOSTOOLS_ENV="DEVELOPMENT" \
FLASK_ENV="development" \
screen -c dev_start.screen

