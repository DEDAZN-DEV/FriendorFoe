# 12 turn, max power 40.24 watts @ 7772 RPM

import random
import sys
import threading
import time

# TODO: Get current GPS, speed, and heading for car

A_ORIGIN = [0, 0]  # ADJUSTABLE VARIABLES (GLOBAL)
A_ACCELERATION = 10  # m/s
A_UPDATE_INTERVAL = 0.5  # 2Hz refresh rate
A_TEST_ITERATIONS = 25
A_POSMAPBUFFERSIZE = 250
A_DIRCHANGEFACTOR = 0.75  # % chance of changing direction

cur_pos = A_ORIGIN


def main():
    A = threading.Thread(target=run, args=("Drone A",))
    A.start()
    B = threading.Thread(target=run, args=("Drone B",))
    B.start()
    C = threading.Thread(target=run, args=("Drone C",))
    C.start()


def run(droneName):
    F_INIT = True  # FLAGS

    xPosStorage = []  # STORAGE LISTS
    yPosStorage = []

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

        if random.uniform(0, 1) < A_DIRCHANGEFACTOR or F_INIT is True:  # Simulate output vector from the simulator
            vector = genRandomVector()
            F_INIT = False

        updatePos(vector)
        print(droneName, vector, cur_pos)

        time.sleep(A_UPDATE_INTERVAL)


def genRandomVector():
    newVector = [random.uniform(-13.4, 13.4), random.uniform(-13.4, 13.4)]
    return newVector


def updatePos(vector):
    global cur_pos

    # TODO: Calculate current location in reference to new target location
    """Calculate new x and y coordinate based on last position"""
    xDelta = (vector[0] * A_UPDATE_INTERVAL) + ((1 / 2) * A_ACCELERATION * (A_UPDATE_INTERVAL ** 2))
    yDelta = (vector[1] * A_UPDATE_INTERVAL) + ((1 / 2) * A_ACCELERATION * (A_UPDATE_INTERVAL ** 2))

    temp_pos = cur_pos
    cur_pos = [cur_pos[0] + xDelta, cur_pos[1] + yDelta]

    if cur_pos[0] < 0.0 or cur_pos[1] < 0.0:
        cur_pos = temp_pos
        updatePos(genRandomVector())
    else:
        return cur_pos


def printf(format, *args):
    sys.stdout.write(format % args)


def getGPSCoords():
    """Poll and obtain data from GPS unit on vehicle"""


def genSignal():
    """Craft signal based on new coordinates"""

    # TODO: Determine what signals are needed to direct car SERVO

    # TODO: Determine what signals are needed to direct car ESC


def txSignal():
    """Poll and transmit across wifi something something darkside..."""

    # TODO: Transmit signals to car through WiFi

main()  # Invoke main()
