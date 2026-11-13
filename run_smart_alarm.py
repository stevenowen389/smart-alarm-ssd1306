#!/usr/bin/env python3
"""Run the Smart Alarm application from the repository root."""
import os
import sys
import runpy

repo_root = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.join(repo_root, 'smart-alarm')
script_path = os.path.join(project_path, 'smart_alarm.py')

if not os.path.isfile(script_path):
    print('ERROR: could not find a runnable smart_alarm entrypoint.', file=sys.stderr)
    sys.exit(2)

if project_path not in sys.path:
    sys.path.insert(0, project_path)
os.environ.setdefault('smart_alarm_path', project_path)
runpy.run_path(script_path, run_name='__main__')
