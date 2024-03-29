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
MIN_SPEED = 1580
TURNDELAY = 30
TURNDIAMETER = 1.5
TURNFACTOR = 0.001
DEGPERPOINT = (MAX_LEFT - MAX_RIGHT) / TURNDIAMETER
SPDSCALE = (MAX_SPEED - MIN_SPEED) / MAXVELOCITY
NUM_DRONES = 2

# NETWORK VALUES #
HOST_IP = "0.0.0.0"
HOST_IP_FOF = "192.168.0.125"  # <-- This is the internal IP on the machine running car_controller.py (ipconfig/ifconfig)
HOST_PORTS = [8000, 8001, 8002]
HOST = ''

# GPS VALUES #
ORIGIN = [0, 0]
ORIGIN_LATITUDE = 29.189537
ORIGIN_LONGITUDE = -81.046341
CORNER_LAT = 29.198097
CORNER_LONG = -81.046161
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
