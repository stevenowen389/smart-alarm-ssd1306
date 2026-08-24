import sys
import os
apa102_path = os.environ.get('APA102_PI_PATH', os.path.expanduser('~/APA102_Pi'))
sys.path.append(os.path.abspath(apa102_path))
import colorschemes


numLEDs = 9

print('Rainbow Brightness 5of10')
myCycle = colorschemes.Rainbow(numLEDs=numLEDs, pauseValue=0.05, numStepsPerCycle = 255, numCycles = 2, globalBrightness=5)
myCycle.start()

print('Just plain white for 3 seconds')
myCycle = colorschemes.Solid(numLEDs=numLEDs, pauseValue=3, numStepsPerCycle = 1, numCycles = 1)
myCycle.start()




