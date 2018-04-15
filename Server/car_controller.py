"""
Author: Julian Pryde
Purpose: To provide functions with which to control data_handling.py
"""

import asyncio

import server_cfg as cfg
from data_handling import Drone
from gps_ops import GPSCalculations as GPS


class CarController:

    def start_cars(self, debug, plot_points, gps_connected):
        """
        Initializes server with a given velocity vector

        :param debug: <Boolean> Debug mode (T/F)
        :param plot_points: whether or not to plot points as the drone moves
        :param gps_connected: whether or not there is a gps connected
        :return: <Int> 0 on success
        """
        # drones = self.instantiate_drones(cfg.NUM_DRONES, debug)

        event_loop = asyncio.get_event_loop()
        # futures = [asyncio.ensure_future(drone.drone(debug, plot_points)) for drone in drones]
        self.run_server(event_loop, debug, plot_points, gps_connected)
        event_loop.close()

    @staticmethod
    def run_server(event_loop, debug, plot_points, gps_connected):

        servers = []

        for i in range(cfg.NUM_DRONES):
            coroutine = event_loop.create_server(
                lambda: ServerClientProtocol(debug, plot_points, gps_connected),
                '192.168.0.105',
                8000 + i
            )
            server = event_loop.run_until_complete(coroutine)
            print("Serving on : ", server.sockets[0].getsockname())
            servers.append(server)

        try:
            event_loop.run_forever()
        except KeyboardInterrupt:
            pass

        for j, server in enumerate(servers):
            server.close()
            event_loop.run_until_complete(server.wait_closed())


class ServerClientProtocol(asyncio.Protocol):
    def __init__(self, debug, plot_points, gps_connected):
        self.transport = None
        self.drone_instance = None
        self.debug = debug
        self.plot_points = plot_points
        self.gps_connected = gps_connected
        self.id = None
        self.gps = GPS(debug)
        if self.debug:
            print("******INITIALIZED SERVER******")

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from: ', peername)
        self.id = peername[1]  # port
        self.transport = transport
        self.drone_instance = Drone(self.plot_points, self.debug, self.id, self.transport, self.gps_connected)

    def data_received(self, data):
        data = str(data)
        data = self.remove_bytes_array_denotors(data)
        data_array = data.split('\\')
        if self.debug:
            print("Received Data: ", data)

        for message in data_array:
            message = message.split(':')
            if self.debug:
                print("Message: ", message)
            #           print("Data identifier: ", message[0])
            #           print("Data value: ", message[1])

            if message[0] == 'status':
                print('Vehicle status: ', message[1])

            elif message[0] == 'gps':
                if self.debug:
                    pass
                    print("Received GPS message: ", message[1])

                try:
                    gps_data = self.gps.parse_gps_msg(message[1])
                    self.drone_instance.cardata.XPOS = gps_data[0]
                    self.drone_instance.cardata.YPOS = gps_data[1]

                    self.drone_instance.message_passing.post_gps_data(gps_data, self.id)
                    if self.debug:
                        print('GPS Message: ', gps_data)
                except ValueError:
                    if self.debug:
                        print('Invalid GPS Message...Exiting')
                    self.drone_instance.connection.client_tx('disconnect')
                    self.drone_instance.cardata.XPOS = 222
                    self.drone_instance.cardata.YPOS = 222

            elif message[0] == 'request':
                self.drone_instance.drone()

    @staticmethod
    def remove_bytes_array_denotors(data):
        data = data[2:-1]
        return data


if __name__ == "__main__":
    car_controller = CarController()
    car_controller.start_cars(debug=False, plot_points=False, gps_connected=False)
