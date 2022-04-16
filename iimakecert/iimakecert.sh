#!/bin/bash

# PyIRCIoT iimakecert :: the service script for
# creating a set of cryptographic certificates

# * incomplete *

# Copyright (c) 2021 Alexey Y. Woronov

export THE_NAME="irciot"

SERVICE_NAME="service"
CLIENT_NAME="client"

CA_SIZE=4096
CA_DAYS=3650

CRL_DAYS=3650

SERVICE_SIZE=4096
SERVICE_DAYS=1095

CLIENT_DAYS=365
CLIENT_SIZE=2048

if [ "${2}" != "" ]; then
 SERVICE_NAME="${2}"
 CLIENT_NAME="${2}"
fi

CA_KEY="${THE_NAME}-ca.key"
CA_CRT="${THE_NAME}-ca.crt"

F_NAME="${THE_NAME}-${SERVICE_NAME}"
SERVICE_KEY="${F_NAME}.key"
SERVICE_TMP="${F_NAME}.csr"
SERVICE_CRT="${F_NAME}.crt"

F_NAME="${THE_NAME}-${CLIENT_NAME}"
CLIENT_KEY="${F_NAME}.key"
CLIENT_TMP="${F_NAME}.csr"
CLIENT_CRT="${F_NAME}.crt"
CLINET_CRL="${F_NAME}.crl"

DH_PEM="${F_NAME}-dh.pem"

BASENAME_BIN="/usr/bin/basename"
DIRNAME_BIN="/usr/bin/dirname"
MV_BIN="/bin/mv"
OPENSSL_BIN="/usr/bin/openssl"
RM_BIN="/bin/rm"
TOUCH_BIN="/usr/bin/touch"

function err_exit () {
 echo "${1}, exiting..."
 exit ${2}
}

function err_msg () {
 ERRMSG="Creation of ${2} has been aborted"
 err_exit "$("${BASENAME_BIN}" "${1}"): ${ERRMSG} (${3})" ${4}
}

for THE_BIN in "${BASENAME_BIN}" "${DIRNAME_BIN}" \
 "${MV_BIN}" "${OPENSSL_BIN}" "${RM_BIN}" ; do
 if [ ! -x "${THE_BIN}" ]; then
  ERRMSG="Cannot find binary '${THE_BIN}'"
  err_exit "$("${BASENAME_BIN}" "${0}"): ${ERRMSG}" 1
 fi
done

function get_conf () {
 THE_CONF="openssl-${1}.conf"
 for THE_PATH in "$(${DIRNAME_BIN} "${0}")" "." ; do
  if [ -f "${THE_PATH}/${THE_CONF}" ]; then
   if [ "${1}" != "ca" ]; then
    for THE_FILE in "index.txt" "index.txt.attr" ; do
     "${TOUCH_BIN}" "${THE_PATH}/${THE_FILE}" 2>/dev/null
    done
   fi
   echo "${THE_PATH}/${THE_CONF}"
   return
  fi
 done
}

function get_serial () {
 for THE_PATH in "$("${DIRNAME_BIN}" "${0}")" "." ; do
  if [ -s "${THE_PATH}/serial" ]; then
   echo "${THE_PATH}/serial"
   return
  fi
 done
 echo "01" > "./serial" 2>/dev/null
 echo "./serial"
}

if [ "${1}" == "" ]; then
 echo "Usage:"
 echo " ${0} NEW-CA"
 echo " ${0} NEW-SERVICE-CERT [<service name>] [<index>]"
 echo " ${0} NEW-CLIENT-CERT [<client name>] [<life in days>]"
 echo " ${0} GEN-DH [<service name>]"
 echo " ${0} CRL <certificate file name>"
 echo
 exit 0
elif [ "${1}" == "NEW-CA" ]; then
 export OPENSSL_CONF="$(get_conf ca)"
 "${MV_BIN}" -f "${CA_KEY}" "${CA_KEY}.old" 2>/dev/null
 "${MV_BIN}" -f "${CA_CRT}" "${CA_CRT}.old" 2>/dev/null
 "${OPENSSL_BIN}" genrsa -out "${CA_KEY}" ${CA_SIZE}
 ERRLV=$?
 if [ ${ERRLV} -ne 0 ]; then
  err_msg "${0}" "CA key" ${ERRLV} 11
 fi
 "${OPENSSL_BIN}" req -new -x509 -nodes -days ${CA_DAYS} \
  -key "${CA_KEY}" -out "${CA_CRT}"
 ERRLV=$?
 if [ ${ERRLV} -ne 0 ]; then
  "${RM_BIN}" -f "${CA_KEY}" 2>/dev/null
  err_msg "${0}" "CA certificate" ${ERRLV} 12
 fi
