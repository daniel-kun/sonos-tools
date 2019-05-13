#!/bin/bash

SONOSTOOLS_KUBECONFIG=${HOME}/.ci_tmpfiles/kube_config
SONOSTOOLS_TLS_CERTFILE=${HOME}/.ci_tmpfiles/cert
SONOSTOOLS_TLS_PRIVKEY=${HOME}/.ci_tmpfiles/privkey

rm -rvf ${HOME}/.ci_tmpfiles/
mkdir ${HOME}/.ci_tmpfiles

# Just for testing:
echo "Inside ci_prepare.sh:
${SONOSTOOLS_KUBECONFIG_BASE64}"

echo "${SONOSTOOLS_KUBECONFIG_BASE64}" | base64 -d > ${SONOSTOOLS_KUBECONFIG}
echo "${SONOSTOOLS_TLS_CERTFILE_BASE64}" | base64 -d > ${SONOSTOOLS_TLS_CERTFILE}
echo "${SONOSTOOLS_TLS_PRIVKEY_BASE64}" | base64 -d > ${SONOSTOOLS_TLS_PRIVKEY}

