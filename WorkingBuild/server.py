# 12 turn, max power 40.24 watts @ 7772 RPM

import dubins
import math
import multiprocessing
import random
import socket
import sys
import time

import global_cfg as cfg
import gps_ops as gps
import matplotlib.pyplot as plt
import pymysql as sql
import vector_ops as vec


class BColors:
    """
    Color class for stdout
    """

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


class CarData:
    """
    Data structure for drone metrics
    """

    XPOS = 0.0
    YPOS = 0.0
    HEADING = 0.0
    TURNANGLE = 0.0
    SPEED = 0.0
    DIST_TRAVELED = 0.0


def main():
    """
    Driver function for the entire program. Spawns sub-processes to control each drone and then terminates.
    :return: 0 on successful completion
    """

    proclst = []

    try:
        if len(sys.argv) < 2:
            print("Missing argument...\nUsage: python server.py [stop, run, debug_circle [time in seconds], "
                  "debug_random, debug_gps]")
            sys.exit()
        else:
            test_type = sys.argv[1]
        if test_type == 'run':
            droneId = random.randint(000, 999)
            print('Session ID: ' + str(droneId))
            proclst.append(
                multiprocessing.Process(target=run, args=('Drone ' + str(droneId), cfg.CLIENT_IP_A, cfg.PORT,)).start())
        # proclst.append(multiprocessing.Process(target=run, args=('Drone 2', cfg.CLIENT_IP_A, cfg.PORT,)).start())
        elif test_type == 'debug_circle':
            if len(sys.argv) < 3:
                print("Missing argument...\nUsage: python server.py debug_circle <time in seconds>")
            else:
                length = int(sys.argv[2])
                a = multiprocessing.Process(target=force_circle, args=(cfg.CLIENT_IP_A, cfg.PORT, length,))
                a.start()
                # subprocesses.append(a)
                a.join()
        elif test_type == 'debug_random':
            a = multiprocessing.Process(target=rand_run, args=(cfg.CLIENT_IP_A, cfg.PORT,))
            a.start()
            # subprocesses.append(a)
            a.join()
        elif test_type == 'stop':
            stop(cfg.CLIENT_IP_A, cfg.PORT)
        elif test_type == 'debug_gps':
            gps.gps_debug()
        elif test_type == 'test_run':
            a = multiprocessing.Process(target=test_run, args=None)
            a.start()
            # subprocesses.append(a)
            a.join()
        else:
            print(
                "Invalid argument...\nUsage: python server.py [stop, normal_run, debug_circle <time>, debug_random, "
                "test_run]")
            sys.exit()

    except KeyboardInterrupt:
        print('Early Termination...Killing alive processes')
        for i in range(0, len(proclst)):
            while proclst[i].isalive():
                proclst[i].terminate()
                print(str(proclst[i]) + '....Killed')

    return 0


