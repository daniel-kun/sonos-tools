#!/bin/bash

SONOSTOOLS_KUBECONFIG=${HOME}/.ci_tmpfiles/kube_config
SONOSTOOLS_TLS_CERTFILE=${HOME}/.ci_tmpfiles/cert
SONOSTOOLS_TLS_PRIVKEY=${HOME}/.ci_tmpfiles/privkey

rm -rvf ${HOME}/.ci_tmpfiles/
mkdir ${HOME}/.ci_tmpfiles

# Just for testing:

echo "================== 1"
echo "${SONOSTOOLS_KUBECONFIG_BASE64}" | base64 -d > ${SONOSTOOLS_KUBECONFIG}
cat ${SONOSTOOLS_KUBECONFIG}
echo "================== 2"
echo "${SONOSTOOLS_TLS_CERTFILE_BASE64}" | base64 -d > ${SONOSTOOLS_TLS_CERTFILE}
cat ${SONOSTOOLS_TLS_CERTFILE}
echo "================== 3"
echo "${SONOSTOOLS_TLS_PRIVKEY_BASE64}" | base64 -d > ${SONOSTOOLS_TLS_PRIVKEY}
cat ${SONOSTOOLS_TLS_PRIVKEY}

