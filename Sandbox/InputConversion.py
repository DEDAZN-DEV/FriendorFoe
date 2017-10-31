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
A_SERVER_IP = "192.168.0.103"
A_SERVER_PORT = 7777


def main():
    """

    @return:
    """

    a = threading.Thread(target=run, args=("Drone A",))
    a.start()
    # b = threading.Thread(target=run, args=("Drone B",))
    # b.start()
    # c = threading.Thread(target=run, args=("Drone C",))
    # c.start()


def run(dronename):
    """

    @param dronename:
    @return:
    """

    f_init = True  # FLAGS

    xpossstorage = []  # STORAGE LISTS
    yposstorage = []

    counter = 0  # LOCAL VARIABLES
    cardata = [0.0, 0.0, 0.0, 0.0]

    while True:
        xpossstorage.append(cardata[0])
        yposstorage.append(cardata[1])

        if len(xpossstorage) > A_POSMAPBUFFERSIZE:  # Remove oldest data from buffer
            xpossstorage.pop(0)
            yposstorage.pop(0)

        # TODO: Get output vector from simulation
        temp_data = cardata[:]

        if random.uniform(0, 1) < A_DIRCHANGEFACTOR or f_init is True:  # Simulate output vector from the simulator
            vector = genrandomvector()
            f_init = False
            cardata = updatepos(vector, True, temp_data)
        else:
            cardata = updatepos(vector, False, temp_data)

        while cardata[0] < 0.0 or cardata[1] < 0.0 or cardata[0] > 100.0 or cardata[1] > 64.0:
            print(BColors.WARNING + str(
                datetime.now()) + " [WARNING] " + dronename +
                  ": Current heading will hit or exceed boundary edge! Recalculating..." + BColors.ENDC)
            vector = genrandomvector()
            cardata = updatepos(vector, True, temp_data)

        hexangle = gensignal(cardata[2])

        counter = counter + 1
        curtime = datetime.now()
        printf(BColors.OKBLUE + "%10s [CONSOLE]%7.5d%10s%45s%15.10f%15.10f%12.5f%12s%11.5f%10s\n" + BColors.ENDC,
               str(curtime), counter, dronename,
               vector.__str__(), cardata[0], cardata[1], cardata[2],
               hexangle, cardata[3], dronename)

        sockettx(str(curtime) + "     " + hexangle, A_SERVER_IP, A_SERVER_PORT)

        time.sleep(A_UPDATE_INTERVAL)


def genrandomvector():
    """

    @return:
    """

    newvector = [random.uniform(-A_MAXVELOCITY, A_MAXVELOCITY), random.uniform(-A_MAXVELOCITY, A_MAXVELOCITY)]
    return newvector


def gentargetedvector():
    """

    @return:
    """


def updatepos(vector, flag, data):
    # TODO: Calculate current location in reference to new target location
    """

    @param vector:
    @param flag:
    @param data:
    @return:
    """

    xdelta = (vector[0] * A_UPDATE_INTERVAL) + ((1 / 2) * A_ACCELERATION * (A_UPDATE_INTERVAL ** 2))
    ydelta = (vector[1] * A_UPDATE_INTERVAL) + ((1 / 2) * A_ACCELERATION * (A_UPDATE_INTERVAL ** 2))

    newdata = data[:]

    newdata[0] = newdata[0] + xdelta  # xpos
    newdata[1] = newdata[1] + ydelta  # ypos

    if flag:
        if ydelta >= 0:
            newdata[2] = math.atan(xdelta / ydelta) * 180 / math.pi  # angle
        else:
            newdata[2] = (math.atan(xdelta / ydelta) * 180 / math.pi) - 180
        if vector[1] >= 0:
            newdata[3] = math.atan(vector[1] / vector[0]) * 180 / math.pi  # heading
        else:
            newdata[3] = (math.atan(vector[1] / vector[0]) * 180 / math.pi) - 180
    else:
        newdata[2] = 0.00

    if newdata[2] < -180:
        newdata[2] = newdata[2] + 360
    elif newdata[2] > 180:
        newdata[2] = newdata[2] - 360

    if newdata[3] < 0:
        newdata[3] = newdata[3] + 360
    elif newdata[3] > 360:
        newdata[3] = newdata[3] - 360

    return newdata


def printf(layout, *args):
    """

    @param layout:
    @param args:
    @return:
    """

    sys.stdout.write(layout % args)


def getgpscoords():
    """

    @return:
    """


def gensignal(anglevalue):
    """

    @param anglevalue:
    @return:
    """

    # TODO: Determine what signals are needed to direct car SERVO

    return float_to_hex(anglevalue)

    # TODO: Determine what signals are needed to direct car ESC


def txsignal():
    """

    @return:
    """

    # TODO: Transmit signals to car through WiFi


def float_to_hex(f):  # IEEE 32-bit standard for float representation
    """

    @param f:
    @return:
    """

    return hex(struct.unpack('<I', struct.pack('<f', f))[0])


def sockettx(data, server, port):
    """

    @param data:
    @param server:
    @param port:
    @return:
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((server, port))
        sock.sendall(data.encode())
        print(BColors.OKGREEN + "Data Sent Successfully..." + BColors.ENDC)
    except ConnectionRefusedError:
        print(BColors.FAIL + "Connection refused...." + BColors.ENDC)
    except TimeoutError:
        print(BColors.FAIL + "Connection timed out...." + BColors.ENDC)


class BColors:
    """

    """

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def disable(self):
    """

    @param self:
    @return:
    """

    self.HEADER = ''
    self.OKBLUE = ''
    self.OKGREEN = ''
    self.WARNING = ''
    self.FAIL = ''
    self.ENDC = ''


main()  # Invoke main()
