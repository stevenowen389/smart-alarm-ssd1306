#!/usr/bin/env python3
"""Small launcher to run the smart_alarm project from the repo root.

This wrapper avoids import/filename collisions when there is both a top-level
script named ``smart_alarm`` and a package directory ``smart_alarm/``.

Run with the project's venv Python, e.g.:
  /home/steven/smart_alarm/.venv/bin/python run_smart_alarm.py

The launcher tries, in order:
 1. import the smart_alarm package and call smart_alarm.main() or run it as a module
 2. fallback to executing the top-level script file named "smart_alarm" in the repo root

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

# Fallback: run the repository's top-level script file named `smart_alarm`
script_path = os.path.join(repo_root, 'smart_alarm')
if os.path.isfile(script_path):
    runpy.run_path(script_path, run_name='__main__')
else:
    print('ERROR: could not find a runnable smart_alarm entrypoint (no package import and no top-level script).', file=sys.stderr)
    sys.exit(2)
