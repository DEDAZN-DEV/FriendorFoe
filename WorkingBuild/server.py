# 12 turn, max power 40.24 watts @ 7772 RPM

# import asyncio
# import aiohttp
import traceback
import requests
import math
import sys
import matplotlib.pyplot as plt
import json

import WorkingBuild.global_cfg as cfg
import WorkingBuild.gps_ops as gps
from WorkingBuild.stepped_turning import Turning

BUFFERSIZE = 50


class CarData:
    """
    Data structure for drone metrics
    """

    def __init__(self, debug, drone_id):
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
        self.ID = drone_id
        if debug:
            print("******INITIALIZED CARDATA*******")


class Drone:
    def __init__(self, debug, drone_number, transport):
        if debug:
            print("\n******BEGINNING INITIALIZATION******")
        self.debug = debug
        self.drone_id = drone_number
        self.connection = CarConnection(debug, transport)
        self.turning = Turning(debug)
        self.message_passing = ServerMessagePassing(debug)
        self.plotting = Plotting(debug)
        self.gps_calculations = gps.GPSCalculations(debug)
        self.cardata = CarData(debug, self.drone_id)
        if debug:
            print("******FINISHED INITIALIZATION******")

    def drone(self, plot_points):
        """
        Default drone control algorithm. Uses input from ATE-3 Sim to control
        drones.
        :param plot_points: whether or not to open the plot
        :return: Nothing
        """
        try:
            print("\nDrone: ", self.drone_id)
            self.gps_calculations.request_gps_fix(self.connection)
            # self.message_passing.post_gps_data(self.cardata)
            velocity_vector = self.execute_turn()
            if plot_points:
                self.plotting.plot_car_path(self.cardata, self.debug, self.drone_id, velocity_vector)
        except KeyboardInterrupt:
            self.connection.client_tx('disconnect')
            sys.exit()

    def execute_turn(self):
        velocity_vector = self.message_passing.get_velocity_data()
        desired_heading = self.turning.calculate_desired_heading(self.cardata)
        self.turning.find_vehicle_speed(self.cardata, velocity_vector)
        turn_data = self.turning.initialize_turn_data(self.cardata, desired_heading)
        turn_data = self.turning.stepped_turning_algorithm(turn_data)
        self.turning.apply_turn_to_cardata(self.cardata, turn_data)
        turn_signal, speed_signal = self.turning.generate_servo_signals(self.cardata)
        self.connection.send_turn_to_car(speed_signal, turn_signal)
        return velocity_vector


class ServerMessagePassing:

    def __init__(self, debug):
        if debug:
            print('******INITIALIZED API SERVER CONNECTION******')

    @staticmethod
    def post_gps_data(gps_data, drone_id):
        """
        Uses aiohttp to post gps data from a webserver
        :param gps_data: list of [x position, y position]
        :param drone_id: drone id
        :return: true if successful
        """
        gps_data_dict = {"xpos": gps_data[0], "ypos": gps_data[1], "id": drone_id}
#       with aiohttp.ClientSession() as session:
#           with session.post(
        response = requests.post(cfg.SERVER_BASE_ADDRESS + cfg.SERVER_POST_ADDRESS, json=gps_data_dict)
        print(response.status_code)
        print(response.text)

    @staticmethod
    def get_velocity_data():
        """
        Uses aiohttp to get velocity data for the car from a webserver
        :return:
        """
#       with aiohttp.ClientSession() as session:
#           response = session.get(cfg.SERVER_BASE_ADDRESS + cfg.SERVER_GET_ADDRESS)
        response = requests.get(cfg.SERVER_BASE_ADDRESS + cfg.SERVER_GET_ADDRESS)
        print(response.status_code)
        velocity_info = response.text

        print("New Velocity Info: " + velocity_info)
        velocity_info = json.loads(velocity_info)
        print("Decoded Velocity Info: " + str(velocity_info))

        velocity_vector = [velocity_info["xvel"], velocity_info["yvel"]]
        return velocity_vector


class Plotting:
    def __init__(self, debug):
        plt.figure(num=1, figsize=(6, 8))
        plt.ion()
        self.xpos = []
        self.ypos = []
        if debug:
            print('******INITIALIZED PLOTTING******')

    def plot_car_path(self, cardata, debug, dronename, velocity_vector):
        if math.sqrt(velocity_vector[0] ** 2 + velocity_vector[1] ** 2) != 0:
            pause_interval = cardata.DIST_TRAVELED / cardata.SPEED
        else:
            pause_interval = 1e-6  # <-- This is a starter to the program
        print("Pause Interval: " + str(pause_interval))
        if len(self.xpos) > BUFFERSIZE:
            self.xpos.pop(0)
            self.ypos.pop(0)
        self.xpos.append(cardata.XPOS)
        self.ypos.append(cardata.YPOS)
        plt.clf()
        plt.title(dronename)
        if not debug:
            plt.axis([0.0, cfg.LENGTH_X, 0.0, cfg.LENGTH_Y])
        plt.plot(self.xpos, self.ypos, 'k-')
        plt.plot(cardata.TGTXPOS, cardata.TGTYPOS, 'rx')
        plt.grid(True)
        if debug:
            print('Calculated Tgt Pos: ', cardata.TGTXPOS, cardata.TGTYPOS)
            print('Calculated XY Pos: ', cardata.XPOS, cardata.YPOS)
            # print('Interval Time: ', interval_time)
            print('')
        plt.pause(pause_interval)


class CarConnection:
    def __init__(self, debug, transport):
        self.debug = debug
        self.transport = transport
        if debug:
            print('******INITIALIZED CONNECTION*******')

    def client_tx(self, data):
        print("About to send: ", data)
        try:
            self.transport.write(bytearray(data + "\\", 'utf-8'))
        except self.transport.socket.error:
            traceback.print_exc()

    def send_turn_to_car(self, speed_signal, turn_signal):
        print("ABOUT TO SEND: " + str(cfg.STEERING) + str(turn_signal))
        print("AND: " + str(cfg.ESC) + str(speed_signal))
        self.client_tx(str(cfg.STEERING) + str(turn_signal))
        self.client_tx(str(cfg.ESC) + str(speed_signal))


class DebugOutput:
    def __init__(self):
        self.HEADER = '\033[95m'
        self.OKBLUE = '\033[94m'
        self.OKGREEN = '\033[92m'
        self.WARNING = '\033[93m'
        self.FAIL = '\033[91m'
        self.ENDC = '\033[0m'

    @staticmethod
    def printf(layout, *args):
        """
        Printf implementation from C using system calls
        :param layout: String, placeholders and general text.
        :param args: Variables to be inserted in above string.
        :return: 0 on successful completion
        """
        sys.stdout.write(layout % args)

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
