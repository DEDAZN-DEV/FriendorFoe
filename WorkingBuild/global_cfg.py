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
TEST_SPEED = 3000
TURNDELAY = 30
TURNDIAMETER = 1.5
TURNFACTOR = 0.001
DEGPERPOINT = 2000 / TURNDIAMETER
SPDSCALE = 2000 / MAXVELOCITY
NUM_DRONES = 2

# TEST VALUES #
MAX_TEST_SPEED = 6500
SPDLIMITER = MAX_SPEED - MAX_TEST_SPEED

# NETWORK VALUES #
HOST_IP = "192.168.0.12"  # <-- This is the internal IP on the machine running car_controller.py (ipconfig/ifconfig)
COM_PORT = ''
HOST = ''
CLIENT_PORTS = [7878, 7879]


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
SERVER_BASE_ADDRESS = 'http://localhost/cgi-bin'
SERVER_POST_ADDRESS = '/post_gps_data.cgi'
SERVER_GET_ADDRESS = '/get_velocity_vector.cgi'
SERVER_HELLO_ADDRESS = '/hello.cgi'
