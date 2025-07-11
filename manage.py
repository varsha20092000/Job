#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


import os
from django.core.management import call_command

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Jobs.settings')

    # Add this block to load data during deployment if not already loaded
    if os.environ.get("RENDER") == "true":
        try:
            call_command("loaddata", "App/jobs.json")
            print("Jobs data loaded successfully.")
        except Exception as e:
            print("Error loading jobs data:", e)

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)



if __name__ == '__main__':
    main()
