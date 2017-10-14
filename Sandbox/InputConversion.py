import random
import sys


def printf(format, *args):
    sys.stdout.write(format % args)

# TODO: Get current GPS, speed, and heading for car
ORIGIN = [0, 0]

cur_pos = [0, 0]

for i in range(0, 10):
    prev_pos = cur_pos
    cur_pos = [random.randint(0, 10000), random.randint(0, 10000)]

    print prev_pos, cur_pos

# TODO: Get output vector from simulation
    sim_pos = [random.randint(0, 10000), random.randint(0, 10000)]

    print sim_pos
    print

# TODO: Calculate current location in reference to new target location

# TODO: Determine magnitude and speed vector

# TODO: Determine what signals are needed to direct car SERVO

# TODO: Determine what signals are needed to direct car ESC

# TODO: Transmit signals to car through WiFi
