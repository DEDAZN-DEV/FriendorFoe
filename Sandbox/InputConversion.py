import random
import sys


def printf(format, *args):
    sys.stdout.write(format % args)


# TODO: Get current GPS, speed, and heading for car
ORIGIN = [0, 0]

init_pos = ORIGIN
cur_pos = init_pos

for i in range(0, 10):
    prev_pos = cur_pos
    cur_pos = [cur_pos[0] + random.randint(0, 10), cur_pos[1] + random.randint(0, 10)]

    print(prev_pos, cur_pos)

    # Testing...1...2...3. Testing.

# TODO: Get output vector from simulation

# TODO: Calculate current location in reference to new target location

# TODO: Determine magnitude and speed vector

# TODO: Determine what signals are needed to direct car SERVO

# TODO: Determine what signals are needed to direct car ESC

# TODO: Transmit signals to car through WiFi
