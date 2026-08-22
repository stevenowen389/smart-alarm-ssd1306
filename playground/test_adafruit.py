import sys
import traceback
import inspect

try:
    import Adafruit_GPIO
    print('Adafruit_GPIO loaded from:', inspect.getsourcefile(Adafruit_GPIO))
except Exception:
    print('Could not import Adafruit_GPIO')
    traceback.print_exc()
    sys.exit(1)

try:
    import Adafruit_GPIO.GPIO as G
    print('Probing platform GPIO...')
    try:
        platform = G.get_platform_gpio()
        print('get_platform_gpio() returned:', platform)
    except Exception:
        print('get_platform_gpio() raised:')
        traceback.print_exc()
        sys.exit(2)
except Exception:
    print('Could not import Adafruit_GPIO.GPIO')
    traceback.print_exc()
    sys.exit(3)
