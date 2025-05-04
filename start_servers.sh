#!/bin/bash

# Exit on any error
set -e

# Check if manage.py exists
if [ ! -f "manage.py" ]; then
    echo "Error: manage.py not found. Please run this script from the Django project root."
    exit 1
fi

# Check if oaktrek_flask/app.py exists
if [ ! -f "oaktrek_flask/app.py" ]; then
    echo "Error: app.py not found in oaktrek_flask directory."
    exit 1
fi

# Detect the operating system
OS=$(uname -s)

# Function to start servers based on OS
start_servers() {
    case "$OS" in
        Linux*)
            # For Linux (using gnome-terminal or xterm)
            if command -v gnome-terminal >/dev/null 2>&1; then
                gnome-terminal --tab --title="Django Server" -- bash -c "python manage.py runserver 8000; exec bash"
                gnome-terminal --tab --title="Flask Server" -- bash -c "cd oaktrek_flask && python app.py; exec bash"
            elif command -v xterm >/dev/null 2>&1; then
                xterm -T "Django Server" -e "python manage.py runserver 8000; bash" &
                xterm -T "Flask Server" -e "cd oaktrek_flask && python app.py; bash" &
            else
                echo "Error: No supported terminal (gnome-terminal or xterm) found."
                exit 1
            fi
            ;;
        Darwin*)
            # For macOS (using Terminal.app)
            osascript <<EOF
                tell application "Terminal"
                    do script "cd \"$PWD\" && python manage.py runserver 8000"
                    do script "cd \"$PWD/oaktrek_flask\" && python app.py"
                    activate
                end tell
EOF
            ;;
        CYGWIN*|MINGW*|MSYS*)
            # For Windows (using cmd or PowerShell)
            if command -v powershell >/dev/null 2>&1; then
                powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd \"$PWD\"; python manage.py runserver 8000'"
                powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd \"$PWD/oaktrek_flask\"; python app.py'"
            else
                start cmd /k "python manage.py runserver 8000"
                start cmd /k "cd oaktrek_flask && python app.py"
            fi
            ;;
        *)
            echo "Error: Unsupported operating system."
            exit 1
            ;;
    esac
}

echo "Starting Django server on port 8000 and Flask server on port 5000..."
start_servers
echo "Servers are starting in separate terminal windows."