"""
Author: Julian Pryde
Purpose: To provide functions with which to control server.py
"""

import ctypes
from multiprocessing import Array as SharedArray

import WorkingBuild.server as server

shared_gps_data = SharedArray(typecode_or_type=ctypes.c_double, size_or_initializer=2)
shared_velocity_vector = SharedArray(typecode_or_type=ctypes.c_double, size_or_initializer=2)


def start_server(initial_velocity_vector):
    """

    :param initial_velocity_vector:
    :return:
    """
    server.main(True, "run", shared_gps_data, shared_velocity_vector)
    with shared_velocity_vector.get_lock():
        shared_velocity_vector[0] = initial_velocity_vector[0]
        shared_velocity_vector[1] = initial_velocity_vector[1]


def get_gps_data():
    """

    :return:
    """
    with shared_gps_data.get_lock():
        x_position = shared_gps_data[0]
        y_position = shared_gps_data[1]

    return [x_position, y_position]


def set_velocity_vectors(velocity_vector):
    """

    :param velocity_vector:
    :return:
    """
    with shared_velocity_vector.get_lock():
        shared_velocity_vector[0] = velocity_vector[0]
        shared_velocity_vector[1] = velocity_vector[1]
