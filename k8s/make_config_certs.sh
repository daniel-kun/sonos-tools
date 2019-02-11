#!/bin/sh

kubectl delete secret/ingress-cert
sudo kubectl create secret tls ingress-cert --cert="${SONOSTOOLS_TLS_CERTFILE}" --key="${SONOSTOOLS_TLS_PRIVKEY}"

