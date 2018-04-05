"""
Author: Julian Pryde
Purpose: To provide functions with which to control server.py
"""

import asyncio
import socket
import sys
from concurrent.futures import FIRST_COMPLETED

import WorkingBuild.global_cfg as cfg
from WorkingBuild.server import Drone


class CarController:
    def start_cars(self, debug, num_drones, plot_points):
        """
        Initializes server with a given velocity vector

        :param debug: <Boolean> Debug mode (T/F)
        :param num_drones: number of cars being run
        :param plot_points: whether or not to plot the points
        :return: <Int> 0 on success
        """
        drones = self.instantiate_drones(num_drones)
        self.listen_for_drones(drones)

        event_loop = asyncio.get_event_loop()
        asyncio.ensure_future(self.run_drones(debug, plot_points, drones))
        event_loop.run_forever()

    @staticmethod
    def instantiate_drones(num_drones):
        drones = list()
        for drone_num in range(1, num_drones + 1):
            drones.append(Drone())

        return drones

    @staticmethod
    async def run_drones(debug, plot_points, drones):
        try:

            drone_counter = 0
            futures = list()
            for drone in drones:
                drone.drone(drone_counter, debug, plot_points)
                futures.append(drone)
                drone_counter += 1

            done, pending = await asyncio.wait(futures)
            print(done.pop().result())

            for future in pending:
                future.cancel()

        except KeyboardInterrupt:
            print('Keyboard Interrupt...ending scheduled tasks')
            print('....Done\n')

    @staticmethod
    def listen_for_drones(drones):
        for drone in drones:
            drone.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            drone.socket_id = drone

        counter = 0
        for drone in drones:
            try:
                drone.client_socket.bind(('', cfg.CLIENT_PORTS[counter]))
                counter += 1
            except socket.error as emsg1:
                print(emsg1)
                sys.exit()

            drone.client_socket.listen()
            print("Connected. IP: " + drone.client_socket.IP + ", PORT: " + drone.client_socket.IPPORT)


#   def connect_to_client(self, socket):
#       while True:
#           (conn, address) = socket.accept()
#           try:
#               while True:
#                   try:
#                       data = conn.recv(64).decode('utf8')
#                       if data:
#                           print('[DEBUG] Recieved data from: ' +
#                                 conn.getpeername().__str__() +
#                                 '\t\t' +
#                                 data.__str__())
#                           result = execute_data(data, conn)

#                           if result == 404:
#                               break

#                   except TypeError as emsg2:
#                       print('[WARN] ' + str(emsg2))
#                       conn.close()
#                       sys.exit()
#                   except socket.error:
#                       print('[WARN][NETWORK] Socket error')
#                       break
#           except KeyboardInterrupt:
#               execute_data('stop', conn)

if __name__ == "__main__":
    car_controller = CarController()
    car_controller.start_cars(
        debug=True,
        num_drones=2,
        plot_points=True
    )
