"""
Author: Julian Pryde
Purpose: To provide functions with which to control server.py
"""

import asyncio
# from concurrent.futures import FIRST_COMPLETED

import WorkingBuild.global_cfg as cfg
from WorkingBuild.server import Drone


class CarController:
    def start_cars(self, debug, plot_points):
        """
        Initializes server with a given velocity vector

        :param debug: <Boolean> Debug mode (T/F)
        :param plot_points: whether or not to plot the points
        :return: <Int> 0 on success
        """
        drones = self.instantiate_drones(cfg.NUM_DRONES, debug)
        self.connect_sockets(drones, debug)

        event_loop = asyncio.get_event_loop()
        asyncio.ensure_future(self.run_drones(debug, plot_points, drones))
        event_loop.run_forever()

    @staticmethod
    def instantiate_drones(num_drones, debug):
        drones = list()
        for drone_id in range(0, num_drones):
            drones.append(Drone(debug, drone_id))

        return drones

    @staticmethod
    async def run_drones(debug, plot_points, drones):
        try:

            futures = list()
            drone_counter = 0
            for drone in drones:
                await drone.drone(debug, plot_points)
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
    def connect_sockets(drones, debug):
        counter = 0
        for drone in drones:
            print("Drone ", counter, " listening for connections.")
            drone.connection.listen_for_client_connections(counter, debug)
            counter += 1


if __name__ == "__main__":
    car_controller = CarController()
    car_controller.start_cars(
        debug=True,
        plot_points=True
    )
