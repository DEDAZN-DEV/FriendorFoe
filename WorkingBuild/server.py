# 12 turn, max power 40.24 watts @ 7772 RPM

import multiprocessing
import random
import socket
import sys
import time

import matplotlib.pyplot as plt

import global_cfg as cfg
import gps_ops as gps
import vector_ops as vec


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
        print("Missing argument...\nUsage: python server.py [stop, normal_run, debug_circle [time in seconds], "
              "debug_random, debug_gps]")
        sys.exit()
    else:
        testtype = sys.argv[1]

    if testtype == 'normal_run':
        # a = multiprocessing.Process(target=run, args=('A', CLIENT_IP_A, cfg.PORT,))
        # a.start()
        print()
    elif testtype == 'debug_circle':
        if len(sys.argv) < 3:
            print("Missing argument...\nUsage: python server.py debug_circle [time in seconds]")
        else:
            length = int(sys.argv[2])
            a = multiprocessing.Process(target=force_circle, args=(cfg.CLIENT_IP_A, cfg.PORT, length,))
            a.start()
    elif testtype == 'debug_random':
        a = multiprocessing.Process(target=rand_run, args=(cfg.CLIENT_IP_A, cfg.PORT,))
        a.start()
    elif testtype == 'stop':
        a = multiprocessing.Process(target=stop, args=(cfg.CLIENT_IP_A, cfg.PORT,))
        a.start()
    elif testtype == 'debug_gps':
        gps.gps_debug()
    elif testtype == 'test_run':
        a = multiprocessing.Process(target=test_run, args=('A', cfg.CLIENT_IP_A, cfg.PORT,))
        a.start()
    else:
        print("Invalid argument...\nUsage: python server.py [stop, normal_run, debug_circle, debug_random]")
        sys.exit()


def stop(client_ip, port):
    """
    Emergency override of current operation for car.
    :param client_ip: IP of target client
    :param port: PORT of target client
    :return: Nothing
    """
    socket_tx('stop', client_ip, port)
    print('Stopping')


def force_circle(client_ip, port, length):
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


# def run(dronename, ip, port):
#     """
#     Definition wrapper to handle the drones in their individual threads
#     :param dronename:
#     :param ip:
#     :return:
#     """
#     xposstorage = []
#     yposstorage = []
#
#     f_init = True  # FLAGS
#
#     counter = 0  # LOCAL VARIABLES
#     cardata = [0.0, 0.0, 0.0, 0.0]
#
#     while True:
#         xposstorage.append(cardata[0])
#         yposstorage.append(cardata[1])
#
#         if len(xposstorage) > POSMAPBUFFERSIZE:  # Remove oldest data from buffer
#             xposstorage.pop(0)
#             yposstorage.pop(0)
#
#         temp_data = cardata[:]
#         vector = [0, 0]
#
#         # if random.uniform(0, 1) < vec.DIRCHANGEFACTOR or f_init is True:  # Simulate output vector from the simulator
#         #     vector = vec.gen_random_vector()
#         #     f_init = False
#         #     cardata = vec.update_pos(vector, True, temp_data)
#         # else:
#         #     cardata = vec.update_pos(vector, False, temp_data)
#
#
#         vector = vec.gen_targeted_vector(cardata, vector[0], vector[1])
#
#         while cardata[0] < 0.0 or cardata[1] < 0.0 or cardata[0] > gps.LENGTH_X or cardata[1] > gps.LENGTH_Y:
#             print(BColors.WARNING + str(
#                 datetime.now()) + " [WARNING] " + dronename +
#                   ": Current heading will hit or exceed boundary edge! Recalculating..." + BColors.ENDC)
#             # vector = vec.gen_random_vector()
#             vector = vec.gen_targeted_vector(cardata, vector[0], vector[1])
#             cardata = vec.update_pos(vector, temp_data)
#
#         # hexangle = gen_signal(cardata[2])
#
#         counter = counter + 1
#         curtime = datetime.now()
#         # printf(BColors.OKBLUE + "%10s [CONSOLE]%7.5d%10s%45s%15.10f%15.10f%12.5f%12s%11.5f%10s\n" + BColors.ENDC,
#                str(curtime), counter, dronename,
#                vector.__str__(), cardata[0], cardata[1], cardata[2],
#                hexangle, cardata[3], dronename)
#
#         # socket_tx(str(curtime) + "     " + hexangle, ip, cfg.PORT)
#
#         print(xposstorage, yposstorage)
#
#         # More plotting things
#         plt.ion()
#         plt.axis([0.0, 64.0, 0.0, 100.0])
#         plt.plot(xposstorage, yposstorage, 'k-')
#
#         time.sleep(vec.UPDATE_INTERVAL)


def test_run(dronename, ip, port):
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
    cardata = [0.0, 0.0, 0.0, 45.0, 0.0]
    stage = 1

    plt.ion()
    plt.axis([0.0, cfg.LENGTH_X, 0.0, cfg.LENGTH_Y])

    while True:
        xposstorage.append(cardata[0])
        yposstorage.append(cardata[1])

        if len(xposstorage) > cfg.POSMAPBUFFERSIZE:  # Remove oldest data from buffer
            xposstorage.pop(0)
            yposstorage.pop(0)

        # TODO: Get output vector from simulation
        temp_data = cardata[:]

        tgt = vec.new_pos(stage, cardata)  # dummy input from algorithm
        print(tgt)
        while tgt[0] < 0 or tgt[0] > cfg.LENGTH_X or tgt[1] < 0 or tgt[1] > cfg.LENGTH_Y:
            print("Outside of boundaries....Recalculating")
            tgt = vec.new_pos(stage, cardata)

        vector = vec.gen_targeted_vector(temp_data, tgt[0], tgt[1])

        cardata = vec.update_pos(vector, temp_data)

        print(vector)
        print(cardata)

        gen_signal(cardata[2], cardata[4])

        flag = False

        if abs(cardata[0] - 25) < 0.05 and abs(cardata[1] - 50) < 0.05 and flag is False:
            stage = stage + 1
            flag = True
        elif abs(cardata[0] - 50) < 0.1 and abs(cardata[1] - 35) < 0.1:
            socket_tx('stop', ip, port)
            break

        # More plotting things
        plt.plot(xposstorage, yposstorage, 'k-')
        plt.pause(cfg.UPDATE_INTERVAL)


def printf(layout, *args):
    """
    Quality of life improvement (Personal sanity).
    @param layout: Standard C layout for printf.
    @param args: Arguments for the placeholders in layout
    @return:
    """

    sys.stdout.write(layout % args)


def gen_signal(angle, speed):
    """
    Crafts a signal based on the input, IEEE floating point single-percision.
        @return: Returns a 32-byte value in hex format.
    """

    if angle < 0:
        # center is 6000
        ang = int(round(4000 + (abs(angle) * cfg.DEGPERPOINT)))
    else:
        ang = int(round(6000 + (angle * cfg.DEGPERPOINT)))

    spd = int(round(6000 + (speed * cfg.SPDSCALE)))

    print(str(5) + str(ang))
    print(str(3) + str(spd))

    socket_tx(str(5) + str(ang), cfg.CLIENT_IP_A, cfg.PORT)
    socket_tx(str(3) + str(spd), cfg.CLIENT_IP_A, cfg.PORT)


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
