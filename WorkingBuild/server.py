# 12 turn, max power 40.24 watts @ 7772 RPM

import asyncio
import math
import socket
import sys
import matplotlib.pyplot as plt

import WorkingBuild.global_cfg as cfg
import WorkingBuild.gps_ops as gps
from WorkingBuild.stepped_turning import Turning

BUFFERSIZE = 50


class CarData:
    """
    Data structure for drone metrics
    """

    def __init__(self, debug):
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
        if debug:
            print("******INITIALIZED CARDATA*******")


class Drones:
    @staticmethod
    async def drone(dronename, ip, port, debug, car_controller, plot_points):
        """
        Default drone control algorithm. Uses input from ATE-3 Sim to control
        drones.
        :param debug:
        :param dronename: String, name of drone
        :param ip: String, LAN IP address of drone
        :param port: LAN Port of drone to be controlled, not necessary but can be
        changed.
        :param car_controller: Class containing shared memory for passing info between the cars and the user
        :param plot_points: whether or not to open the plot
        :return: Nothing
        """
        turning = Turning(debug)
        message_passing = ServerMessagePassing(debug)
        connection = CarConnection(ip, port, debug)
        plotting = Plotting(debug)
        gps_calculations = gps.GPSCalculations(debug)
        cardata = CarData(debug)

        try:
            while True:
                print("\n")
                gps_calculations.request_gps_fix(connection, cardata, debug)
                message_passing.update_shared_gps_data(car_controller, cardata)

                await asyncio.sleep(0)

                velocity_vector = await Drones.execute_turn(car_controller,
                                                            cardata,
                                                            connection,
                                                            debug,
                                                            message_passing,
                                                            turning)

                # await asyncio.sleep(0)

                if plot_points:
                    plotting.plot_car_path(cardata, debug, dronename, velocity_vector)
        except KeyboardInterrupt:
            connection.socket_tx('disconnect')
            connection.sock.close()
            sys.exit()

    @staticmethod
    async def execute_turn(car_controller, cardata, connection, debug, message_passing, turning):
        velocity_vector = message_passing.update_velocity_vector(car_controller)
        desired_heading = turning.calculate_desired_heading(cardata, debug)
        turning.find_vehicle_speed(cardata, velocity_vector)
        turn_data = turning.initialize_turn_data(cardata, desired_heading)
        turn_data = turning.stepped_turning_algorithm(turn_data)
        turning.apply_turn_to_cardata(cardata, turn_data)
        turn_signal, speed_signal = turning.generate_servo_signals(cardata)
        connection.send_turn_to_car(speed_signal, turn_signal)
        return velocity_vector


class ServerMessagePassing:

    def __init__(self, debug):
        if debug:
            print('******INITIALIZED SHARED MEMORY*******')

    @staticmethod
    def update_shared_gps_data(car_controller, cardata):
        """
        Updates the shared memory with GPS data from the car
        :param car_controller:
        :param cardata:
        :return:
        """
        with car_controller.shared_gps_data.get_lock():
            car_controller.shared_gps_data[0] = cardata.XPOS
            car_controller.shared_gps_data[1] = cardata.YPOS
            print('Updated Car GPS Position: ',
                  car_controller.shared_gps_data[0],
                  car_controller.shared_gps_data[0]
                  )

    @staticmethod
    def update_velocity_vector(car_controller):
        """
        Updates the velocity vector that the server uses with new info from the user
        :param car_controller:
        :return:
        """
        velocity_vector = [0, 0]
        with car_controller.shared_velocity_vector.get_lock():
            velocity_vector[0] = car_controller.shared_velocity_vector[0]
            velocity_vector[1] = car_controller.shared_velocity_vector[1]
            print('Shared Vel Vector: ', car_controller.shared_velocity_vector[0],
                  ', ', car_controller.shared_velocity_vector[1])
            print('Received Vel Vector: ', velocity_vector)
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
    def __init__(self, ip, port, debug):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((ip, port))
            if debug:
                print('******INITIALIZED CONNECTION*******')
        except KeyboardInterrupt:
            sys.exit()

    def socket_tx(self, data):
        """
        Transmits specified data to drone through sockets
        :param data: String, data to be transmitted
        :return: 0 on successful completion
        """
        output = DebugOutput()
        try:
            print('SENDING: ' + data)
            self.sock.sendall(data.encode('utf8'))
            print('SERVER SENT: ' + data)
            print(output.OKGREEN + "Data Sent Successfully..." + output.ENDC)
        except socket.herror:
            print(output.FAIL + "Connection refused...." + output.ENDC)
        except socket.timeout:
            print(output.FAIL + "Connection timed out...." + output.ENDC)

        response = self.socket_rx()
        while not response:
            print(response)
            pass
        print('Client Response: ' + response)
        return response

    def socket_rx(self):
        output = DebugOutput()
        try:
            message = self.sock.recv(128).decode('utf8')
            # print(output.OKGREEN + "Data Received Successfully..." + output.ENDC)
            return message
        except socket.herror:
            print(output.FAIL + "Connection refused...." + output.ENDC)
        except socket.timeout:
            print(output.FAIL + "Connection timed out...." + output.ENDC)

    def send_turn_to_car(self, speed_signal, turn_signal):
        print("ABOUT TO SEND: " + str(cfg.STEERING) + str(turn_signal))
        print("AND: " + str(cfg.ESC) + str(speed_signal))
        self.socket_tx(str(cfg.STEERING) + str(turn_signal))
        self.socket_tx(str(cfg.ESC) + str(speed_signal))


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