def run(dronename, ip, port):
    """
    Default drone control algorithm. Uses input from ATE-3 Sim to control drones.
    :param dronename: String, name of drone
    :param ip: String, LAN IP address of drone
    :param port: LAN Port of drone to be controlled, not necessary but can be changed.
    :return: Nothing
    """
    cardata = CarData()

    # cardata.XPOS, cardata.YPOS = gps.get_coords()
    # velocity_vector = vec.call_sim()
    # [tgtx, tgty] = vec.calc_xy(velocity_vector[0], velocity_vector[1], cardata.XPOS, cardata.YPOS)

    plt.figure(num=1, figsize=(6, 8))
    plt.ion()

    xpos = []
    ypos = []

    q0 = (cardata.XPOS, cardata.YPOS, 0)
    qs = []

    init_flag = True
    old_heading = cardata.HEADING

    step_size = cfg.UPDATE_INTERVAL  # 2HZ refresh rate for turn calculation

    # for n in range(cfg.TEST_ITERATIONS):
    while True:
        if init_flag is True:
            q1 = (random.randint(10, cfg.LENGTH_X - 10), random.randint(10, cfg.LENGTH_Y) - 10, 0)
            # q1 = (tgtx, tgty, 0)
            init_flag = False
        else:
            q1 = (random.randint(10, cfg.LENGTH_X - 10), random.randint(10, cfg.LENGTH_Y - 10), cardata.HEADING)
        # q1 = (tgtx, tgty, 0)

        qs, _ = dubins.path_sample(q0, q1, cfg.TURNRADIUS, step_size)
        path_length = dubins.path_length(q0, q1, cfg.TURNRADIUS)

        for i in range(len(qs) - 1):

            prev_XPOS = cardata.XPOS
            prev_YPOS = cardata.YPOS

            cardata.XPOS = qs[i][0]
            cardata.YPOS = qs[i][1]

            dist_traveled = math.sqrt((cardata.XPOS - prev_XPOS) ** 2 + (cardata.YPOS - prev_YPOS) ** 2)
            cardata.DIST_TRAVELED = dist_traveled
            path_length = path_length - dist_traveled

            old_heading = cardata.HEADING

            cardata.TURNANGLE = math.degrees(qs[i][2]) - old_heading

            if cardata.TURNANGLE <= -180:
                cardata.TURNANGLE = cardata.TURNANGLE + 360
            elif cardata.TURNANGLE >= 180:
                cardata.TURNANGLE = cardata.TURNANGLE - 360

            cardata.HEADING = math.degrees(qs[i][2])

            # TODO: Insert speed modification function here
            # Speed Modification Stub
            if abs(cardata.TURNANGLE) < 1.0:
                cardata.SPEED = cfg.MAXVELOCITY
            else:
                cardata.SPEED = cfg.TURNSPEED  # <-- Relate this to the angle in which its turning, higher angle == slower speed

            pause_interval = dist_traveled / cardata.SPEED

            if pause_interval == 0:
                pause_interval = 1e-6  # <-- This is a starter to the program for the initial draw

            if len(xpos) > cfg.BUFFERSIZE:
                xpos.pop(0)
                ypos.pop(0)

            xpos.append(qs[i][0])
            ypos.append(qs[i][1])

            tgtxstorage = q1[0]
            tgtystorage = q1[1]

            dbinsert(cardata, dronename)

            plt.clf()
            plt.title(dronename)
            plt.axis([0.0, cfg.LENGTH_X, 0.0, cfg.LENGTH_Y])
            plt.plot(xpos, ypos, 'k-')
            plt.plot(tgtxstorage, tgtystorage, 'rx')
            plt.grid(True)

            plt.pause(pause_interval)  # <- TODO: Update this to reflect car speed (distance / current speed)?

        q0 = q1


def stop(client_ip, port):
    """
    Emergency override of current operation for car.
    :param client_ip: IP of target client
    :param port: PORT of target client
    :return: 0 on successful completion
    """

    socket_tx('stop', client_ip, port)
    print('Stopping')

    return 0


def force_circle(client_ip, port, length):
    """
    Forces the specified drone to run in a continuous circle for a designated period of time.
    :param client_ip: String, LAN IP of drone to be controlled
    :param port: String, LAN Port of drone to be controlled
    :param length: Int, Length of circle pattern in seconds
    :return: 0 on successful completion
    """

    socket_tx('start', client_ip, port)

    time.sleep(length)

    socket_tx('stop', client_ip, port)

    return 0


def rand_run(client_ip, port):
    """
    Creates 10 random STR inputs and then spools the ESC by increasing the pulse length by 50ms every 1s
    :param client_ip: IP of target client
    :param port: PORT of target client
    :return: 0 on successful completion
    """

    print('Controlling STR')

    for i in range(5):
        inval = random.randint(4000, 8000)
        print(inval)
        socket_tx(str(cfg.STEERING) + str(inval), client_ip, port)
        time.sleep(2)

    socket_tx('stop', client_ip, port)
    time.sleep(1)

    print('Controlling ESC')

    # Forward
    for x in range(6000, 8000, 50):
        print(x)
        socket_tx(str(cfg.ESC) + str(x), client_ip, port)
        time.sleep(1)

    socket_tx('stop', client_ip, port)

    return 0


