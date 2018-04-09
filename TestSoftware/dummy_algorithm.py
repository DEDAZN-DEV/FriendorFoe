"""
Stripped down version of server.py for testing purposes only
"""

import random
import sys
import time

from Server.car_controller import CarController as Controller

if __name__ == '__main__':
    controller = Controller()
    controller.start_server(initial_velocity_vector=[2, 2], debug=False, num_cars=1)
    print("Not in event loop")

    while True:
        try:
            print("\nGPS Data: " + str(controller.get_gps_data()) + "\n")

            time.sleep(1)
            x_velocity = random.randint(1, 10)
            y_velocity = random.randint(1, 10)
            controller.set_velocity_vectors([x_velocity, y_velocity])

        except KeyboardInterrupt:
            print("Exiting...")
            sys.exit()
