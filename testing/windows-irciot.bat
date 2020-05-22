@ECHO OFF
SET SCRIPT=firstrun
IF "%1"=="test_irc" SET SCRIPT=rfc1459-test.py
IF "%1"=="test_route" SET SCRIPT=irciot_router-test.py
IF "%1"=="test_lang" SET SCRIPT=irciot_languages-test.py
iF %SCRIPT%==firstrun GOTO maintag
<NUL SET /P strTemp="Test %2 ... "
%SCRIPT% %2 2>NUL | find "TEST_IS_OK" > NUL
IF %ERRORLEVEL%==0 GOTO testok
ECHO FAILED
GOTO exittag
:testok
ECHO OK
GOTO exittag
:maintag
ECHO Performing trasnport layer IRC (RFC1459) tests ...
SET IRC_TESTS=default isitip nicks masks
FOR /D %%i IN (%IRC_TESTS%) DO CALL %0 test_irc %%i
ECHO Performing IRC-IoT routing engine tests ...
SET IRC_ROUTE=forwarding translation
FOR /D %%i IN (%IRC_TESTS%) DO CALL %0 test_route %%i
ECHO Performing Extrnal Languages (EL) tests ...
SET LANG_TESTS=lua js python pyrangefor
FOR /D %%i IN (%LANG_TESTS%) DO CALL %0 test_lang %%i
ECHO done
:exittag
