#!/bin/bash

# PyIRCIoT iimakecert :: the service script for
# creating a set of cryptographic certificates

# * incomplete *

# Copyright (c) 2021 Alexey Y. Woronov

export THE_NAME="irciot"

export CA_SIZE="4096"
export CA_DAYS="3650"

export CA_KEY="${THE_NAME}-ca.key"
export CA_CRT="${THE_NAME}-ca.crt"

export MV_BIN="/bin/mv"
export OPENSSL_BIN="/usr/bin/openssl"
export RM_BIN="/bin/rm"

function err_exit () {
 echo "$1, exiting..."
 exit $2
}

for THE_BIN in "${MV_BIN}" "${OPENSSL_BIN}" "${RM_BIN}" ; do
 if [ ! -x "${THE_BIN}" ]; then
  err_exit "${0}: Cannot find binary '${THE_BIN}'" 1
 fi
done

if [ "${1}" == "" ]; then
 echo "Usage:"
 echo " ${0} NEW-CA"
 echo " ${0} NEW-SERVICE-CERT <service name> [<index>]"
 echo " ${0} NEW-CLIENT-CERT <client name> [<life in days>]"
 echo " ${0} CRL <certificate file name>"
 echo
 exit 0
elif [ "${1}" == "NEW-CA" ]; then
 "${MV_BIN}" "${CA_KEY}" "${CA_KEY}.old" 2>/dev/null
 "${MV_BIN}" "${CA_CRT}" "${CA_CRT}.old" 2>/dev/null
 "${OPENSSL_BIN}" genrsa -out "${CA_KEY}" ${CA_SIZE}
 ERRLV=$?
 if [ ${ERRLV} -ne 0 ]; then
  err_exit "${0}: Creation of CA key has been aborted"
 fi
 "${OPENSSL_BIN}" req -new -x509 -nodes -days ${CA_DAYS} \
  -key "${CA_KEY}" -out "${CA_CRT}"
 ERRLV=$?
 if [ ${ERRLV} -ne 0 ]; then
  "${RM_BIN}" -f "${CA_KEY}" 2>/dev/null
  err_exit "${0}: Creation of CA certificate has been aborted"
 fi
elif [ "${1}" == "NEW-SERVICE-CERT" -a "${2}" != "" ]; then
 echo

elif [ "${1}" == "NEW-CLIENT-CERT" -a "${2}" != "" ]; then
 echo

elif [ "${1}" == "CRL" -a -f "${2}" ]; then
 echo

else err_exit "$0: Incorrect parameters" 15 ; fi

exit 0
