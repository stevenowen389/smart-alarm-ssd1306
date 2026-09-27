from apa102_pi.colorschemes import colorschemes


num_leds = 6

print('Rainbow Brightness 5 of 10')
cycle = colorschemes.Rainbow(num_led=num_leds, pause_value=0.05,
                             num_steps_per_cycle=255, num_cycles=2,
                             global_brightness=5)
cycle.start()

print('Just plain white for 3 seconds')
cycle = colorschemes.Solid(num_led=num_leds, pause_value=3,
                           num_steps_per_cycle=1, num_cycles=1)
cycle.start()