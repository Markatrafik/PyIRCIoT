#!/bin/bash

export SCRIPT_NAME="${0}"
export SCRIPT_DIR="$(/usr/bin/dirname "${SCRIPT_NAME}" 2>/dev/null)"
export TEST_IRCIOT_CMD="${SCRIPT_DIR}/irciot-test.py"
export TEST_IRCIOTR_CMD="${SCRIPT_DIR}/irciot_router-test.py"
export TEST_RFC1459_CMD="${SCRIPT_DIR}/rfc1459-test.py"
export TEST_LANGUAGES_CMD="${SCRIPT_DIR}/languages-test.py"
export TEST_IRCIOT_LIB="./irciot.py"
export TEST_IRCIOTR_LIB="./irciot_router.py"
export TEST_RFC1459_LIB="./rfc1459.py"
export TEST_LANGUAGES_LIB="./languages.py"

export GREP_BINARY="/bin/grep"
if [ ! -f "${GREP_BINARY}" -a -f "/usr/bin/grep" ]; then
 export GREP_BINARY="/usr/bin/grep" ; fi # Btw, MacOS

for TEST_CMD in "${TEST_IRCIOT_CMD}" "${TEST_IRCIOTR_CMD}" \
 "${TEST_RFC1459_CMD}" "${TEST_LANGUAGES_CMD}" ; do
if [ ! -x "${TEST_CMD}" ] ; then
 echo "Cannot find automatic test Python script: '${TEST_CMD}'"
fi
done

export TEST_COUNT=0
export TEST_OK=0
export TEST_FAILED=0

function checkascii () {
 LC_ALL=C "${GREP_BINARY}" -e '[^ -~]' "${1}" 1>/dev/null 2>/dev/null
 ERRLV=$?
 if [ ${ERRLV} -eq 0 ]; then
  echo "TEST_FAILED" ; else
  echo "TEST_IS_OK" ; fi
}

function resultat () {
 RESULT="\033[1;36m--- total: performed ${TEST_COUNT} tests"
 RESULT="${RESULT}, \033[1;32m${TEST_OK} ok\033[1;36m, \033[1;3"
 if [ ${TEST_FAILED} -eq 0 ]; then
  RESULT="${RESULT}6" ; else RESULT="${RESULT}1" ; fi
 RESULT="${RESULT}m${TEST_FAILED} failed \033[1;36m"
 while export RESULT="${RESULT}-" ; do
  RESLEN="${#RESULT}"
  if [ ${RESLEN} -gt 104 ]; then break ; fi
 done
 RESULT="${RESULT}\033[0m\n"
 echo -ne "${RESULT}\n"
}

function interrupt () {
 echo
 resultat
 echo -ne "\033[1mInterrupted by Ctrl-C\033[0m\n\n"
}

trap "interrupt ; exit 0" SIGINT

function run_tests () {
 TEST_NAME="'${4}' "
 if [ "x${5}x" == "xirciotx" ]; then
  export TEST_CMD="${TEST_IRCIOT_CMD}"
  export TEST_LIB="${TEST_IRCIOT_LIB}"
 elif [ "x${5}x" == "xirciot_languagesx" ]; then
  export TEST_CMD="${TEST_LANGUAGES_CMD}"
  export TEST_LIB="${TEST_LANGUAGES_LIB}"
 elif [ "x${5}x" == "xirciot_routerx" ]; then
  export TEST_CMD="${TEST_IRCIOTR_CMD}"
  export TEST_LIB="${TEST_IRCIOTR_LIB}"
 elif [ "x${5}x" == "xrfc1459x" ]; then
  export TEST_CMD="${TEST_RFC1459_CMD}"
  export TEST_LIB="${TEST_RFC1459_LIB}"
 else echo "Unknown section: '${5}'" ; exit 1 ; fi
 if [ "x${1}x" != "xx" ]; then
  export TEST_NAME="${TEST_NAME}'${1}' " ; fi
 if [ "x${2}x" != "xx" ]; then
  export TEST_NAME="${TEST_NAME}'${2}' " ; fi
 if [ "x${3}x" != "xx" ]; then
  export TEST_NAME="${TEST_NAME}'${3}' " ; fi
 while export TEST_NAME="${TEST_NAME}-" ; do
 TEST_LEN="${#TEST_NAME}"
 if [ ${TEST_LEN} -gt 49 ]; then break ; fi
 done
 echo -ne "Test ${TEST_NAME} "
 if [ "x${TEST_NAME:0:7}x" == "x'ascii'x" ]; then
   export OUTDATA="$(checkascii "${TEST_LIB}")"
 else export OUTDATA="$("${TEST_CMD}" \
  "${4}" "${1}" "${2}" "${3}" \
   2>/dev/null | /usr/bin/head -n 4096 2>/dev/null)" ; fi
 let TEST_COUNT=TEST_COUNT+1
 echo "${OUTDATA}" | "${GREP_BINARY}" -e "TEST_IS_OK" \
  1>/dev/null ; ERRLVOK=$?
 echo "${OUTDATA}" | "${GREP_BINARY}" -e "TEST_IS_SKIPPED" \
  1>/dev/null ; ERRLVSKIP=$?
 if [ ${ERRLVOK} -eq 0 -o ${ERRLVSKIP} -eq 0 ]; then
  echo -ne "\033[1;32mok\033[0m"
  let TEST_OK=TEST_OK+1
  if [ ${ERRLVSKIP} -eq 0 ]; then
   echo -ne "\033[32m:skipped\033[0m" ; fi
  echo ""
 else
  let TEST_FAILED=TEST_FAILED+1
  echo -ne "\033[1;31mfailed\033[0m\n" ; fi
}

if [ -x "${TEST_IRCIOT_CMD}" ]; then
echo -ne '\033[1;36m---------------- '
echo -ne 'PyLayerIRCIoT tests'
echo -ne ' ------------------\033[0m\n'
for m in ascii crc c1integrity c2integrity version test4rsa \
test4aes test2fish ; do
 run_tests "" "" "" "${m}" irciot
done
for j in "" big_mtu ; do
for k in "" ed25519 rsa1024 ; do
for l in "" base64 base85 base32 cryptrsa cryptaes ; do
for m in default libirciot bchsigning ; do
 run_tests "${j}" "${k}" "${l}" "${m}" irciot
done
done
done
done
fi

if [ -x "${TEST_RFC1459_CMD}" ]; then
echo -ne '\033[1;36m------------------ '
echo -ne 'PyLayerIRC tests'
echo -ne ' -------------------\033[0m\n'
for m in ascii isitip nicks masks langenc ; do
 run_tests "" "" "" "${m}" rfc1459
done
fi

if [ -x "${TEST_IRCIOTR_CMD}" ]; then
echo -ne '\033[1;36m--------------- '
echo -ne 'PyIRCIoT_router tests'
echo -ne ' -----------------\033[0m\n'
for j in "" big_mtu ; do
for m in ascii forwarding translation lmrstatuses gmrstatuses ; do
 run_tests "${j}" "" "" "${m}" irciot_router
done
done
fi

if [ -x "${TEST_RFC1459_CMD}" ]; then
echo -ne '\033[1;36m-------------- '
echo -ne 'PyLayerIRCIoT_EL_ tests'
echo -ne ' ----------------\033[0m\n'
for m in ascii lua js python pyrangefor pycosinus ; do
 run_tests "" "" "" "${m}" irciot_languages
done
fi

resultat

exit 0
