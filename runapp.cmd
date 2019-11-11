@ECHO OFF

rem Microsoft Windows Command Line Script
rem Author:	@kaloneh <kaloneh@gmail.com>
rem This script runs the application by setting necessary environment variables

SETLOCAL ENABLEEXTENSIONS

@IF "%OS%" == "Windows_NT" SETLOCAL

IF "%OS%" == "Windows_NT" (
  SET "DIRNAME=%~dp0%"
) ELSE (
  SET "DIRNAME=.\"
)

:set_env
FOR /F "eol=; tokens=1,2* delims==* " %%i in (%DIRNAME%.env_example) do SET "%%i=%%j"
FOR /F "usebackq tokens=1,2* delims==" %%i in (`SET`) do (
	IF /I "%%i"=="PYTHON_HOME" (
		IF EXIST "%%j\python.EXE" SET "__PYTHON_EXE__=%%j\python.EXE"
		IF EXIST "%%j\Scripts\flask.EXE" SET "__FLASK_EXE__=%%j\Scripts\flask.EXE"
	) ELSE (
		IF /I "%%i"=="PYTHON_PATH" (
			IF EXIST "%%j\python.EXE" SET "__PYTHON_EXE__=%%j\python.EXE"
			IF EXIST "%%j\Scripts\flask.EXE" SET "__FLASK_EXE__=%%j\Scripts\flask.EXE"
		)
	)
)
SET "__TOGO__=run"

REM echo %FLASK_APP%
REM echo %DATABASE_URL%

:set_executable
IF "X%PYTHON_PATH%"=="X" SET "__PYTHON_EXE__=python.EXE"
IF "X%__FLASK_EXE__%"=="X" SET "__FLASK_EXE__=flask.EXE"

IF "%1%"=="run" GOTO run
IF "%1%"=="test" (
	SET "__TOGO__=test"
	GOTO install
)
IF "%1%"=="install" (
	SET "__TOGO__=end"
	GOTO install 
)
IF "x%1%"=="x" GOTO install 
IF "%1%"=="help" (
CALL _help full
) ELSE (
GOTO _help
)

:run
rem License header here
"%__PYTHON_EXE__%" -V
if "%ERRORLEVEL%" NEQ "0" GOTO end
"%__FLASK_EXE__%" run
GOTO end

:test
ECHO testing FlackApp
pytest
GOTO end

:install
ECHO Installing requirements...
pip install -r requirements.txt
GOTO %__TOGO__%

:_help
ECHO runapp.cmd [options]
ECHO options
ECHO 	install	Install requirements from requirements.txt
ECHO 	run	Run the Flack application
ECHO 	test	Test the Flack application by running pytest
ECHO 	help	Print these lines.
ECHO 	If you run the script without option it installs 
ECHO 	Flack's requirements and then runs the Flack application.
ECHO 	Example:
ECHO 	runapp.cmd install

GOTO end

:end
SET "__PYTHON_EXE__="
SET "__FLASK_EXE__="
SET "__TOGO__="
IF "x!NOPAUSE!" == "x" PAUSE
rem IF "%ERRORLEVEL%" NEQ "0" ECHO %ERRORLEVEL%

:EOF
