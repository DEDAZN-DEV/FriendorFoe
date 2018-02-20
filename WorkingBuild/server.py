# 12 turn, max power 40.24 watts @ 7772 RPM

import dubins
import math
import random
import socket
import sys
from multiprocessing import Process, freeze_support

import matplotlib.pyplot as plt
import pymysql as sql

import global_cfg as cfg
import gps_ops as gps
import vector_ops as vec

BUFFERSIZE = 50


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

    def __init__(self):
        self.LAT = 0.0
        self.LONG = 0.0
        self.XPOS = 0.0
        self.YPOS = 0.0
        self.HEADING = 0.0
        self.TURNANGLE = 0.0
        self.SPEED = 0.0
        self.DIST_TRAVELED = 0.0


class Drone:
    """
    """

    def __init__(self, func, ip, port, droneid):
        self.name = droneid
        self.process = Process(target=func, args=('Drone ' + str(droneid), ip, port))
        print('Drone ID: ' + str(self.name))


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

                a = Drone(run, cfg.CLIENT_IP_A, cfg.PORT, random.randint(0, 999))
                proclst.append(a)
                a.process.start()
                a.process.join()

            elif test_type == 'debug_gps':

                gps.gps_debug()

            else:
                print(
                    "Invalid argument...\nUsage: python server.py [stop, run]")
                sys.exit()

    except KeyboardInterrupt:

        print('Keyboard Interrupt....Killing live processes')

        for i in range(0, len(proclst)):

            if proclst[i].process.is_alive():
                print('Killing Drone ID: ' + str(proclst[i].name))
                proclst[i].process.terminate()

        print('....Done\n')


def run(dronename, ip, port):
    """
    Default drone control algorithm. Uses input from ATE-3 Sim to control drones.
    :param dronename: String, name of drone
    :param ip: String, LAN IP address of drone
    :param port: LAN Port of drone to be controlled, not necessary but can be changed.
    :return: Nothing
    """
    init = True
    cardata = CarData()

    plt.figure(num=1, figsize=(6, 8))
    plt.ion()

    xpos = []
    ypos = []

    gps.calc_originxy()
    gps.set_xy_ratio()

    # IP Initialization
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    # End IP Stuff

    # GPS Initialization
    socket_tx('gps', sock)
    message = socket_rx(sock)

    print(message)

    try:
        cardata.XPOS = gps.parse_gps_msg(str(message.decode()))[0]
        cardata.YPOS = gps.parse_gps_msg(str(message.decode()))[1]
    except TypeError:
        print('Invalid GPS Message...Exiting')
        socket_tx('stop', sock)
        sys.exit()
    print(cardata.XPOS, cardata.YPOS)
    # END GPS

    q0 = (cardata.XPOS, cardata.YPOS, 0)

    step_size = cfg.UPDATE_INTERVAL  # 2HZ refresh rate for turn calculation

    while True:
        # GPS
        socket_tx('gps', sock)
        message = socket_rx(sock)

        try:
            cardata.XPOS = gps.parse_gps_msg(str(message.decode()))[0]
            cardata.YPOS = gps.parse_gps_msg(str(message.decode()))[1]
        except TypeError:
            print('Invalid GPS Message...Exiting')
            socket_tx('stop', sock)
            sys.exit()
        # END GPS

        seed1 = random.random()

        if seed1 <= cfg.DIRCHANGEFACTOR or init:
            init = False
            velocity_vector = vec.call_sim()

        [tgtx, tgty] = vec.calc_xy(velocity_vector[0], velocity_vector[1], cardata.XPOS, cardata.YPOS,
                                   cardata.HEADING)

        while tgtx < cfg.TURNDIAMETER or tgtx > cfg.LENGTH_X - cfg.TURNDIAMETER or tgty < cfg.TURNDIAMETER or tgty > cfg.LENGTH_Y - cfg.TURNDIAMETER:
            velocity_vector = vec.call_sim()
            [tgtx, tgty] = vec.calc_xy(velocity_vector[0], velocity_vector[1], cardata.XPOS, cardata.YPOS,
                                       cardata.HEADING)

        ##########################################################################
        desired_heading = math.atan2((tgty - cardata.YPOS), (tgtx - cardata.XPOS))
        print('Last Angle Orientation: ', math.degrees(desired_heading))

        if abs(math.degrees(desired_heading)) >= cfg.MAX_TURN_RADIUS:
            print('Code For Dampened Turn Here')
        else:
            q1 = (tgtx, tgty, desired_heading)  # maintain original heading to target
            ##########################################################################

            qs, _ = dubins.path_sample(q0, q1, cfg.TURNDIAMETER, step_size)
            path_length = dubins.path_length(q0, q1, cfg.TURNDIAMETER)

            interval_time = 0.0

            for i in range(0, len(qs) - 1):

                prev_xpos = cardata.XPOS
                prev_ypos = cardata.YPOS

                cardata.XPOS = qs[i][0]
                cardata.YPOS = qs[i][1]

                # GPS
                socket_tx('gps', sock)
                message = socket_rx(sock)

                try:
                    cardata.XPOS = gps.parse_gps_msg(str(message.decode()))[0]
                    cardata.YPOS = gps.parse_gps_msg(str(message.decode()))[1]
                except TypeError:
                    print('Invalid GPS Message...Exiting')
                    socket_tx('stop', sock)
                    sys.exit()
                # END GPS

                dist_traveled = math.sqrt((cardata.XPOS - prev_xpos) ** 2 + (cardata.YPOS - prev_ypos) ** 2)
                cardata.DIST_TRAVELED = dist_traveled
                path_length = path_length - dist_traveled

                old_heading = cardata.HEADING

                cardata.TURNANGLE = math.degrees(qs[i][2]) - old_heading

                if cardata.TURNANGLE <= -180:
                    cardata.TURNANGLE = cardata.TURNANGLE + 360
                elif cardata.TURNANGLE >= 180:
                    cardata.TURNANGLE = cardata.TURNANGLE - 360

                cardata.HEADING = math.degrees(qs[i][2])

                if abs(cardata.TURNANGLE) < 1.0:
                    cardata.SPEED = math.sqrt(velocity_vector[0] ** 2 + velocity_vector[1] ** 2)
                else:
                    cardata.SPEED = 5
                    # ^ Relate this to the angle in which its turning, higher angle == slower speed

                ################################################################
                gen_turn_signal(cardata.TURNANGLE, sock)

                gen_spd_signal(cardata.SPEED, cardata.TURNANGLE, sock)
                ################################################################

                pause_interval = dist_traveled / cardata.SPEED

                if pause_interval == 0:
                    pause_interval = 1e-6  # <-- This is a starter to the program for the initial draw

                if len(xpos) > BUFFERSIZE:
                    xpos.pop(0)
                    ypos.pop(0)

                xpos.append(cardata.XPOS)
                ypos.append(cardata.YPOS)

                plt.clf()
                plt.title(dronename)
                plt.axis([0.0, cfg.LENGTH_X, 0.0, cfg.LENGTH_Y])
                plt.plot(xpos, ypos, 'k-')
                plt.plot(tgtx, tgty, 'rx')
                plt.grid(True)

                interval_time = interval_time + pause_interval

                # print('Recieved Vel Vector: ', velocity_vector)
                # print('Calculated Tgt Pos: ', tgtx, tgty)
                # print('Received Lat, Long: ', cardata.LAT, cardata.LONG)
                # print('Calculated XY Pos: ', cardata.XPOS, cardata.YPOS)
                # print('Interval Time: ', interval_time)
                # print('')

                # dbinsert(cardata, dronename)

                plt.pause(pause_interval)

            q0 = q1


