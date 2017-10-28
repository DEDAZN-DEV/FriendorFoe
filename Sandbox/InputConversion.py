# 12 turn, max power 40.24 watts @ 7772 RPM

import math
import random
import socket
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
A_DIRCHANGEFACTOR = 0.25  # % chance of changing velocity input
A_MAXVELOCITY = 13.4  # m/s

# UDP Settings
SERVER = "172.18.12.182"
PORT = 2222


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

    while True:
        xPosStorage.append(carData[0])
        yPosStorage.append(carData[1])

        if len(xPosStorage) > A_POSMAPBUFFERSIZE:  # Remove oldest data from buffer
            xPosStorage.pop(0)
            yPosStorage.pop(0)

        # TODO: Get output vector from simulation
        temp_data = carData[:]

        if random.uniform(0, 1) < A_DIRCHANGEFACTOR or F_INIT is True:  # Simulate output vector from the simulator
            vector = genRandomVector()
            F_INIT = False
            carData = updatePos(vector, True, temp_data)
        else:
            carData = updatePos(vector, False, temp_data)

        while carData[0] < 0.0 or carData[1] < 0.0 or carData[0] > 100.0 or carData[1] > 64.0:
            print(bcolors.WARNING + str(
                datetime.now()) + " [WARNING] " + droneName + ": Current heading will hit or exceed boundary edge! Recalculating..." + bcolors.ENDC)
            vector = genRandomVector()
            carData = updatePos(vector, True, temp_data)

        hexAngle = genSignal(carData[2])

        counter = counter + 1
        curTime = datetime.now()
        printf(bcolors.OKBLUE + "%10s [CONSOLE]%7.5d%10s%45s%15.10f%15.10f%12.5f%12s%11.5f%10s\n" + bcolors.ENDC,
               str(curTime), counter, droneName,
               vector.__str__(), carData[0], carData[1], carData[2],
               hexAngle, carData[3], droneName)

        socketTx(str(curTime) + "\t" + hexAngle)

        time.sleep(A_UPDATE_INTERVAL)


def genRandomVector():
    newVector = [random.uniform(-A_MAXVELOCITY, A_MAXVELOCITY), random.uniform(-A_MAXVELOCITY, A_MAXVELOCITY)]
    return newVector


def genTargetedVector():
    """Create vector that is pointing drone towards target"""


def updatePos(vector, flag, data):
    # TODO: Calculate current location in reference to new target location
    """Calculate new x and y coordinate based on last position"""
    xDelta = (vector[0] * A_UPDATE_INTERVAL) + ((1 / 2) * A_ACCELERATION * (A_UPDATE_INTERVAL ** 2))
    yDelta = (vector[1] * A_UPDATE_INTERVAL) + ((1 / 2) * A_ACCELERATION * (A_UPDATE_INTERVAL ** 2))

    newData = data[:]

    newData[0] = newData[0] + xDelta  # xpos
    newData[1] = newData[1] + yDelta  # ypos

    if flag:
        if yDelta >= 0:
            newData[2] = math.atan(xDelta / yDelta) * 180 / math.pi  # angle
        else:
            newData[2] = (math.atan(xDelta / yDelta) * 180 / math.pi) - 180
        if vector[1] >= 0:
            newData[3] = math.atan(vector[1] / vector[0]) * 180 / math.pi  # heading
        else:
            newData[3] = (math.atan(vector[1] / vector[0]) * 180 / math.pi) - 180
    else:
        newData[2] = 0.00

    if newData[2] < -180:
        newData[2] = newData[2] + 360
    elif newData[2] > 180:
        newData[2] = newData[2] - 360

    if newData[3] < 0:
        newData[3] = newData[3] + 360
    elif newData[3] > 360:
        newData[3] = newData[3] - 360

    return newData


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


def socketTx(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER, PORT))
    sock.sendall(data.encode())


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
