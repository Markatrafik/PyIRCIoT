#!/bin/bash

# PyIRCIoT iimakecert :: the service script for
# creating a set of cryptographic certificates

# * incomplete *

# Copyright (c) 2021 Alexey Y. Woronov

export OPENSSL_BIN="/usr/bin/openssl"

function err_exit () {
 echo "$1, exiting..."
 exit $2
}

for THE_BIN in "${OPENSSL_BIN}" ; do
 if [ ! -x "${THE_BIN}" ]; then
  err_exit "$0: Cannot find binary '${THE_BIN}'" 1
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
 echo

elif [ "${1}" == "NEW-SERVICE-CERT" -a "${2}" != "" ]; then
 echo

elif [ "${1}" == "NEW-CLIENT-CERT" -a "${2}" != "" ]; then
 echo

elif [ "${1}" == "CRL" -a -f "${2}" ]; then
 echo

else err_exit "$0: Incorrect parameters" 15 ; fi

exit 0
