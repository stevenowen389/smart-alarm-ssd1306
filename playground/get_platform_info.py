#!/usr/bin/env python3
import sys
import traceback
import inspect
import importlib
import subprocess
import os

print('--- Adafruit_GPIO import info ---')
try:
    import Adafruit_GPIO
    print('Adafruit_GPIO file:', inspect.getsourcefile(Adafruit_GPIO))
except Exception:
    print('Could not import Adafruit_GPIO')
    traceback.print_exc()

print('\n--- Adafruit_GPIO.GPIO probe ---')
try:
    import Adafruit_GPIO.GPIO as G
    print('has get_platform_gpio:', hasattr(G, 'get_platform_gpio'))
    print('\nget_platform_gpio source:\n')
    try:
        print(inspect.getsource(G.get_platform_gpio))
    except Exception:
        print('<could not show source>')

    try:
        print('\nCalling get_platform_gpio()...')
        platform = G.get_platform_gpio()
        print('get_platform_gpio() returned:', platform)
    except Exception:
        print('get_platform_gpio() raised:')
        traceback.print_exc()
except Exception:
    print('Could not import Adafruit_GPIO.GPIO')
    traceback.print_exc()

print('\n--- Python / environment ---')
print('exe:', sys.executable)
print('version:', sys.version.splitlines()[0])
print('sys.path[0:8]=', sys.path[0:8])

print('\nRPi.GPIO spec:')
try:
    print(importlib.util.find_spec('RPi.GPIO'))
except Exception:
    traceback.print_exc()

print('\n--- device nodes ---')
for p in ('/dev/gpiomem', '/dev/mem'):
    try:
        st = os.stat(p)
        print(p, 'exists, mode:', oct(st.st_mode))
    except Exception as e:
        print(p, 'not present or inaccessible:', e)

print('\n/dev/i2c-*:')
try:
    for path in sorted([p for p in os.listdir('/dev') if p.startswith('i2c-')]):
        full = os.path.join('/dev', path)
        try:
            st = os.stat(full)
            print(full, 'mode:', oct(st.st_mode))
        except Exception as e:
            print(full, 'inaccessible:', e)
except Exception:
    print('/dev listing failed')

print('\n--- i2cdetect -y 1 (may require i2c-tools) ---')
try:
    r = subprocess.run(['i2cdetect', '-y', '1'], capture_output=True, text=True)
    print(r.stdout)
    if r.stderr:
        print('stderr:', r.stderr)
except Exception as e:
    print('i2cdetect failed:', e)

print('\n--- done ---')
