# 12 turn, max power 40.24 watts @ 7772 RPM

import math
import random
import socket
import sys
from multiprocessing import Process, freeze_support

import matplotlib.pyplot as plt

import WorkingBuild.global_cfg as cfg
import WorkingBuild.gps_ops as gps
# import WorkingBuild.mock_sim_inputs as vec
import WorkingBuild.stepped_turning as turning

BUFFERSIZE = 50


class BColors:
    """
    Color class for stdout
    """

    def __init__(self):
        pass

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
        self.TGTXPOS = 0.0
        self.TGTYPOS = 0.0
        self.HEADING = 0.0
        self.TURNANGLE = 0.0
        self.SPEED = 0.0
        self.DIST_TRAVELED = 0.0


class Drone:
    """
    """

    def __init__(self, func, ip, port, droneid, debug, shared_gps_data, shared_velocity_vector):
        self.name = droneid
        self.process = Process(target=func,
                               args=('Drone ' + str(droneid), ip, port, debug, shared_gps_data, shared_velocity_vector))

        print('Drone ID: ' + str(self.name))


def main(debug_mode, test_arg, shared_gps_data, shared_velocity_vector):
    """
    Driver function for the entire program. Spawns sub-processes to control
    each drone and then terminates.
    :return: 0 on successful completion
    """

    proclst = []

    try:
        if test_arg == 'run':
            a = Drone(run, cfg.CLIENT_IP_A,
                      cfg.PORT,
                      random.randint(0, 999),
                      debug_mode,
                      shared_gps_data,
                      shared_velocity_vector)
            proclst.append(a)
            a.process.start()
            # a.process.join()

        elif test_type == 'debug_gps':
            gps.gps_debug()

    except KeyboardInterrupt:
        print('Keyboard Interrupt....Killing live processes')
        for i in range(0, len(proclst)):
            if proclst[i].process.is_alive():
                print('Killing Drone ID: ' + str(proclst[i].name))
                proclst[i].process.terminate()
        print('....Done\n')


def update_shared_gps_data(shared_gps_data, cardata):
    """

    :param shared_gps_data:
    :param cardata:
    :return:
    """
    with shared_gps_data.get_lock():
        shared_gps_data[0] = cardata.XPOS
        shared_gps_data[1] = cardata.YPOS


def update_velocity_vector(shared_velocity_vector):
    """

    :param shared_velocity_vector:
    :return:
    """
    velocity_vector = [0, 0]
    with shared_velocity_vector.get_lock():
        velocity_vector[0] = shared_velocity_vector[0]
        velocity_vector[1] = shared_velocity_vector[1]

    return velocity_vector


def run(dronename, ip, port, debug, shared_gps_data, shared_velocity_vector):
    """
    Default drone control algorithm. Uses input from ATE-3 Sim to control
    drones.
    :param debug:
    :param dronename: String, name of drone
    :param ip: String, LAN IP address of drone
    :param port: LAN Port of drone to be controlled, not necessary but can be
    changed.
    :param shared_gps_data: GPS data shared with the simulation
    :param shared_velocity_vector: Velocity vectors that are shared between the sim and the server
    :return: Nothing
    """
    cardata = CarData()
    xpos, ypos = initialize_plot()
    initialize_gps()
    sock = initialize_connection(ip, port)

    while True:
        request_gps_fix(cardata, debug, sock)
        update_shared_gps_data(shared_gps_data, cardata)

        velocity_vector = update_velocity_vector(shared_velocity_vector)
        desired_heading = calculate_desired_heading(cardata, debug)
        find_vehicle_speed(cardata, velocity_vector)
        turn_data = initialize_turn_data(cardata, desired_heading)
        turn_data = turning.stepped_turning_algorithm(turn_data)
        apply_turn_to_cardata(cardata, turn_data)
        turn_signal, speed_signal = generate_servo_signals(cardata)
        send_turn_to_car(sock, speed_signal, turn_signal)

        plot_car_path(cardata, debug, dronename, velocity_vector, xpos, ypos)


def plot_car_path(cardata, debug, dronename, velocity_vector, xpos, ypos):
    pause_interval = cardata.DIST_TRAVELED / cardata.SPEED
    print("Pause Interval: " + str(pause_interval))
    if pause_interval == 0:
        pause_interval = 1e-6  # <-- This is a starter to the program
    if len(xpos) > BUFFERSIZE:
        xpos.pop(0)
        ypos.pop(0)
    xpos.append(cardata.XPOS)
    ypos.append(cardata.YPOS)
    plt.clf()
    plt.title(dronename)
    if not debug:
        plt.axis([0.0, cfg.LENGTH_X, 0.0, cfg.LENGTH_Y])
    plt.plot(xpos, ypos, 'k-')
    plt.plot(cardata.TGTXPOS, cardata.TGTYPOS, 'rx')
    plt.grid(True)
    if debug:
        print('Recieved Vel Vector: ', velocity_vector)
        print('Calculated Tgt Pos: ', cardata.TGTXPOS, cardata.TGTYPOS)
        print('Received Lat, Long: ', cardata.LAT, cardata.LONG)
        print('Calculated XY Pos: ', cardata.XPOS, cardata.YPOS)
        # print('Interval Time: ', interval_time)
        print('')
    plt.pause(pause_interval)


