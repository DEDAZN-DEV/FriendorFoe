"""
Author: Julian Pryde
Purpose: To provide functions with which to control server.py
"""

import ctypes
from multiprocessing import Array as SharedArray

import WorkingBuild.server as server

shared_gps_data = SharedArray(typecode_or_type=ctypes.c_double, size_or_initializer=2)
shared_velocity_vector = SharedArray(typecode_or_type=ctypes.c_double, size_or_initializer=2)


def start_server(initial_velocity_vector, dbg_mode):
    """
    Initilizes server with a given velocity vector

    :param initial_velocity_vector: <Array>
    :param dbg_mode: <Boolean> Debug mode (T/F)
    :return: <Int> 0 on success
    """
    print('***')
    server.main(dbg_mode, 'run', shared_gps_data, shared_velocity_vector)
    with shared_velocity_vector.get_lock():
        shared_velocity_vector[0] = initial_velocity_vector[0]
        shared_velocity_vector[1] = initial_velocity_vector[1]

    return 0


def get_gps_data():
    """
    Get gps data from shared buffer for API

    :return: <Array> An array with two elements consisting of x and y positions
    """
    with shared_gps_data.get_lock():
        x_position = shared_gps_data[0]
        y_position = shared_gps_data[1]

    return [x_position, y_position]


def set_velocity_vectors(velocity_vector):
    """
    API function to change velocity vectors

    :param velocity_vector: <Array> New vector [x,y] to be input to our software
    :return: <Int> 0 on success
    """
    with shared_velocity_vector.get_lock():
        shared_velocity_vector[0] = velocity_vector[0]
        shared_velocity_vector[1] = velocity_vector[1]

    return 0
