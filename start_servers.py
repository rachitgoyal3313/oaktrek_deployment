import subprocess
import os
import signal
import sys
import time

def start_django_server():
    """Start the Django development server."""
    print("Starting Django server...")
    django_process = subprocess.Popen(
        ["python", "manage.py", "runserver"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return django_process

def start_flask_server():
    """Start the Flask application."""
    print("Starting Flask server...")
    flask_dir = os.path.join(os.getcwd(), "oaktrek_flask")
    flask_process = subprocess.Popen(
        ["python", "app.py"],
        cwd=flask_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return flask_process

def monitor_processes(django_process, flask_process):
    """Monitor both processes and handle termination."""
    try:
        while True:
            # Check if either process has terminated
            django_status = django_process.poll()
            flask_status = flask_process.poll()

            if django_status is not None:
                print(f"Django server terminated with exit code {django_status}")
                flask_process.terminate()
                break
            if flask_status is not None:
                print(f"Flask server terminated with exit code {flask_status}")
                django_process.terminate()
                break

            # Print output from both processes
            for line in iter(django_process.stdout.readline, ''):
                if line:
                    print(f"[Django] {line.strip()}")
            for line in iter(flask_process.stdout.readline, ''):
                if line:
                    print(f"[Flask] {line.strip()}")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nShutting down servers...")
        django_process.terminate()
        flask_process.terminate()
        try:
            django_process.wait(timeout=5)
            flask_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("Force killing processes...")
            django_process.kill()
            flask_process.kill()
        print("Servers stopped.")
        sys.exit(0)

def main():
    """Main function to start both servers."""
    # Ensure we're in the correct directory
    if not os.path.exists("manage.py"):
        print("Error: manage.py not found. Please run this script from the Django project root.")
        sys.exit(1)
    
    if not os.path.exists("oaktrek_flask/app.py"):
        print("Error: app.py not found in oaktrek_flask directory.")
        sys.exit(1)

    # Start both servers
    django_process = start_django_server()
    flask_process = start_flask_server()

    # Monitor processes
    monitor_processes(django_process, flask_process)

if __name__ == "__main__":
    main()