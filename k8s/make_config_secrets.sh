#!/bin/sh

kubectl delete configmap/secrets
kubectl create configmap secrets \
    --from-literal=sonos-tools.gcp_api_key=$SONOSTOOLS_GCP_API_KEY \
    --from-literal=sonos-tools.mongodb_connecturi=$SONOSTOOLS_MONGODB_CONNECTURI \
    --from-literal=sonos-tools.google_auth_client_id=$SONOSTOOLS_GOOGLE_AUTH_CLIENT_ID \
    --from-literal=sonos-tools.cluster_public_root=$SONOSTOOLS_CLUSTER_PUBLIC_ROOT \
    --from-literal=sonos-tools.redirect_root=$SONOSTOOLS_CLUSTER_PUBLIC_ROOT \
    --from-literal=sonos-tools.sonosapi_appkey=$SONOSTOOLS_SONOSAPI_APPKEY \
    --from-literal=sonos-tools.sonosapi_secret=$SONOSTOOLS_SONOSAPI_SECRET \
    --from-literal=sonos-tools.flask_secret="$SONOSTOOLS_FLASK_SECRET_KEY" \

kubectl delete configmap/secret-google-auth-clientfile
kubectl create configmap secret-google-auth-clientfile --from-file=$SONOSTOOLS_GOOGLE_AUTH_CLIENTFILE

