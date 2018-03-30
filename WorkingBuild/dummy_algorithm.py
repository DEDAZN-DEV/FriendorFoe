"""
Stripped down version of server.py for testing purposes only
"""

import sys
import time

from WorkingBuild.car_controller import CarController as Controller

if __name__ == '__main__':
    controller = Controller()
    controller.start_car([2, 2], True)

    while True:
        try:
            time.sleep(1)
            print("GPS Data: " + str(controller.get_gps_data()))
            controller.set_velocity_vectors([1, 1])
        except KeyboardInterrupt:
            print("Exiting...")
            sys.exit()
