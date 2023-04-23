"""
A simpler audio sampler that responds to button presses
from a raspberry pi. 

It supports n number of buttons each button plays a single
sample. Press and hold a button to play the assoicated sample,
releasing the button will stop the sample playing. 
"""
import os
import subprocess
from threading import Thread
import time

from gpiozero import Button
from signal import pause


# TODO: These should be passed in at runtime. 
num_buttons = 1
pins = [5]
samples = ['7vacuum.wav']

buttons = {} # Holds button objects
threads = {} # Holds threads for each button
stops = {} # Holds stop flags for each button


def start_sample(button: int) -> None:
    """
    Play a sample depending on the button pressed.

    The sample is started as a sub process using the aplay
    application. We poll the application to know when its
    completed, stopping the sample if a stop flag is detected.

    Args:
        button (int): 
    """
    print(f"Playing sample {button}.")
    process = subprocess.Popen(['aplay', samples[buttons]])

    status = None
    while status is None:
        status = process.poll()
        # Listen for the button stop flag which indicates the button has
        # been released and we should stop the sample playing. 
        if stops[button]:
            process.kill()

        time.sleep(0.1)

    stops[button] = False
    

def handle_button_press(button:int ) -> None: 
    """
    Handle a button press by starting playing a sample in
    a new thread. 

    Args:
        button (int): The id of the pressed button.
    """
    threads[button] = Thread(target=lambda: start_sample(button))
    threads[button].start()


def handle_button_release(button: int) -> None:
    """
    Handle a button release by setting the button stop flag
    to true.

    Args:
        button (int): The id of the released button.  
    """
    if threads[button] is not None:
        stops[button] = True
        # TODO: Test this with multiple simultaneous button presses.
        threads[button].join() 


def setup_sampler() -> None:
    """
    Perform initial setup of the sampler for the number of configured
    buttons. This creates the Button objects and assigns the listeners
    of the when_activated and when_deactivated events. 
    """
    for i in range(num_buttons):
        buttons[i] = Button(pins[i])
        threads[i] = None
        stops[i] = False

        buttons[i].when_activated = lambda: handle_button_press(i)
        buttons[i].when_deactivated = lambda: handle_button_release(i)


if __name__ == "__main":
    setup_sampler()
    
    print("Running..")
    pause()