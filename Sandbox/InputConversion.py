# 12 turn, max power 40.24 watts @ 7772 RPM

import math
import random
import struct
import sys
import threading
import time

from datetime import datetime

# TODO: Get current GPS, speed, and heading for car

A_ORIGIN = [0, 0]  # ADJUSTABLE VARIABLES (GLOBAL)
A_ACCELERATION = 10  # m/s
A_UPDATE_INTERVAL = 0.5  # 2Hz refresh rate
A_TEST_ITERATIONS = 25
A_POSMAPBUFFERSIZE = 250
A_DIRCHANGEFACTOR = 0.1  # % chance of changing velocity input
A_MAXVELOCITY = 10  # m/s


def main():
    A = threading.Thread(target=run, args=("Drone A",))
    A.start()
    # B = threading.Thread(target=run, args=("Drone B",))
    # B.start()
    # C = threading.Thread(target=run, args=("Drone C",))
    # C.start()


def run(droneName):
    F_INIT = True  # FLAGS

    xPosStorage = []  # STORAGE LISTS
    yPosStorage = []

    counter = 0  # LOCAL VARIABLES
    carData = [0.0, 0.0, 0.0, 0.0]

    # plt.axhline(0, color='red')  # Initial setup for plot
    # plt.axvline(0, color='red')
    # plt.ion()

    while True:
        xPosStorage.append(carData[0])
        yPosStorage.append(carData[1])

        if len(xPosStorage) > A_POSMAPBUFFERSIZE:  # Remove oldest data from buffer
            xPosStorage.pop(0)
            yPosStorage.pop(0)

        # plt.figure(1)
        # plt.plot(xPosStorage, yPosStorage, color='blue', linewidth=1.25)  # Map plot
        # plt.pause(A_UPDATE_INTERVAL)
        # plt.clf()
        # plt.draw()

        # TODO: Get output vector from simulation

        temp_xpos = carData[0]
        temp_ypos = carData[1]

        if random.uniform(0, 1) < A_DIRCHANGEFACTOR or F_INIT is True:  # Simulate output vector from the simulator
            vector = genRandomVector()
            F_INIT = False
            carData = updatePos(vector, True, carData)
        else:
            carData = updatePos(vector, False, carData)

        while carData[0] < 0.0 or carData[1] < 0.0 or carData[1] > 100 or carData[0] > 64:
            print(bcolors.WARNING + str(
                datetime.now()) + " [WARNING] " + droneName + ": Current heading will hit or exceed boundary edge! Recalculating..." + bcolors.ENDC)
            carData[0] = temp_xpos
            carData[1] = temp_ypos
            vector = genRandomVector()
            carData = updatePos(vector, True, carData)

        hexAngle = genSignal(carData[2])

        counter = counter + 1

        printf(bcolors.OKBLUE + "%10s [CONSOLE]%7.5d%10s%43s%15.10f%15.10f%10.5f%12s%10.5f%10s\n" + bcolors.ENDC,
               str(datetime.now()), counter, droneName,
               vector.__str__(), carData[0], carData[1], carData[2],
               hexAngle, carData[3], droneName)

        time.sleep(A_UPDATE_INTERVAL)


def genRandomVector():
    newVector = [random.uniform(-A_MAXVELOCITY, A_MAXVELOCITY), random.uniform(-A_MAXVELOCITY, A_MAXVELOCITY)]
    return newVector


def genTargetedVector():
    """Create vector that is pointing drone towards target"""


def updatePos(vector, flag, carData):
    global A_ORIGIN

    # Car Variables
    cur_xpos = A_ORIGIN[0]
    cur_ypos = A_ORIGIN[1]

    # TODO: Calculate current location in reference to new target location
    """Calculate new x and y coordinate based on last position"""
    xDelta = (vector[0] * A_UPDATE_INTERVAL) + ((1 / 2) * A_ACCELERATION * (A_UPDATE_INTERVAL ** 2))
    yDelta = (vector[1] * A_UPDATE_INTERVAL) + ((1 / 2) * A_ACCELERATION * (A_UPDATE_INTERVAL ** 2))

    carData[0] = carData[0] + xDelta
    carData[1] = carData[1] + yDelta

    if flag:
        carData[2] = math.atan(xDelta / yDelta)
        carData[3] = carData[3] + carData[2]

        if carData[3] < 0:
            carData[3] = carData[3] + 360
        elif carData[3] > 360:
            carData[3] = carData[3] - 360

    else:
        carData[2] = 0.00

    return carData


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


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def disable(self):
    self.HEADER = ''
    self.OKBLUE = ''
    self.OKGREEN = ''
    self.WARNING = ''
    self.FAIL = ''
    self.ENDC = ''


main()  # Invoke main()