elif [ "${1}" == "NEW-SERVICE-CERT" ]; then
 export OPENSSL_CONF="$(get_conf service)"
 "${MV_BIN}" -f "${SERVICE_KEY}" "${SERVICE_KEY}.old" 2>/dev/null
 "${MV_BIN}" -f "${SERVICE_CRT}" "${SERVICE_CRT}.old" 2>/dev/null
 "${OPENSSL_BIN}" genrsa -out "${SERVICE_KEY}" ${SERVICE_SIZE}
 ERRLV=$?
 if [ ${ERRLV} -ne 0 ]; then
  err_msg "${0}" "service key" ${ERRLV} 11
 fi
 "${OPENSSL_BIN}" req -new -x509 -nodes -days ${SERVICE_DAYS} \
  -key "${SERVICE_KEY}" -out "${SERVICE_TMP}" \
  -config "${OPENSSL_CONF}"
 ERRLV=$?
 if [ ${ERRLV} -eq 0 ]; then
  "${OPENSSL_BIN}" x509 -days "${SERVICE_DAYS}" \
   -inform PEM -in "${SERVICE_TMP}" -signkey "${SERVICE_KEY}" \
   -out "${SERVICE_CRT}" -CA "${CA_CRT}" -CAkey "${CA_KEY}" \
   -CAserial "$(get_serial ca)"
   ERRLV=$?
 fi
 "${RM_BIN}" -f "${SERVICE_TMP}" 2>/dev/null
 if [ ${ERRLV} -ne 0 ]; then
  "${RM_BIN}" -f "${SERVICE_KEY}" 2>/dev/null
  err_msg "${0}" "service certificate" ${ERRLV} 12
 fi
elif [ "${1}" == "NEW-CLIENT-CERT" ]; then
 export OPENSSL_CONF="$(get_conf client)"
 if [ "${3}" != "" ]; then CLIENT_DAYS="${3}" ; fi
 "${MV_BIN}" -f "${CLIENT_KEY}" "${CLIENT_KEY}.old" 2>/dev/null
 "${MV_BIN}" -f "${CLIENT_CRT}" "${CLIENT_CRT}.old" 2>/dev/null
 "${OPENSSL_BIN}" genrsa -out "${CLIENT_KEY}" ${CLIENT_SIZE}
 ERRLV=$?
 if [ ${ERRLV} -ne 0 ]; then
  err_msg "${0}" "client key" ${ERRLV} 11
 fi
 "${OPENSSL_BIN}" req -new -x509 -nodes -days ${SERVICE_DAYS} \
  -key "${CLIENT_KEY}" -out "${CLIENT_TMP}" \
  -config "${OPENSSL_CONF}"
 ERRLV=$?
 if [ ${ERRLV} -eq 0 ]; then
  "${OPENSSL_BIN}" x509 -days "${CLIENT_DAYS}" \
   -inform PEM -in "${CLIENT_TMP}" -signkey "${SERVICE_KEY}" \
   -out "${CLIENT_CRT}" -CA "${CA_CRT}" -CAkey "${CA_KEY}" \
   -CAserial "$(get_serial ca)"
   ERRLV=$?
 fi
 "${RM_BIN}" -f "${CLIENT_TMP}" 2>/dev/null
 if [ ${ERRLV} -ne 0 ]; then
  "${RM_BIN}" -f "${CLIENT_KEY}" 2>/dev/null
  err_msg "${0}" "client certificate" ${ERRLV} 12
 fi
elif [ "${1}" == "GEN-DH" ]; then
 "${MV_BIN}" -f "${DH_PEM}" "${DH_PEM}.old" 2>/dev/null
 "${OPENSSL_BIN}" dhparam -out "${DH_PEM}" ${SERVICE_SIZE}
elif [ "${1}" == "CRL" -a -f "${2}" ]; then
 DIR_NAME="$("${DIRNAME_BIN}" "${2}" 2>/dev/null)"
 if [ "${DIR_NAME}" == "" ]; then DIR_NAME="." ; fi
 export OPENSSL_CONF="$(get_conf ca)"
 REVOKE_NAME="${DIR_NAME}/$("${BASENAME_BIN}" "${2}" .crt).crl"

else err_exit "${0}: Incorrect parameters" 15 ; fi

exit 0
