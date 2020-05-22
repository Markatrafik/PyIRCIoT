@ECHO OFF
SET SCRIPT=firstrun
SET IRC_TESTS=default isitip nicks masks
SET ROUTE_TESTS=default forwarding translation
SET LANG_TESTS=default lua js python pyrangefor
IF "%1"=="test_irc" SET SCRIPT=rfc1459-test.py
IF "%1"=="test_route" SET SCRIPT=irciot_router-test.py
IF "%1"=="test_lang" SET SCRIPT=irciot_languages-test.py
iF %SCRIPT%==firstrun GOTO maintag
<NUL SET /P strTemp="Test %2 ... "
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
:maintag
ECHO Performing trasnport layer IRC (RFC1459) tests ...
FOR /D %%i IN (%IRC_TESTS%) DO CALL %0 test_irc %%i
ECHO Performing IRC-IoT routing engine tests ...
FOR /D %%i IN (%ROUTE_TESTS%) DO CALL %0 test_route %%i
ECHO Performing Extrnal Languages (EL) tests ...
FOR /D %%i IN (%LANG_TESTS%) DO CALL %0 test_lang %%i
ECHO done
:exittag
