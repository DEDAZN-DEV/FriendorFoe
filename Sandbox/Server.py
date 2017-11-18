# 12 turn, max power 40.24 watts @ 7772 RPM

import math
import random
import socket
import struct
import sys
import threading
import time
from datetime import datetime

import matplotlib.pyplot as plt

# TODO: Get current GPS, speed, and heading for car
ORIGIN = [0, 0]  # ADJUSTABLE VARIABLES (GLOBAL)
ORIGIN_LATITUDE = 29.195267
ORIGIN_LONGITUDE = -81.054341
CORNER_LAT = 29.196433
CORNER_LONG = -81.054020
RADIUS_OF_EARTH = 6378137  # m
ROTATION_ANGLE = 15  # off x axis rotate clockwise

LENGTH_X = 69
LENGTH_Y = 117
BASE_X = 0
BASE_Y = 0
X_RATIO = 1
Y_RATIO = 1

ACCELERATION = 10  # m/s
UPDATE_INTERVAL = 0.5  # 2Hz refresh rate

DIRCHANGEFACTOR = 01.25  # % chance of changing velocity input
MAXVELOCITY = 13.4  # m/s

TEST_ITERATIONS = 25
POSMAPBUFFERSIZE = 250

CLIENT_IP_A = "10.33.29.9"  # <-- This is the internal IP on the machine running TestReceiver.py (ipconfig/ipconfig)
CLIENT_PORT_A = 7777  # <-- DO NOT CHANGE

CLIENT_IP_B = "127.0.0.1"
CLIENT_PORT_B = 7777

CLIENT_IP_C = "127.0.0.1"
CLIENT_PORT_C = 7777

# Plotting things
plt.ion()


class BColors:
    """
    Wrapper class for console output coloring.
    """

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def main():
    """
    Definition of main to run the code. Testing...
    @return: Nothing
    """
    testtype = sys.argv[1]

    calc_originxy()
    set_xy_ratio()

    if testtype == 'normal':
        a = threading.Thread(target=run, args=(CLIENT_IP_A, CLIENT_PORT_A,))

        # b = threading.Thread(target=run, args=("Drone B", CLIENT_IP_B, CLIENT_PORT_B))

        # c = threading.Thread(target=run, args=("Drone C",))
    elif testtype == 'debug_circle':
        a = threading.Thread(target=test_run, args=(CLIENT_IP_A, CLIENT_PORT_A,))

        # b = threading.Thread(target=run, args=("Drone B", CLIENT_IP_B, CLIENT_PORT_B))

        # c = threading.Thread(target=run, args=("Drone C",))
    elif testtype == 'debug_random':
        a = threading.Thread(target=rand_run, args=(CLIENT_IP_A, CLIENT_PORT_A,))

        # b = threading.Thread(target=run, args=("Drone B", CLIENT_IP_B, CLIENT_PORT_B))

        # c = threading.Thread(target=run, args=("Drone C",))
    else:
        print("Invalid Input")
        sys.exit()

    a.start()
    # b.start()
    # c.start()


def test_run(client_ip, port):
    socket_tx('start', client_ip, port)

    time.sleep(15)

    socket_tx('stop', client_ip, port)


def rand_run(client_ip, port):
    for i in range(10):
        inval = random.randint(4000, 8000)
        print(inval)
        socket_tx(str(inval), client_ip, port)
        time.sleep(2)

    socket_tx('stop', client_ip, port)


def run(dronename, ip, port):
    """
    Definition wrapper to handle the drones in their individual threads
    :param dronename:
    :param ip:
    :param port:
    :return:
    """
    xposstorage = []
    yposstorage = []

    f_init = True  # FLAGS

    counter = 0  # LOCAL VARIABLES
    cardata = [0.0, 0.0, 0.0, 0.0]

    while True:
        xposstorage.append(cardata[0])
        yposstorage.append(cardata[1])

        if len(xposstorage) > POSMAPBUFFERSIZE:  # Remove oldest data from buffer
            xposstorage.pop(0)
            yposstorage.pop(0)

        # TODO: Get output vector from simulation
        temp_data = cardata[:]

        if random.uniform(0, 1) < DIRCHANGEFACTOR or f_init is True:  # Simulate output vector from the simulator
            vector = gen_random_vector()
            f_init = False
            cardata = update_pos(vector, True, temp_data)
        else:
            cardata = update_pos(vector, False, temp_data)

        while cardata[0] < 0.0 or cardata[1] < 0.0 or cardata[0] > 100.0 or cardata[1] > 64.0:
            print(BColors.WARNING + str(
                datetime.now()) + " [WARNING] " + dronename +
                  ": Current heading will hit or exceed boundary edge! Recalculating..." + BColors.ENDC)
            vector = gen_random_vector()
            cardata = update_pos(vector, True, temp_data)

        hexangle = gen_signal(cardata[2])

        counter = counter + 1
        curtime = datetime.now()
        printf(BColors.OKBLUE + "%10s [CONSOLE]%7.5d%10s%45s%15.10f%15.10f%12.5f%12s%11.5f%10s\n" + BColors.ENDC,
               str(curtime), counter, dronename,
               vector.__str__(), cardata[0], cardata[1], cardata[2],
               hexangle, cardata[3], dronename)

        socket_tx(str(curtime) + "     " + hexangle, ip, port)

        time.sleep(UPDATE_INTERVAL)


