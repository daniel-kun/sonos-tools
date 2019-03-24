#!/bin/bash

source ~/.sonostools-dev.env

helm install charts/sonos-tools \
    --set Env="${SONOSTOOLS_ENV}" \
    --set ClusterPublicIP="${SONOSTOOLS_CLUSTER_PUBLIC_IP}" \
    --set ClusterPublicRoot="${SONOSTOOLS_CLUSTER_PUBLIC_ROOT}" \
    --set DockerRepo="${SONOSTOOLS_DOCKER_REPO}" \
    --set DockerImagePrefix="${SONOSTOOLS_DOCKER_IMAGE_PREFIX}" \
    --set FlaskSecret="${SONOSTOOLS_FLASK_SECRET_KEY}" \
    --set GcpApiKey="${SONOSTOOLS_GCP_API_KEY}" \
    --set GoogleAuthClientId="${SONOSTOOLS_GOOGLE_AUTH_CLIENT_ID}" \
    --set MongoDBConnectUri="${SONOSTOOLS_MONGODB_CONNECTURI}" \
    --set RedirectRoot="${SONOSTOOLS_REDIRECT_ROOT}" \
    --set SonosApiEndpoint="${SONOSTOOLS_SONOSAPI_ENDPOINT}" \
    --set SonosApiEndpointWS="${SONOSTOOLS_SONOSAPI_ENDPOINT_WS}" \
    --set SonosApiAppKey="${SONOSTOOLS_SONOSAPI_APPKEY}" \
    --set SonosApiAppSecret="${SONOSTOOLS_SONOSAPI_SECRET}" \
    --set-file TlsCert="${SONOSTOOLS_TLS_CERTFILE}"  \
    --set-file TlsKey="${SONOSTOOLS_TLS_PRIVKEY}" \
;

