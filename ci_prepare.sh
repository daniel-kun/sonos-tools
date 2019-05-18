#!/bin/bash

mkdir -p ${HOME}/.kube
SONOSTOOLS_KUBECONFIG=${HOME}/.kube/config
SONOSTOOLS_TLS_CERTFILE=${HOME}/.ci_tmpfiles/cert
SONOSTOOLS_TLS_PRIVKEY=${HOME}/.ci_tmpfiles/privkey

rm -rvf ${HOME}/.ci_tmpfiles/
mkdir ${HOME}/.ci_tmpfiles

# Just for testing:

echo "${SONOSTOOLS_KUBECONFIG_BASE64}" | base64 -d > ${SONOSTOOLS_KUBECONFIG}
echo "${SONOSTOOLS_TLS_CERTFILE_BASE64}" | base64 -d > ${SONOSTOOLS_TLS_CERTFILE}
echo "${SONOSTOOLS_TLS_PRIVKEY_BASE64}" | base64 -d > ${SONOSTOOLS_TLS_PRIVKEY}

echo "kubeconf md5: `md5sum ${SONOSTOOLS_KUBECONFIG}`"
echo "TLS cert md5: `md5sum ${SONOSTOOLS_TLS_CERTFILE}`"
echo "TLS key  md5: `md5sum ${SONOSTOOLS_TLS_PRIVKEY}`"

echo "Logging into docker:"
echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USERNAME}" --password-stdin
echo "Building and pushing docker images:"
COMMIT=`git log --pretty=format:'%H' -n 1`
VER="commit${COMMIT}"
./build.sh "$VER"
./deploy_dev.sh "$VER"

