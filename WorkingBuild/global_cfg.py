"""
Global configuration values, all constants set before start
"""

# CAR VALUES #
ACCELERATION = 15  # of car in m/s**2
CENTER = 1500
ESC = 3
MAX_RIGHT = 1000
NEUTRAL = 1500
MAX_LEFT = 2000
MAX_SPEED = 2000
MAX_TURN_RADIUS = 30  # degrees
MAXVELOCITY = 13.4  # m/s
STEERING = 5
MIN_MOVE_SPEED = 1567
TURNDELAY = 30
TURNDIAMETER = 1.5
TURNFACTOR = 0.001
DEGPERPOINT = 2000 / TURNDIAMETER
SPDSCALE = 2000 / MAXVELOCITY

# TEST VALUES #
MAX_TEST_SPEED = 6500
SPDLIMITER = MAX_SPEED - MAX_TEST_SPEED

# NETWORK VALUES #
CLIENT_IP_A = "10.33.100.132"  # <-- This is the internal IP on the machine running client.py (ipconfig/ifconfig)
COM_PORT = ''
HOST = ''
PORT = 7878

# GPS VALUES #
ORIGIN = [0, 0]
ORIGIN_LATITUDE = 29.190110
ORIGIN_LONGITUDE = -81.046302
CORNER_LAT = 29.190643
CORNER_LONG = -81.045049
ROTATION_ANGLE = -45
RADIUS_OF_EARTH = 6378137  # m
NOISE = 0.0000005

# MOCK SIM VALUES #
DIRCHANGEFACTOR = 0.25  # % chance of changing velocity input for testing
TEST_ITERATIONS = 25
LENGTH_X = 90
LENGTH_Y = 120
UPDATE_INTERVAL = 0.5  # 2Hz refresh rate

# TODO Change this on getting server information from customer
# SIMULATION SERVER
SERVER_BASE_ADDRESS = 'http://pages.erau.edu/~prydej/friendorfoe'
SERVER_POST_ADDRESS = '/post_gps_data.py'
SERVER_GET_ADDRESS = '/get_velocity_vector.py'