def printf(layout, *args):
    """
    Printf implementation from C using system calls
    :param layout: String, placeholders and general text.
    :param args: Variables to be inserted in above string.
    :return: 0 on successful completion
    """

    sys.stdout.write(layout % args)


def gen_turn_signal(angle, sock):
    """
    Generates turn signal for MSC and transmits to drone
    :param angle: Float, angle of turn for drone
    :param sock:
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

    socket_tx(str(cfg.STEERING) + str(ang), sock)


def gen_spd_signal(speed, angle, sock):
    """
    Generates speed signal for MSC and transmits to drone
    :param speed: Float, speed to be reached
    :param angle: Float, current angle of turn
    :param sock:
    :return: 0 on successful completion
    """

    if abs(angle) > 1.0:
        spd = int(round((cfg.TEST_SPEED + (speed * cfg.SPDSCALE)) / (abs(angle) * cfg.TURNFACTOR)))
    else:
        spd = int(round(cfg.TEST_SPEED + (speed * cfg.SPDSCALE)))

    if spd > cfg.MAX_SPEED:
        spd = cfg.MAX_SPEED - cfg.SPDLIMITER  # <- FOR TESTING PURPOSES
    elif spd < cfg.TEST_SPEED:
        spd = cfg.TEST_SPEED

    socket_tx(str(cfg.ESC) + str(spd), sock)


def socket_tx(data, sock):
    """
    Transmits specified data to drone through sockets
    :param data: String, data to be transmitted
    :param sock:
    :return: 0 on successful completion
    """

    try:
        sock.sendall(data.encode())
        print(data)
        print(BColors.OKGREEN + "Data Sent Successfully..." + BColors.ENDC)
    except socket.herror:
        print(BColors.FAIL + "Connection refused...." + BColors.ENDC)
    except socket.timeout:
        print(BColors.FAIL + "Connection timed out...." + BColors.ENDC)


def socket_rx(sock):
    try:
        message = sock.recv(64)
        print(BColors.OKGREEN + "Data Received Successfully..." + BColors.ENDC)
        return message
    except socket.herror:
        print(BColors.FAIL + "Connection refused...." + BColors.ENDC)
    except socket.timeout:
        print(BColors.FAIL + "Connection timed out...." + BColors.ENDC)


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


def dbinsert(data, dronename):
    """
    Craft SQL querry and insert data into database to store test results.
    :param data: Data to be inserted (CARDATA obj)
    :param dronename: String, name of drone
    :return: 0 on successful completion
    """

    db = sql.connect(host='localhost', user='FriendorFoe@localhost', passwd='password', db='DRONES')
    cursor = db.cursor()

    # noinspection SqlNoDataSourceInspection
    query = """INSERT INTO DRONES.POS(DRONENAME, GPSX, GPSY, XPOS, YPOS, SPEED, HEADING, TURN_ANGLE, DIST_TRAVELED) VALUES ("%s", %f, %f, %f, %f, %f, %f, %f, %f)"""

    try:
        cursor.execute(query % (
            dronename, data.LONG, data.LAT, data.XPOS, data.YPOS, data.SPEED, data.HEADING, data.TURNANGLE,
            data.DIST_TRAVELED))
        db.commit()
    except Exception as e1:
        db.rollback()
        print(e1)

    db.close()


if __name__ == '__main__':
    freeze_support()
    main()
