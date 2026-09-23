"""App entrypoint. Wires up display, clock, audio, alarm loop and web server,
then runs them concurrently under uasyncio.
"""
import uasyncio as asyncio

from modules import clock, display, audio, alarm, web


async def main():
    clk = clock.Clock()
    disp = display.Display()
    snd = audio.Audio()
    alarm_ctrl = alarm.Alarm(clk, disp, snd)

    asyncio.create_task(alarm_ctrl.run())
    asyncio.create_task(web.serve(alarm_ctrl))

    while True:
        disp.render_clock(clk.now())
        await asyncio.sleep(1)


asyncio.run(main())
