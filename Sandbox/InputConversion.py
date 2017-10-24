# 12 turn, max power 40.24 watts @ 7772 RPM

import math
import random
import struct
import sys
import threading
import time

# TODO: Get current GPS, speed, and heading for car

A_ORIGIN = [0, 0]  # ADJUSTABLE VARIABLES (GLOBAL)
A_ACCELERATION = 10  # m/s
A_UPDATE_INTERVAL = 0.5  # 2Hz refresh rate
A_TEST_ITERATIONS = 25
A_POSMAPBUFFERSIZE = 250
A_DIRCHANGEFACTOR = 0.0  # % chance of changing velocity input
A_MAXVELOCITY = 13.4  # m/s to mph

# Car Variables
cur_pos = A_ORIGIN
heading = 0.00  # degrees (True North)
angle = 0.00


def main():
    A = threading.Thread(target=run, args=("Drone A",))
    A.start()
    # B = threading.Thread(target=run, args=("Drone B",))
    # B.start()
    # C = threading.Thread(target=run, args=("Drone C",))
    # C.start()


def run(droneName):
    global cur_pos

    F_INIT = True  # FLAGS

    xPosStorage = []  # STORAGE LISTS
    yPosStorage = []

    counter = 0  # LOCAL VARIABLES

    # plt.axhline(0, color='red')  # Initial setup for plot
    # plt.axvline(0, color='red')
    # plt.ion()

    while True:
        xPosStorage.append(cur_pos[0])
        yPosStorage.append(cur_pos[1])

        if len(xPosStorage) > A_POSMAPBUFFERSIZE:  # Remove oldest data from buffer
            xPosStorage.pop(0)
            yPosStorage.pop(0)

        # plt.figure(1)
        # plt.plot(xPosStorage, yPosStorage, color='blue', linewidth=1.25)  # Map plot
        # plt.pause(A_UPDATE_INTERVAL)
        # plt.clf()
        # plt.draw()

        # TODO: Get output vector from simulation

        temp_pos = cur_pos

        if random.uniform(0, 1) < A_DIRCHANGEFACTOR or F_INIT is True:  # Simulate output vector from the simulator
            vector = genRandomVector()
            F_INIT = False
            updatePos(vector, True)
        else:
            updatePos(vector, False)

        while cur_pos[0] < 0.0 or cur_pos[1] < 0.0 or cur_pos[0] > 100 or cur_pos[1] > 64:
            print()
            cur_pos = temp_pos
            vector = genRandomVector()
            updatePos(vector, True)

        hexAngle = genSignal(angle)

        counter = counter + 1

        printf("%10d%10s%45s%45s%10.5f%12s%10.5f%10s\n", counter, droneName, vector.__str__(), cur_pos.__str__(), angle,
               hexAngle, heading, droneName)

        time.sleep(A_UPDATE_INTERVAL)


def genRandomVector():
    newVector = [random.uniform(-A_MAXVELOCITY, A_MAXVELOCITY), random.uniform(-A_MAXVELOCITY, A_MAXVELOCITY)]
    return newVector


def genTargetedVector():
    """Create vector that is pointing drone towards target"""


def updatePos(vector, flag):
    global cur_pos, angle, heading

    # TODO: Calculate current location in reference to new target location
    """Calculate new x and y coordinate based on last position"""
    xDelta = (vector[0] * A_UPDATE_INTERVAL) + ((1 / 2) * A_ACCELERATION * (A_UPDATE_INTERVAL ** 2))
    yDelta = (vector[1] * A_UPDATE_INTERVAL) + ((1 / 2) * A_ACCELERATION * (A_UPDATE_INTERVAL ** 2))

    cur_pos = [cur_pos[0] + xDelta, cur_pos[1] + yDelta]

    if flag:
        angle = math.atan(xDelta / yDelta)
        heading = (heading + angle) % 360
    else:
        angle = 0.00


def printf(format, *args):
    sys.stdout.write(format % args)


def getGPSCoords():
    """Poll and obtain data from GPS unit on vehicle"""


def genSignal(angleValue):
    """Craft signal based on new coordinates"""

    # TODO: Determine what signals are needed to direct car SERVO

    return float_to_hex(angleValue)

    # TODO: Determine what signals are needed to direct car ESC


def txSignal():
    """Poll and transmit across wifi something something darkside..."""

    # TODO: Transmit signals to car through WiFi


def float_to_hex(f):  # IEEE 32-bit standard for float representation
    return hex(struct.unpack('<I', struct.pack('<f', f))[0])


main()  # Invoke main()
