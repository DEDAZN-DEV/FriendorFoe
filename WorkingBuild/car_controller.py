"""
Author: Julian Pryde
Purpose: To provide functions with which to control server.py
"""

import asyncio
import random
from concurrent.futures import FIRST_COMPLETED

import WorkingBuild.global_cfg as cfg
from WorkingBuild.server import Drones


class CarController:
    # def __init__(self):
        # pass
        # self.shared_gps_data = SharedArray(typecode_or_type=ctypes.c_double, size_or_initializer=2)
        # self.shared_velocity_vector = SharedArray(typecode_or_type=ctypes.c_double, size_or_initializer=2)

    def start_cars(self, debug, num_drones):
        """
        Initializes server with a given velocity vector

        :param debug: <Boolean> Debug mode (T/F)
        :param num_drones: number of cars being run
        :return: <Int> 0 on success
        """
#       with self.shared_velocity_vector.get_lock():
#           self.shared_velocity_vector[0] = initial_velocity_vector[0]
#           self.shared_velocity_vector[1] = initial_velocity_vector[1]

        # self.server = ServerMain()
        event_loop = asyncio.get_event_loop()
        asyncio.ensure_future(self.run_drones(debug, False, num_drones))
        event_loop.run_forever()

    @staticmethod
    async def run_drones(debug, plot_points, num_drones):
        try:
            droneids = []
            for drone_num in range(1, num_drones + 1):
                droneids.append(random.randint(0, 999))

            futures = [Drones().drone(droneid,
                                      cfg.CLIENT_IP_A,
                                      cfg.PORT,
                                      debug,
                                      plot_points
                                      )
                       for droneid in droneids
                       ]

            done, pending = await asyncio.wait(futures, return_when=FIRST_COMPLETED)
            print("Drones: " + str(droneids))
            print(done.pop().result())

            for future in pending:
                future.cancel()

        except KeyboardInterrupt:
            print('Keyboard Interrupt...ending scheduled tasks')

            print('....Done\n')

#   def get_gps_data(self):
#       """
#       Get gps data from shared buffer for API

#       :return: <Array> An array with two elements consisting of x and y positions
#       """
#       with self.shared_gps_data.get_lock():
#           x_position = self.shared_gps_data[0]
#           y_position = self.shared_gps_data[1]

#       return [x_position, y_position]

#   def set_velocity_vectors(self, velocity_vector):
#       """
#       API function to change velocity vectors

#       :param velocity_vector: <Array> New vector [x,y] to be input to our software
#       :return: <Int> 0 on success
#       """
#       with self.shared_velocity_vector.get_lock():
#           self.shared_velocity_vector[0] = velocity_vector[0]
#           self.shared_velocity_vector[1] = velocity_vector[1]

#       return 0


if __name__ == "__main__":
    car_controller = CarController()
    car_controller.start_cars(True, 1)
