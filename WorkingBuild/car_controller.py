"""
Author: Julian Pryde
Purpose: To provide functions with which to control server.py
"""

import ctypes
from multiprocessing import Array as SharedArray
from WorkingBuild.server import Main as ServerMain


class CarController:
    def __init__(self):
        self.shared_gps_data = SharedArray(typecode_or_type=ctypes.c_double, size_or_initializer=2)
        self.shared_velocity_vector = SharedArray(typecode_or_type=ctypes.c_double, size_or_initializer=2)
        self.server = None

    def start_car(self, initial_velocity_vector, dbg_mode):
        """
        Initializes server with a given velocity vector

        :param initial_velocity_vector: <Array>
        :param dbg_mode: <Boolean> Debug mode (T/F)
        :return: <Int> 0 on success
        """
        print('***')
        self.server = ServerMain()
        self.server.main(dbg_mode, 'run', self, False)
        with self.shared_velocity_vector.get_lock():
            self.shared_velocity_vector[0] = initial_velocity_vector[0]
            self.shared_velocity_vector[1] = initial_velocity_vector[1]

        return 0

    def get_gps_data(self):
        """
        Get gps data from shared buffer for API

        :return: <Array> An array with two elements consisting of x and y positions
        """
        with self.shared_gps_data.get_lock():
            x_position = self.shared_gps_data[0]
            y_position = self.shared_gps_data[1]

        return [x_position, y_position]

    def set_velocity_vectors(self, velocity_vector):
        """
        API function to change velocity vectors

        :param velocity_vector: <Array> New vector [x,y] to be input to our software
        :return: <Int> 0 on success
        """
        with self.shared_velocity_vector.get_lock():
            self.shared_velocity_vector[0] = velocity_vector[0]
            self.shared_velocity_vector[1] = velocity_vector[1]

        return 0
