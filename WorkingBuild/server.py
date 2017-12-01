# 12 turn, max power 40.24 watts @ 7772 RPM

import math
import multiprocessing
import random
import socket
import struct
import sys
import time
from datetime import datetime

import matplotlib.pyplot as plt

# Car variables
ACCELERATION = 10  # m/s
UPDATE_INTERVAL = 0.5  # 2Hz refresh rate
DIRCHANGEFACTOR = 01.25  # % chance of changing velocity input
MAXVELOCITY = 13.4  # m/s

# Plotting variables
TEST_ITERATIONS = 25
POSMAPBUFFERSIZE = 25

# Clientside IP addresses and ports for each RC car
CLIENT_IP_A = "10.33.28.231"  # <-- This is the internal IP on the machine running client.py (ipconfig/ifconfig)
PORT_NUMBER = 7777  # <-- DO NOT CHANGE

CLIENT_IP_B = "127.0.0.1"

CLIENT_IP_C = "127.0.0.1"


class BColors:
    """
    Wrapper class for console output coloring.
    """

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def main():
    """
    Definition of main to run the code. Testing...
    @return: Nothing
    """

    if len(sys.argv) < 2:
        print("Missing argument...\nUsage: python server.py [stop, normal_run, debug_circle, debug_random]")
        sys.exit()
    else:
        testtype = sys.argv[1]

    calc_originxy()
    set_xy_ratio()

    if testtype == 'normal_run':
        a = multiprocessing.Process(target=run, args=(CLIENT_IP_A, PORT_NUMBER,))
    elif testtype == 'debug_circle':
        length = int(sys.argv[2])
        a = multiprocessing.Process(target=test_run, args=(CLIENT_IP_A, PORT_NUMBER, length,))
    elif testtype == 'debug_random':
        a = multiprocessing.Process(target=rand_run, args=(CLIENT_IP_A, PORT_NUMBER,))
    elif testtype == 'stop':
        a = multiprocessing.Process(target=stop, args=(CLIENT_IP_A, PORT_NUMBER,))
    else:
        print("Invalid argument...\nUsage: python server.py [stop, normal_run, debug_circle, debug_random]")
        sys.exit()

    a.start()


def stop(client_ip, port):
    """
    Emergency override of current operation for car.
    :param client_ip: IP of target client
    :param port: PORT of target client
    :return: Nothing
    """
    socket_tx('stop', client_ip, port)
    print('Stopping')


def test_run(client_ip, port, length):
    """
    Circular test profile for MSC to ESC and STR servos
    :param client_ip: IP of target client
    :param port: PORT of target client
    :return: Nothing
    """
    socket_tx('start', client_ip, port)

    time.sleep(length)

    socket_tx('stop', client_ip, port)


def rand_run(client_ip, port):
    """
    Creates 10 random STR inputs and then spools the ESC by increasing the pulse length by 50ms every 1s
    :param client_ip: IP of target client
    :param port: PORT of target client
    :return: Nothing
    """
    print('Controlling STR')

    for i in range(10):
        inval = random.randint(4000, 8000)
        print(inval)
        socket_tx(str(5) + str(inval), client_ip, port)
        time.sleep(2)

    socket_tx('stop', client_ip, port)
    time.sleep(1)

    print('Controlling ESC')

    # Forward
    for x in range(6000, 8000, 50):
        print(x)
        socket_tx(str(3) + str(x), client_ip, port)
        time.sleep(1)

    socket_tx('stop', client_ip, port)


