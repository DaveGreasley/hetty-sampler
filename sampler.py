import os
import subprocess
from threading import Thread
import time

from gpiozero import Button
from signal import pause


B1 = 'CatA'
B2 = 'CatB'

b1 = Button(17)

threads = {
    B1: None,
    B2: None,
}

stops = {
    B1: False,
    B2: False, 
}

def start_sample(button):
    print("Playing sample.")
    process = subprocess.Popen(['aplay', '/home/pi/hetty-sampler/samples/7vacuum.wav'])

    status = None
    while status is None:
        status = process.poll()
        if stops[button]:
            process.kill()

        time.sleep(0.1)

    stops[button] = False
    

def handle_button_press(button):
    threads[button] = Thread(target=lambda: start_sample(button))
    threads[button].start()


def handle_button_release(button):
    if threads[button] is not None:
        stops[button] = True
        threads[button].join()


b1.when_activated = lambda: print("Activated")
b1.when_deactivated = lambda: handle_button_release(B1)


print("Running..")
pause()