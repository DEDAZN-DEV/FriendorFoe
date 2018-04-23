"""
Author: Julian Pryde
Purpose: To provide functions with which to control data_handling.py
"""

import asyncio
from timeit import default_timer as timer

import server_cfg as cfg
from data_handling import Drone
from gps_ops import GPSCalculations as GPS


class CarController:

    def start_cars(self, debug, plot_points):
        """
        Initializes server with a given velocity vector

        :param debug: <Boolean> Debug mode (T/F)
        :param plot_points: whether or not to plot points as the drone moves
        :return: <Int> 0 on success
        """
        # drones = self.instantiate_drones(cfg.NUM_DRONES, debug)

        event_loop = asyncio.get_event_loop()
        # futures = [asyncio.ensure_future(drone.drone(debug, plot_points)) for drone in drones]
        self.run_server(event_loop, debug, plot_points)
        event_loop.close()

    @staticmethod
    def run_server(event_loop, debug, plot_points):

        servers = []
        for i in range(cfg.NUM_DRONES):
            coroutine = event_loop.create_server(
                lambda: ServerClientProtocol(debug, plot_points),
                '',
                8000 + i
            )
            server = event_loop.run_until_complete(coroutine)
            servers.append(server)
            print("Serving on: ", server.sockets[0].getsockname())

        try:
            event_loop.run_forever()
        except KeyboardInterrupt:
            pass

        for i, server in enumerate(servers):
            server.close()
            event_loop.run_until_complete(server.wait_closed())


class ServerClientProtocol(asyncio.Protocol):
    def __init__(self, debug, plot_points):
        self.transport = None
        self.drone_instance = None
        self.debug = debug
        self.plot_points = plot_points
        self.gps = GPS(debug)
        self.clients_connected = []
        if self.debug:
            print("******INITIALIZED SERVER******")

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from: ', peername)
        self.clients_connected.append(peername[1])
        if self.debug:
            print("Connected Clients: ", self.clients_connected)
        self.transport = transport
        self.drone_instance = Drone(self.plot_points, self.debug, self.transport)

    def data_received(self, data_stream):
        start = timer()
        data = data_stream.decode()
        data_array = data.split('\\')

        with open('/dev/null', 'w') as null:
            print("Received Data: ", data_stream, flush=True, file=null)

        if self.debug:
            pass
        print("Data Array: ", data_array)
        print("Array Size: ", len(data_array))

        drone_port = data_array[0]
        drone_id = None
        counter = 0
        if self.debug:
            pass
        print("Clients Connected: ", self.clients_connected)
        for client in self.clients_connected:
            if int(drone_port) == int(client):
                drone_id = counter
            counter += 1

        if self.debug:
            print("Drone ID: ", drone_id)

        gga_message = data_array[1]

        if self.debug:
            print("Received GPS data: ", gga_message)

        gps_data = []
        try:
            gps_data = self.gps.parse_gps_msg(gga_message)

        except ValueError:
            if self.debug:
                print('Invalid GPS Message. Using projected position')
            self.drone_instance.cardata.XPOS = self.drone_instance.cardata.TGTXPOS
            self.drone_instance.cardata.YPOS = self.drone_instance.cardata.TGTYPOS

        self.set_position_variables(gps_data)
        self.drone_instance.turning.update_heading(self.drone_instance.cardata)
        self.drone_instance.message_passing.post_gps_data(gps_data, drone_id)
        if self.debug:
            print('GPS Message: ', gps_data)
        self.drone_instance.drone(drone_id)
        stop = timer()

        self.drone_instance.cardata.INTERVAL_TIMER = (stop - start)

        if self.debug:
            print('[TIME] ' + str(self.drone_instance.cardata.INTERVAL_TIMER))

    def set_position_variables(self, gps_data):
        self.drone_instance.cardata.XPOS_PREV = self.drone_instance.cardata.XPOS
        self.drone_instance.cardata.YPOS_PREV = self.drone_instance.cardata.YPOS
        self.drone_instance.cardata.XPOS = self.drone_instance.cardata.TGTXPOS
        self.drone_instance.cardata.YPOS = self.drone_instance.cardata.TGTYPOS
        # self.drone_instance.cardata.XPOS = gps_data[0]
        # self.drone_instance.cardata.YPOS = gps_data[1]

    @staticmethod
    def remove_bytes_array_denotors(data):
        data = data[2:-1]
        return data


if __name__ == "__main__":
    car_controller = CarController()
    car_controller.start_cars(
        debug=False,
        plot_points=True
    )
