@ECHO OFF
SET SCRIPT=firstrun
SET ROUTE_TESTS=default forwarding translation
SET ROUTE_TESTS=%ROUTE_TESTS% lmrstatuses gmrstatuses
SET IRC_TESTS=default isitip nicks masks langenc
SET LANG_TESTS=default lua js python pyrangefor pycosinus
SET BASE_TESTS=default multidatum multibigval multinextbig libirciot
SET BASE_TESTS=%BASE_TESTS% new2018datums defrag1b64p defrag2b64z
SET BASE_TESTS=%BASE_TESTS% test4rsa test4aes test2fish
SET BASE_ARGS1=base64 base85 base32 cryptrsa cryptaes crypt2fish
SET BASE_ARGS1=%BASE_ARGS1% cryptbz2
SET BASE_ARGS2=ed25519 rsa1024
SET BASE_UNARY=crc c1integrity c2integrity version
SET DLM=~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ~~~~~~~~~~
SETLOCAL EnableExtensions EnableDelayedExpansion
IF "%1"=="test_base" SET SCRIPT=irciot-test.py
IF "%1"=="test_irc" SET SCRIPT=rfc1459-test.py
IF "%1"=="test_route" SET SCRIPT=irciot_router-test.py
IF "%1"=="test_lang" SET SCRIPT=irciot_languages-test.py
IF %SCRIPT%==firstrun GOTO maintag
SET MYT=%2
FOR /L %%A IN (0,1,30) DO IF NOT "%MYT%"=="!MYT:~0,%%A!" (
SET /A Length+=1) ELSE ( SET /A LEN=!Length! )
FOR /L %%A IN (%LEN%,1,43) DO SET ALG=!ALG!.
<NUL SET /P strTemp="Test %2 %ALG% "
%SCRIPT% %2 2>NUL | find "TEST_IS_OK" > NUL
IF %ERRORLEVEL%==0 GOTO testok
%SCRIPT% %2 2>NUL | find "TEST_IS_SKIPPED" > NUL
IF %ERRORLEVEL%==0 GOTO testskip
ECHO FAILED
GOTO exittag
:testskip
ECHO OK:skipped
GOTO exittag
:testok
ECHO OK
GOTO exittag
:banfunc
SETLOCAL
ECHO .
ECHO %* tests ...
ECHO %DLM%
ENDLOCAL & EXIT /B
:maintag
CALL :banfunc Performing IRC-IoT basic tests
FOR /D %%i IN (%BASE_UNARY%) DO CALL %0 test_base %%i
FOR /D %%i IN (%BASE_TESTS%) DO CALL %0 test_base %%i
CALL :banfunc Performing trasnport layer IRC (RFC1459)
FOR /D %%i IN (%IRC_TESTS%) DO CALL %0 test_irc %%i
CALL :banfunc Performing IRC-IoT routing engine
FOR /D %%i IN (%ROUTE_TESTS%) DO CALL %0 test_route %%i
CALL :banfunc Performing Extrnal Languages (EL)
FOR /D %%i IN (%LANG_TESTS%) DO CALL %0 test_lang %%i
ECHO .
ECHO done
:exittag
ENDLOCAL
