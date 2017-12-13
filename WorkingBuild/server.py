# 12 turn, max power 40.24 watts @ 7772 RPM

import dubins
import multiprocessing
import random
import socket
import sys
import time

import matplotlib.pyplot as plt

from WorkingBuild import global_cfg as cfg
from WorkingBuild import gps_ops as gps
from WorkingBuild import vector_ops as vec


class BColors:
    """

    """

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


class CarData:
    """

    """

    XPOS = 0.0
    YPOS = 0.0
    HEADING = 0.0
    TURNANGLE = 0.0
    SPEED = 0.0


def main():
    """

    :return:
    """

    if len(sys.argv) < 2:
        print("Missing argument...\nUsage: python server.py [stop, normal_run, debug_circle [time in seconds], "
              "debug_random, debug_gps]")
        sys.exit()
    else:
        test_type = sys.argv[1]

    if test_type == 'run':
        a = multiprocessing.Process(target=run, args=("DRONE A", cfg.CLIENT_IP_A, cfg.PORT,))
        a.start()

    elif test_type == 'debug_circle':
        if len(sys.argv) < 3:
            print("Missing argument...\nUsage: python server.py debug_circle <time in seconds>")
        else:
            length = int(sys.argv[2])
            a = multiprocessing.Process(target=force_circle, args=(cfg.CLIENT_IP_A, cfg.PORT, length,))
            a.start()

    elif test_type == 'debug_random':
        a = multiprocessing.Process(target=rand_run, args=(cfg.CLIENT_IP_A, cfg.PORT,))
        a.start()

    elif test_type == 'stop':
        stop(cfg.CLIENT_IP_A, cfg.PORT)

    elif test_type == 'debug_gps':
        gps.gps_debug()

    elif test_type == 'test_run':
        a = multiprocessing.Process(target=test_run, args=None)
        a.start()

    else:
        print(
            "Invalid argument...\nUsage: python server.py [stop, normal_run, debug_circle <time>, debug_random, "
            "test_run]")
        sys.exit()


def run(dronename, ip, port):
    """

    :param dronename:
    :param ip:
    :param port:
    :return:
    """

    # TODO
    cardata = CarData()

    # cardata.XPOS, cardata.YPOS = gps.get_coords()
    # velocity_vector = vec.sim_api()

    q0 = (cardata.XPOS, cardata.YPOS, cardata.HEADING)
    q1 = (cfg.LENGTH_X / 2.0, cfg.LENGTH_Y / 2.0, cardata.HEADING)
    turning_radius = 1.0
    step_size = 0.5

    qs, _ = dubins.path_sample(q0, q1, turning_radius, step_size)

    print(qs)


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

    :param client_ip:
    :param port:
    :param length:
    :return:
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

    for i in range(5):
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


def test_run():
    """

    :return:
    """

    xposstorage = []
    yposstorage = []

    cardata = [0.0, 0.0, 0.0, 45.0, 0.0]
    stage = 1

    plt.ion()
    plt.axis([0.0, cfg.LENGTH_X, 0.0, cfg.LENGTH_Y])

    time.sleep(5)

    while True:
        xposstorage.append(cardata[0])
        yposstorage.append(cardata[1])

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

        if abs(cardata[0] - 30) < 0.5 and abs(cardata[1] - 20) < 0.5 and stage < 3:
            stage = stage + 1
        elif abs(cardata[0] - 40) < 0.5 and abs(cardata[1] - 40) < 0.5 and stage < 3:
            stage = stage + 1
        elif abs(cardata[0] - 75) < 0.5 and abs(cardata[1] - 110) < 0.5:
            socket_tx('stop', cfg.CLIENT_IP_A, cfg.PORT)
            time.sleep(30)
            break
        elif stage >= 3:  # abs(cardata[0] - 50) < 0.5 and abs(cardata[1] - 65) < 0.5:
            stage = stage + 1
            # elif abs(cardata[0] - 45) < 0.5 and abs(cardata[1] - 90) < 0.5:
            # stage = stage + 1

        print("Stage: " + str(stage) + '\n---------------------------------------------------------')

        # More plotting things
        plt.plot(xposstorage, yposstorage, 'k-')
        plt.pause(cfg.UPDATE_INTERVAL)


def printf(layout, *args):
    """

    :param layout:
    :param args:
    :return:
    """

    sys.stdout.write(layout % args)


def gen_signal(angle, speed):
    """

    :param angle:
    :param speed:
    :return:
    """

    if angle < 0:
        ang = int(round(cfg.CENTER + (abs(angle) * cfg.DEGPERPOINT)))
    else:
        ang = int(round(cfg.CENTER + (angle * cfg.DEGPERPOINT)))

    if ang > 8000:
        ang = cfg.MAX_LEFT
    elif ang < 4000:
        ang = cfg.MAX_RIGHT

    if abs(ang - cfg.CENTER) > 0.5:
        spd = int(round((cfg.TEST_SPEED + (speed * cfg.SPDSCALE)) / (abs(angle) * cfg.TURNFACTOR)))
    else:
        spd = int(round(cfg.TEST_SPEED + (speed * cfg.SPDSCALE)))

    if spd > cfg.MAX_SPEED:
        spd = cfg.MAX_SPEED - cfg.SPDLIMITER  # <- FOR TESTING
    elif spd < cfg.TEST_SPEED:
        spd = cfg.TEST_SPEED

    print(str(5) + str(ang))
    print(str(3) + str(spd))

    socket_tx(str(5) + str(ang), cfg.CLIENT_IP_A, cfg.PORT)
    if ang != cfg.CENTER:
        print('*** Turn Delay *** - ' + str(abs(angle / cfg.TURNDELAY)))
        time.sleep(abs(angle / 30))
        socket_tx(str(5) + str(cfg.CENTER), cfg.CLIENT_IP_A, cfg.PORT)
        time.sleep(0.1)
        # I changed this \/ from spd
        socket_tx(str(3) + str(spd), cfg.CLIENT_IP_A, cfg.PORT)


def socket_tx(data, client_ip, port):
    """

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

    :param self:
    :return:
    """

    self.HEADER = ''
    self.OKBLUE = ''
    self.OKGREEN = ''
    self.WARNING = ''
    self.FAIL = ''
    self.ENDC = ''


if __name__ == '__main__':
    main()  # Invoke main()