def test_run():
    """
    Test algorithm for drone control and movement
    :return: 0 on successful completion
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

        gen_spd_signal(cardata.SPEED, cardata.TURNANGLE, cfg.CLIENT_IP_A)
        gen_turn_signal(cardata.TURNANGLE, cfg.CLIENT_IP_A)

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

    return 0


def printf(layout, *args):
    """
    Printf implementation from C using system calls
    :param layout: String, placeholders and general text.
    :param args: Variables to be inserted in above string.
    :return: 0 on successful completion
    """

    sys.stdout.write(layout % args)

    return 0


def gen_turn_signal(angle, client):
    """
    Generates turn signal for MSC and transmits to drone
    :param angle: Float, angle of turn for drone
    :param client: String, LAN IP for drone to be controlled
    :return: 0 on successful completion
    """

    if angle < 0:
        ang = int(round(cfg.CENTER + (abs(angle) * cfg.DEGPERPOINT)))
    else:
        ang = int(round(cfg.CENTER - (angle * cfg.DEGPERPOINT)))

    if ang > 8000:
        ang = cfg.MAX_LEFT
    elif ang < 4000:
        ang = cfg.MAX_RIGHT

    socket_tx(str(cfg.TURNING) + str(ang), client, cfg.PORT)

    return 0


def gen_spd_signal(speed, angle, client):
    """
    Generates speed signal for MSC and transmits to drone
    :param speed: Float, speed to be reached
    :param angle: Float, current angle of turn
    :param client: LAN IP address of drone
    :return: 0 on successful completion
    """

    if abs(angle - cfg.CENTER) > 0.5:
        spd = int(round((cfg.TEST_SPEED + (speed * cfg.SPDSCALE)) / (abs(angle) * cfg.TURNFACTOR)))
    else:
        spd = int(round(cfg.TEST_SPEED + (speed * cfg.SPDSCALE)))

    if spd > cfg.MAX_SPEED:
        spd = cfg.MAX_SPEED - cfg.SPDLIMITER  # <- FOR TESTING PURPOSES
    elif spd < cfg.TEST_SPEED:
        spd = cfg.TEST_SPEED

    socket_tx(str(cfg.SPEED) + str(speed), client, cfg.PORT)

    return 0


def socket_tx(data, client_ip, port):
    """
    Transmits specified data to drone through sockets
    :param data: String, data to be transmitted
    :param client_ip: LAN IP of drone
    :param port: Port of drone
    :return: 0 on successful completion
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

    return 0


def disable(self):
    """
    Class to disable color in stdout
    :param self: Self
    :return: 0 on successful completion
    """

    self.HEADER = ''
    self.OKBLUE = ''
    self.OKGREEN = ''
    self.WARNING = ''
    self.FAIL = ''
    self.ENDC = ''

    return 0


def dbinsert(data, dronename):
    """
    Craft SQL querry and insert data into database to store test results.
    :param data: Data to be inserted (CARDATA obj)
    :param dronename: String, name of drone
    :return: 0 on successful completion
    """

    db = sql.connect(host='localhost', user='FriendorFoe@localhost', passwd='password', db='DRONES')
    cursor = db.cursor()

    query = """INSERT INTO DRONES.POS(DRONENAME, XPOS, YPOS, SPEED, HEADING, TURN_ANGLE, DIST_TRAVELED) VALUES ("%s", %f, %f, %f, %f, %f, %f)"""

    try:
        cursor.execute(query % (
            dronename, data.XPOS, data.YPOS, data.SPEED, data.HEADING, data.TURNANGLE, data.DIST_TRAVELED))
        db.commit()
    except Exception as e1:
        db.rollback()
        print(e1)

    db.close()

    return 0


if __name__ == '__main__':
    main()