def gen_random_vector():
    """
    Creates a random velocity vector bounded by the max velocity of the RC car.
    @return: Returns a two element vector consisting of the x and y component of a velocity.
    """

    newvector = [random.uniform(-MAXVELOCITY, MAXVELOCITY), random.uniform(-MAXVELOCITY, MAXVELOCITY)]
    return newvector


def gen_targeted_vector():
    """
    Creates a targeted vector towards a specific position.
    @return: Returns a two element vector consisiting of the x and y component of a velocity.
    """


def update_pos(vector, flag, data):
    """
    Updates the current position of the drone as well as the heading and turn angle.
    @param vector: The velocity vector (xv, yv).
    @param flag: Whether or not to update the heading and turn angle.
    @param data: Temp storage for the car data; 4 elements (xpos, ypos, angle, heading)
    @return: Returns the updated cardata.
    """

    xdelta = (vector[0] * UPDATE_INTERVAL) + ((1 / 2) * ACCELERATION * (UPDATE_INTERVAL ** 2))
    ydelta = (vector[1] * UPDATE_INTERVAL) + ((1 / 2) * ACCELERATION * (UPDATE_INTERVAL ** 2))

    newdata = data[:]

    newdata[0] = newdata[0] + xdelta  # xpos
    newdata[1] = newdata[1] + ydelta  # ypos

    if flag:
        if ydelta >= 0:
            newdata[2] = math.atan(xdelta / ydelta) * 180 / math.pi  # angle
        else:
            newdata[2] = (math.atan(xdelta / ydelta) * 180 / math.pi) - 180
        if vector[1] >= 0:
            newdata[3] = math.atan(vector[1] / vector[0]) * 180 / math.pi  # heading
        else:
            newdata[3] = (math.atan(vector[1] / vector[0]) * 180 / math.pi) - 180
    else:
        newdata[2] = 0.00

    if newdata[2] < -180:
        newdata[2] = newdata[2] + 360
    elif newdata[2] > 180:
        newdata[2] = newdata[2] - 360

    if newdata[3] < 0:
        newdata[3] = newdata[3] + 360
    elif newdata[3] > 360:
        newdata[3] = newdata[3] - 360

    return newdata


def printf(layout, *args):
    """
    Quality of life improvement (Personal sanity).
    @param layout: Standard C layout for printf.
    @param args: Arguments for the placeholders in layout
    @return:
    """

    sys.stdout.write(layout % args)


def parse_gps_msg(message):
    """
    Gets the current GPS coordinates from the RC car. Currently generates a random GPS coordinate +/- error factor
    @return: Returns the lat, long, and altitude.
    """

    # $GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.5,M,46.9,M,,*47

    # 123519 = 12:35:19 UTC
    # 4807.038, N = 48 deg 07.038' N
    # 01131.000, E = 11 deg 32.000' E
    # 1 = Fix quality: 0 = invalid, 1 = GPS fix (SPS), 2 = DGPS fix, 3 = PPS fix, 4 = RTK fix, 5 = Float RTK,
    #       6 = estimated dead reckoning, 7 = manual input mode, 8 = simulation mode
    # 08 = Number of satellites being used
    # 0.9 = Horizontal dilution of position
    # 545.5, M = 545.4 M above mean sea-level
    # 46.9, M = 46.9 M above WGS84 ellipsoid
    # (empty) = Time in seconds since last DGPS update
    # (empty) = DGPS station ID number
    # *47 = checksum data, always begins with *

    # Test GGA message format from UBlox
    # $GPGGA,162254.00,3723.02837,N,12159.39853,W,1,03,2.36,525.6,M,-25.6,M,,*65
    # 74 ASCII characters, 74 byte message length

    # Insert method to poll GPS chips
    poll_gps()

    message = "$GPGGA,162254.00,3723.02837,N,12159.39853,W,1,03,2.36,525.6,M,-25.6,M,,*65"
    # message = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.5,M,46.9,M,,*47"
    separator = []

    for char in range(0, len(message)):
        if message[char] == ',':
            separator.append(char)

    print(separator)

    dlat = ''
    mlat = ''
    dlong = ''
    mlong = ''
    # altitude = ''

    # bytes 17 - 26
    print(message)
    for i in range(separator[1] + 1, separator[1] + 3):
        dlat = dlat + message[i]
    for j in range(separator[1] + 3, separator[2]):
        mlat = mlat + message[j]

    dlat = int(dlat)
    mlat = float(mlat)
    mlat = mlat / 60
    latitude = dlat + mlat

    if message[separator[2] + 1] == 'S':
        latitude = -latitude

    print(latitude)

    # bytes 30 - 40
    for k in range(separator[3] + 1, separator[3] + 4):
        dlong = dlong + message[k]
    for n in range(separator[3] + 4, separator[4]):
        mlong = mlong + message[n]

    dlong = int(dlong)
    mlong = float(mlong)
    mlong = mlong / 60
    longitude = dlong + mlong

    if message[separator[4] + 1] == 'W':
        longitude = -longitude

    print(longitude)

    data = scale_xy(gps_to_xy(latitude, longitude))

    return data


