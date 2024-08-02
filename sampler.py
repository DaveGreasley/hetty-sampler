#!/usr/bin/python
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
from typing import Dict
import time

from gpiozero import Button
from signal import pause


# TODO: These should be passed in at runtime. 
num_buttons = 5
pins = [17, 18, 24, 25, 27]
samples = ['11506_woowah_Hooooover.wav', 'hoova002.wav',
           'Hoover 24.wav', 'tape Shifter Hoover.wav', '9 Bar.wav']

buttons = {} # Holds button objects
threads = {} # Holds threads for each button
processes = {}


def start_sample(button: int) -> None:
    """
    Play a sample depending on the button pressed.

    The sample is started as a sub process using the aplay
    application.

    Args:
        button (int): The id of the pressed button
    """
    print(f"Playing sample {button}.")
    sample_path = f"/home/pi/hetty-sampler/samples/{samples[button]}"
    processes[button] = subprocess.Popen(['aplay', sample_path])
    
    

def handle_button_press(button:int ) -> None: 
    """
    Handle a button press by starting playing a sample in
    a new thread. 

    Args:
        button (int): The id of the pressed button.
    """
    if threads[button] is None:
        threads[button] = Thread(target=lambda: start_sample(button))
        threads[button].start()


def handle_button_release(button: int) -> None:
    """
    Handle a button release by setting the button stop flag
    to true.

    Args:
        button (int): The id of the released button.  
    """
    if processes[button] is not None:
        processes[button].kill()
        processes[button] = None
        threads[button] = None


def create_button_press_handler(i):
    def handle():
        handle_button_press(i)

    return handle


def create_button_release_handler(i):
    def handle():
        handle_button_release(i)

    return handle


def setup_sampler() -> None:
    """
    Perform initial setup of the sampler for the number of configured
    buttons. This creates the Button objects and assigns the listeners
    of the when_activated and when_deactivated events. 
    """
    for i in range(len(pins)):
        b = Button(pins[i])
        b.when_activated = create_button_press_handler(i)
        b.when_deactivated = create_button_release_handler(i)

        buttons[i] = b
        threads[i] = None
        processes[i] = None

       
if __name__ == "__main__":
    setup_sampler()
    
    print("Running..")
    pause()