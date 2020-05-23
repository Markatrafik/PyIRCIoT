@ECHO OFF
SET SCRIPT=firstrun
SET IRC_TESTS=default isitip nicks masks
SET ROUTE_TESTS=default forwarding translation
SET LANG_TESTS=default lua js python pyrangefor
SET DLM=~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ~~~~~~~~~~
SETLOCAL EnableExtensions EnableDelayedExpansion
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
