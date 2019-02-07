#!/bin/sh

kubectl delete configmap/nginx-ingress-conf
kubectl create configmap nginx-ingress-conf --from-file=nginx.conf

