'''

starts a time lapse camera and turntable carrying samples. The turntable is controlled by a
stepper motor. Provide with length of time the capture should run for (days) and
the length of time the resulting video should last (seconds). Also provide the angles on the turntable that
samples to be photographed are at.

'''
import os

import RPi.GPIO as GPIO
import time
import board
import neopixel
import subprocess
import argparse

parser = argparse.ArgumentParser(description="Start a time lapse camera")
parser.add_argument('--experiment_hours',help="length of time experiment will last", type=int)
parser.add_argument('--video_seconds', help="length of time in seconds video should last", type=int)
args = parser.parse_args()

NUM_FRAMES = (24 * args.video_seconds)
FRAME_INTERVAL = (args.experiment_hours * 3600) / NUM_FRAMES ##take one frame every FRAME_INTERVAL seconds
ANGLES = (0,180) #positions in degrees the subjects will be at on the turntable


## setup hardware
pixels = neopixel.NeoPixel(board.D18, 8) #connected to Pi at pin 18, has 8 LED's
TABLE_PIN=25


#p = GPIO.PWM(TABLE_PIN, 50)
#p.start(1)


def lamp_on(pixels):
    pixels.fill( (255, 255, 255))

def lamp_off(pixels):
    pixels.fill((0,0,0))


def get_dc_from_angle(angle, pulse_min=1, pulse_max=12):
    dc = (angle / 180) * (pulse_max - pulse_min) + pulse_min
    return dc


def wake_table(pin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TABLE_PIN, GPIO.OUT)
    p = GPIO.PWM(pin, 50)
    p.start(1)
    return p

def move_table(p, angle):
    dc = get_dc_from_angle(1)
    p.ChangeDutyCycle(dc)
    dc = get_dc_from_angle(angle)
    p.ChangeDutyCycle(dc)

def sleep_table(p):
    p.stop()


def get_picture(frame_id, angle):
    fname ="angle_" + str(angle) + str(frame_id).zfill(6) + ".jpg"
    cmd = "/usr/local/bin/libcamera-still -t 5000 --nopreview -o  {} --autofocus".format(fname)
    os.system(cmd)




try:
    print("waking table...")
    p = wake_table(TABLE_PIN)


    for f in range(NUM_FRAMES):

        print("lamp on...")
        lamp_on(pixels)
        for a in ANGLES:
            print("moving to" + str(a))
            move_table(p, a)
            print("getting picture")
            get_picture(f,a)
        print("lamp off...")
        lamp_off(pixels)
        print("waiting for " + str(FRAME_INTERVAL) + " seconds")
        time.sleep(FRAME_INTERVAL)

    print("sleeping table...")
    sleep_table(p)


except KeyboardInterrupt:
    pass
finally:
    p.stop()
    GPIO.cleanup()