"""
Copyright (C) 2020 Triad Semiconductor

ts4112.py - Simple example program to configure the TS4112
            and put the device into sleep and watch modes

            It alternates between "looking for light" for
            1 second and "power save mode" for 1 second.

Created by: Reid Wender

"""

import digitalio
import board
from time import sleep

# Configuration word for th TS4112

config_word = "00010000000001"

# Pinout for Adafruit ItsyBitsy M4
# Modify the pin assignments to match your board

# D or DATA pin of the TS4112
d = digitalio.DigitalInOut(board.D9)
d.switch_to_input(pull=digitalio.Pull.UP)

# E or ENVELOPE pin of the TS4112
e = digitalio.DigitalInOut(board.D7)
e.switch_to_input(pull=None)

d.switch_to_output(value=True, drive_mode=digitalio.DriveMode.PUSH_PULL)
e.switch_to_output(value=True, drive_mode=digitalio.DriveMode.PUSH_PULL)

######

# Force the TS4112 into SLEEP mode regardless of the state of the TS4112
# Sleep is a low power operation mode

def force_reset():
    d.switch_to_input(pull=None)
    e.switch_to_input(pull=None)

    d.switch_to_output(value=False, drive_mode=digitalio.DriveMode.PUSH_PULL)
    e.switch_to_output(value=False, drive_mode=digitalio.DriveMode.PUSH_PULL)
    d.value = True

    e.value = False
    e.value = True

    e.value = False
    e.value = True

    d.value = False
    d.value = True

    d.switch_to_input(pull=None)
    e.switch_to_input(pull=None)

#########

# Put the TS4112 into WATCH mode looking for modulated light pulses
# This function assumes that the device is already in SLEEP mode before
# goto_watch is called

def goto_watch():
    e.switch_to_output(value=False, drive_mode=digitalio.DriveMode.PUSH_PULL)
    d.switch_to_output(value=False, drive_mode=digitalio.DriveMode.PUSH_PULL)
    #e.value = True
    e.switch_to_input(pull=None)
    d.switch_to_input(pull=None)

#########

# Check the state of the TS4112 by looking at the status of the D and E pins.
# Take the reading 3 times on the off chance that swept laser light from a
# basestation is hitting the photodiode while the D/E pins are being checked
# If the TS4112 is used in a non SteamVR application the a check_bus should be
# changed to match the environment. For example, if you know when modulated
# IR light is being sent then check_bus might not need a multi-attempt check
# but could rather be a single check of the D/E lines

def check_bus():
    print("In Check Bus")
    d.switch_to_input(pull=None)
    e.switch_to_input(pull=None)

    unknown_count, trans_count, sleep3_count, invalid_count = 0,0,0,0

    for i in range(3):
        e_state = e.value
        d_state = d.value

        if (e_state == False):
            if (d_state == False):
                invalid_count += 1
            else:
                trans_count += 1
        else:
            if (d_state == False):
                unknown_count += 1
            else:
                sleep3_count += 1

    if (unknown_count  >= 2): state = 0
    elif (trans_count  >= 2): state = 1
    elif (sleep3_count >= 2): state = 2
    else:                     state = 3

    print("BUS State: ", state)
    return state

######################################################################

# Write the configuration word to the TS4112
# This function assumes that the TS4112 is in SLEEP state

def write_config(config_word):

    e.switch_to_output(value = True, drive_mode=digitalio.DriveMode.PUSH_PULL)
    d.switch_to_output(value = True, drive_mode=digitalio.DriveMode.PUSH_PULL)

    # D low while E (CLK) high starts configuration mode

    d.value = False
    e.value = False

    # E (CLK) pulse while D low indicates configuration write

    e.value = True
    e.value = False

    # Write the 14 bits of the config word on the D pin and pulse E (clk)
    # for each bit to clock into the TS4112. Send bit 13 first, bit 0 last

    for bit in config_word:
        if (bit == '1'): d.value = True
        else:            d.value = False
        e.value = True
        e.value = False

    # End the Config Write Sequence by bringing D high while E is high

    d.value = False
    e.value = True
    d.value = True

    e.switch_to_input(pull = None)
    d.switch_to_input(pull = None)

###################################################

# Read back the configuration word from the TS4112

def read_config():
    readback = ""

    e.switch_to_output(value = True, drive_mode=digitalio.DriveMode.PUSH_PULL)
    d.switch_to_output(value = True, drive_mode=digitalio.DriveMode.PUSH_PULL)
    d.value = False
    e.value = False
    d.value = True
    e.value = True
    d.switch_to_input(pull=None)
    e.value = False

    for i in range(14):
        e.value = True
        if ( d.value == True ): readback += "1"
        else:                   readback += "0"
        e.value = False

    d.switch_to_output(value = False, drive_mode=digitalio.DriveMode.PUSH_PULL)
    e.value = True
    d.value = True
    e.switch_to_input(pull=None)
    d.switch_to_input(pull=None)

    return readback

###########

# Main program

print("\n\nTS4112 Configuration Example\n")

# Force the TS4112 into SLEEP mode regardless of the current state of the IC
force_reset()

# Write the config word to enable both Envelope & Data
write_config(config_word)
read_back = read_config()

if (read_back == config_word):
    print("Readback = WriteConfig")
else:
    print("Error: Did not readback correct configuration word")

while True:

    # While in state WATCH the D/E pins will respond to modulated light
    goto_watch()
    check_bus()
    sleep(1)

    # While in state SLEEP the TS4112 is in low power mode and the D/E
    # pins are both asserted high (logic 1) by the TS4112
    force_reset()
    check_bus()
    sleep(1)
