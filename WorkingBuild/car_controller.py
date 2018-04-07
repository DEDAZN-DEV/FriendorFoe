"""
Author: Julian Pryde
Purpose: To provide functions with which to control server.py
"""

import asyncio
from WorkingBuild.gps_ops import GPSCalculations as GPS
# from concurrent.futures import FIRST_COMPLETED

# import WorkingBuild.global_cfg as cfg
from WorkingBuild.server import Drone


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
        server_coroutine = event_loop.create_server(
            lambda: ServerClientProtocol(debug, plot_points),
            '',
            7878
        )
        server = event_loop.run_until_complete(server_coroutine)
        print("Serving on : ", server.sockets[0].getsockname())
        try:
            event_loop.run_forever()
        except KeyboardInterrupt:
            pass
        server.close()
        event_loop.run_until_complete(server.wait_closed())


class ServerClientProtocol(asyncio.Protocol):
    def __init__(self, debug, plot_points):
        self.transport = None
        self.drone_instance = None
        self.debug = debug
        self.plot_points = plot_points
        self.id = None
        self.gps = GPS(debug)

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from: ', peername)
        self.transport = transport

    def data_received(self, data):
        data = str(data)
        data_array = data.split(':')

        if data_array[0] == 'status':
            print('Vehicle status: ', data_array[1])

        elif data_array[0] == 'gps':
            gps_data = self.gps.parse_gps_msg(data_array[1])
            self.drone_instance.message_passing.post_gps_data(gps_data)
            print('GPS Message: ', gps_data)

        elif data_array[0] == 'id':
            self.id = int(data_array[1])
            if self.drone_instance is None:
                self.drone_instance = Drone(self.debug, self.id, transport=self.transport)
                self.drone_instance.drone(self.debug, self.plot_points)
            else:
                self.drone_instance.drone_id = self.id


if __name__ == "__main__":
    car_controller = CarController()
    car_controller.start_cars(
        debug=True,
        plot_points=True
    )
