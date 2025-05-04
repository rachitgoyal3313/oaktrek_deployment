@echo off
setlocal EnableDelayedExpansion

:: Check if manage.py exists
if not exist "manage.py" (
    echo Error: manage.py not found. Please run this script from the Django project root.
    exit /b 1
)

:: Check if oaktrek_flask/app.py exists
if not exist "oaktrek_flask\app.py" (
    echo Error: app.py not found in oaktrek_flask directory.
    exit /b 1
)

echo Starting Django server on port 8000 and Flask server on port 5000...

:: Start Django server in a new command prompt
start "Django Server" cmd /k "python manage.py runserver 8000"

:: Start Flask server in a new command prompt
start "Flask Server" cmd /k "cd oaktrek_flask && python app.py"

echo Servers are starting in separate terminal windows.
exit /b 0