def send_turn_to_car(sock, speed_signal, turn_signal):
    socket_tx(str(cfg.STEERING) + str(turn_signal), sock)
    socket_tx(str(cfg.ESC) + str(speed_signal), sock)


def generate_servo_signals(cardata):
    """

    :param cardata:
    :return:
    """
    turn_signal = gen_turn_signal(cardata.TURNANGLE)
    speed_signal = gen_spd_signal(cardata.SPEED, cardata.TURNANGLE)

    return turn_signal, speed_signal


def apply_turn_to_cardata(cardata, turn_data):
    cardata.DIST_TRAVELED = turn_data["distance_travelled"]
    cardata.TURNANGLE = turn_data["turning_angle"]
    cardata.HEADING = turn_data["final_heading"]
    cardata.SPEED = turn_data["speed"]
    cardata.TGTXPOS = turn_data["advanced_x_position"]
    cardata.TGTYPOS = turn_data["advanced_y_position"]


def find_vehicle_speed(cardata, velocity_vector):
    if abs(cardata.TURNANGLE) < 1.0:
        cardata.SPEED = math.sqrt(velocity_vector[0] ** 2 +
                                  velocity_vector[1] ** 2)
    else:
        cardata.SPEED = 5
        # ^ Relate this to the angle in which its turning,
        # higher angle == slower speed


def initialize_turn_data(cardata, desired_heading):
    turn_data = {
        "current_heading": cardata.HEADING,
        "desired_heading": desired_heading,
        "speed": cardata.SPEED,
        "initial_x_position": cardata.XPOS,
        "initial_y_position": cardata.YPOS,
        "time_step": cfg.UPDATE_INTERVAL
    }
    return turn_data


def calculate_desired_heading(cardata, debug):
    desired_heading = math.atan2((cardata.TGTYPOS - cardata.YPOS), (cardata.TGTXPOS - cardata.XPOS))
    if debug:
        print('Last Angle Orientation: ', math.degrees(desired_heading))
    return desired_heading


def initialize_gps():
    gps.calc_originxy()
    gps.set_xy_ratio()


def initialize_connection(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        return sock
    except KeyboardInterrupt as intrpt:
        sys.exit()


def initialize_plot():
    plt.figure(num=1, figsize=(6, 8))
    plt.ion()
    xpos = []
    ypos = []
    return xpos, ypos


def request_gps_fix(cardata, debug, sock):
    socket_tx('gps', sock)
    message = socket_rx(sock)
    try:
        cardata.XPOS = gps.parse_gps_msg(str(message))[0]
        cardata.YPOS = gps.parse_gps_msg(str(message))[1]
    except TypeError:
        if debug:
            print('Invalid GPS Message...Exiting')
        socket_tx('disconnect', sock)
        sock.close()
        sys.exit()


def printf(layout, *args):
    """
    Printf implementation from C using system calls
    :param layout: String, placeholders and general text.
    :param args: Variables to be inserted in above string.
    :return: 0 on successful completion
    """

    sys.stdout.write(layout % args)


def gen_turn_signal(angle):
    """
    Generates turn signal for MSC and transmits to drone
    :param angle: Float, angle of turn for drone
    :return: 0 on successful completion
    """

    if angle < -180 or angle > 180:
        raise ValueError

    if angle < 0:
        turn_signal = int(round(cfg.CENTER + (abs(angle) * cfg.DEGPERPOINT)))
    else:
        turn_signal = int(round(cfg.CENTER - (angle * cfg.DEGPERPOINT)))

    if turn_signal > 8000:
        turn_signal = cfg.MAX_LEFT
    elif turn_signal < 4000:
        turn_signal = cfg.MAX_RIGHT

    return turn_signal


def gen_spd_signal(speed, angle):
    """
    Generates speed signal for MSC and transmits to drone
    :param speed: Float, speed to be reached
    :param angle: Float, current angle of turn
    :return: 0 on successful completion
    """

    if abs(angle) > 1.0:
        speed_signal = int(round((cfg.TEST_SPEED + (speed * cfg.SPDSCALE)) /
                           (abs(angle) * cfg.TURNFACTOR)))
    else:
        speed_signal = int(round(cfg.TEST_SPEED + (speed * cfg.SPDSCALE)))

    if speed_signal > cfg.MAX_SPEED:
        speed_signal = cfg.MAX_SPEED - cfg.SPDLIMITER  # <- FOR TESTING PURPOSES
    elif speed_signal < cfg.TEST_SPEED:
        speed_signal = cfg.TEST_SPEED

    return speed_signal


def socket_tx(data, sock):
    """
    Transmits specified data to drone through sockets
    :param data: String, data to be transmitted
    :param sock:
    :return: 0 on successful completion
    """

    try:
        sock.sendall(data.encode())
        print('SERVER SENT: ' + data)
        print(BColors.OKGREEN + "Data Sent Successfully..." + BColors.ENDC)
    except socket.herror:
        print(BColors.FAIL + "Connection refused...." + BColors.ENDC)
    except socket.timeout:
        print(BColors.FAIL + "Connection timed out...." + BColors.ENDC)


def socket_rx(sock):
    try:
        message = sock.recv(128)
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


if __name__ == '__main__':
    freeze_support()
    if len(sys.argv) < 2:
        print("Missing argument...\nUsage: python server.py\
               [run, debug_gps]")
        sys.exit()
    else:
        test_type = sys.argv[1]