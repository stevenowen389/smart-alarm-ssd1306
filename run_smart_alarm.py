#!/usr/bin/env python3
"""Small launcher to run the smart_alarm project from the repo root.

This wrapper avoids import/filename collisions between the package directory
and the legacy executable also named ``smart_alarm`` inside it.

Run with the project's venv Python, e.g.:
  /home/steven/smart_alarm/.venv/bin/python run_smart_alarm.py

The launcher tries, in order:
 1. import the smart_alarm package and call smart_alarm.main() or run it as a module
 2. fallback to executing ``smart_alarm/smart_alarm``

"""
import os
import sys
import runpy

repo_root = os.path.dirname(os.path.abspath(__file__))
# Ensure the repo root is first on sys.path so package imports resolve to the local copy
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Helper: try to import package and run canonical entrypoints
try:
    import smart_alarm as _pkg
except Exception:
    _pkg = None

if _pkg is not None:
    # Prefer well-known entry points if present
    if hasattr(_pkg, 'main') and callable(_pkg.main):
        sys.exit(_pkg.main())
    if hasattr(_pkg, 'run') and callable(_pkg.run):
        sys.exit(_pkg.run())
    # As a last resort try running package as a module
    try:
        runpy.run_module('smart_alarm', run_name='__main__')
        sys.exit(0)
    except Exception:
        # fallthrough to trying the top-level script
        pass

# Fallback: run the legacy executable inside the smart_alarm project directory.
script_path = os.path.join(repo_root, 'smart_alarm', 'smart_alarm')
if os.path.isfile(script_path):
    project_path = os.path.dirname(script_path)
    if project_path not in sys.path:
        sys.path.insert(0, project_path)
    os.environ.setdefault('smart_alarm_path', project_path)
    runpy.run_path(script_path, run_name='__main__')
else:
    print('ERROR: could not find a runnable smart_alarm entrypoint.', file=sys.stderr)
    sys.exit(2)