def poll_gps():
    print("Polling car....")


def calc_originxy():
    global BASE_X, BASE_Y

    temp = gps_to_xy(ORIGIN_LATITUDE, ORIGIN_LONGITUDE)
    BASE_X = temp[0]
    BASE_Y = temp[1]


def set_xy_ratio():
    global X_RATIO, Y_RATIO

    temp = gps_to_xy(CORNER_LAT, CORNER_LONG)
    Y_RATIO = temp[1] / LENGTH_Y
    X_RATIO = temp[0] / LENGTH_X


def gps_to_xy(lat, long):
    """

    @param lat:
    @param long:
    @return:
    """
    radlat = math.radians(lat)
    radlong = math.radians(long)

    x = radlong - math.radians(ORIGIN_LONGITUDE)
    y = math.log(math.tan(radlat) + (1 / math.cos(radlat)))

    rot_x = x * math.cos(math.radians(ROTATION_ANGLE)) + y * math.sin(math.radians(ROTATION_ANGLE))
    rot_y = -x * math.sin(math.radians(ROTATION_ANGLE)) + y * math.cos(math.radians(ROTATION_ANGLE))

    xy = [rot_x - BASE_X, rot_y - BASE_Y]
    # xy = [x - BASE_X, y - BASE_Y]

    return xy


def scale_xy(xy):
    xy[0] = xy[0] / X_RATIO
    xy[1] = xy[1] / Y_RATIO

    return xy


def deg_to_seconds(val):
    return val * 60 * 60


def gen_signal(anglevalue):
    """
    Crafts a signal based on the input, IEEE floating point single-percision.
    @param anglevalue: The float value to be converted
    @return: Returns a 32-byte value in hex format.
    """

    # TODO: Determine what signals are needed to direct car SERVO

    return float_to_hex(anglevalue)

    # TODO: Determine what signals are needed to direct car ESC


def float_to_hex(f):  # IEEE 32-bit standard for float representation
    """
    Converts float value to hex value.
    @param f: Float value.
    @return: The hex value of the target float.
    """

    return hex(struct.unpack('<I', struct.pack('<f', f))[0])


def socket_tx(data, client_ip, port):
    """
    Transmits data over a socket
    :param data:
    :param client_ip:
    :param port:
    :return:
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((client_ip, port))
        sock.sendall(data.encode())
        print(BColors.OKGREEN + "Data Sent Successfully..." + BColors.ENDC)
    except ConnectionRefusedError:
        print(BColors.FAIL + "Connection refused...." + BColors.ENDC)
    except TimeoutError:
        print(BColors.FAIL + "Connection timed out...." + BColors.ENDC)


def disable(self):
    """
    Terminating color for console output.
    @param self: Reference to itself.
    @return: Nothing
    """

    self.HEADER = ''
    self.OKBLUE = ''
    self.OKGREEN = ''
    self.WARNING = ''
    self.FAIL = ''
    self.ENDC = ''


def gps_debug():
    calc_originxy()
    set_xy_ratio()

    print(parse_gps_msg(''))
    print("----------------")

    corner = gps_to_xy(CORNER_LAT, CORNER_LONG)
    print("*** Corner ***")
    print(corner)
    print(scale_xy(corner))

    print("\n*** Center ***")
    middle = gps_to_xy((ORIGIN_LATITUDE + CORNER_LAT) / 2, (ORIGIN_LONGITUDE + CORNER_LONG) / 2)
    print(middle)
    print(scale_xy(middle))

    print("\n*** Origin ***")
    origin = gps_to_xy(ORIGIN_LATITUDE, ORIGIN_LONGITUDE)
    print(origin)
    print(scale_xy(origin))

    print("\n*** Test ***")
    test = gps_to_xy(29.195272, -81.054336)
    print(test)
    print(scale_xy(test))


main()  # Invoke main()
