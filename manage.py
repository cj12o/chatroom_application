#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import subprocess

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

def updateReq():
    subprocess.run(args="python -m pip freeze > requirements.txt",shell=True)

# def setup_periodic_task():
#     subprocess.run(args="python manage.py setup_periodic_task",shell=True)

if __name__ == '__main__':
   
    # setup_periodic_task()
    main()
    # updateReq()

    