def run(dronename, ip):
    """
    Definition wrapper to handle the drones in their individual threads
    :param dronename:
    :param ip:
    :return:
    """
    xposstorage = []
    yposstorage = []

    f_init = True  # FLAGS

    counter = 0  # LOCAL VARIABLES
    cardata = [0.0, 0.0, 0.0, 0.0]

    while True:
        xposstorage.append(cardata[0])
        yposstorage.append(cardata[1])

        if len(xposstorage) > POSMAPBUFFERSIZE:  # Remove oldest data from buffer
            xposstorage.pop(0)
            yposstorage.pop(0)

        # TODO: Get output vector from simulation
        temp_data = cardata[:]

        if random.uniform(0, 1) < DIRCHANGEFACTOR or f_init is True:  # Simulate output vector from the simulator
            vector = gen_random_vector()
            f_init = False
            cardata = update_pos(vector, True, temp_data)
        else:
            cardata = update_pos(vector, False, temp_data)

        while cardata[0] < 0.0 or cardata[1] < 0.0 or cardata[0] > 100.0 or cardata[1] > 64.0:
            print(BColors.WARNING + str(
                datetime.now()) + " [WARNING] " + dronename +
                  ": Current heading will hit or exceed boundary edge! Recalculating..." + BColors.ENDC)
            vector = gen_random_vector()
            cardata = update_pos(vector, True, temp_data)

        hexangle = gen_signal(cardata[2])

        # counter = counter + 1
        # curtime = datetime.now()
        # printf(BColors.OKBLUE + "%10s [CONSOLE]%7.5d%10s%45s%15.10f%15.10f%12.5f%12s%11.5f%10s\n" + BColors.ENDC,
        #        str(curtime), counter, dronename,
        #        vector.__str__(), cardata[0], cardata[1], cardata[2],
        #        hexangle, cardata[3], dronename)
        #
        # socket_tx(str(curtime) + "     " + hexangle, ip, PORT_NUMBER)

        print(xposstorage, yposstorage)

        # More plotting things
        plt.ion()
        plt.axis([0.0, 64.0, 0.0, 100.0])
        plt.plot(xposstorage, yposstorage, 'k-')

        time.sleep(UPDATE_INTERVAL)


def gen_random_vector():
    """
    Creates a random velocity vector bounded by the max velocity of the RC car.
    @return: Returns a two element vector consisting of the x and y component of a velocity.
    """

    newvector = [random.uniform(-MAXVELOCITY, MAXVELOCITY), random.uniform(-MAXVELOCITY, MAXVELOCITY)]
    return newvector


def gen_targeted_vector():
    """
    Creates a targeted vector towards a specific position.
    @return: Returns a two element vector consisiting of the x and y component of a velocity.
    """


def update_pos(vector, flag, data):
    """
    Updates the current position of the drone as well as the heading and turn angle.
    @param vector: The velocity vector (xv, yv).
    @param flag: Whether or not to update the heading and turn angle.
    @param data: Temp storage for the car data; 4 elements (xpos, ypos, angle, heading)
    @return: Returns the updated cardata.
    """

    xdelta = (vector[0] * UPDATE_INTERVAL) + ((1 / 2) * ACCELERATION * (UPDATE_INTERVAL ** 2))
    ydelta = (vector[1] * UPDATE_INTERVAL) + ((1 / 2) * ACCELERATION * (UPDATE_INTERVAL ** 2))

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
    Quality of life improvement (Personal sanity).
    @param layout: Standard C layout for printf.
    @param args: Arguments for the placeholders in layout
    @return:
    """

    sys.stdout.write(layout % args)


def gen_signal(anglevalue):
    """
    Crafts a signal based on the input, IEEE floating point single-percision.
    @param anglevalue: The float value to be converted
    @return: Returns a 32-byte value in hex format.
    """

    # TODO: Determine what signals are needed to direct car SERVO

    return float_to_hex(anglevalue)

    # TODO: Determine what signals are needed to direct car ESC


def float_to_hex(f):  # IEEE 32-bit standard for float representation
    """
    Converts float value to hex value.
    @param f: Float value.
    @return: The hex value of the target float.
    """

    return hex(struct.unpack('<I', struct.pack('<f', f))[0])


def socket_tx(data, client_ip, port):
    """
    Transmits data over a socket
    :param data:
    :param client_ip:
    :param port:
    :return:
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((client_ip, port))
        sock.sendall(data.encode())
        print(BColors.OKGREEN + "Data Sent Successfully..." + BColors.ENDC)
    except socket.herror:
        print(BColors.FAIL + "Connection refused...." + BColors.ENDC)
    except socket.timeout:
        print(BColors.FAIL + "Connection timed out...." + BColors.ENDC)


def disable(self):
    """
    Terminating color for console output.
    @param self: Reference to itself.
    @return: Nothing
    """

    self.HEADER = ''
    self.OKBLUE = ''
    self.OKGREEN = ''
    self.WARNING = ''
    self.FAIL = ''
    self.ENDC = ''


main()  # Invoke main()
