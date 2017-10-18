import random
import sys

import matplotlib.pyplot as plt


def printf(format, *args):
    sys.stdout.write(format % args)


# Initial setup for mapping
plt.axhline(0, color='red')
plt.axvline(0, color='red')

# TODO: Get current GPS, speed, and heading for car
# STATIC DECLARATIONS
ORIGIN = [0, 0]
ACCELERATION = 10  # m/s
UPDATE_INTERVAL = 0.003  # 0.003 s between vector update
TEST_ITERATIONS = 25

# STORAGE LISTS
xPosStorage = []
yPosStorage = []

cur_pos = ORIGIN

# while(True):
for iteration in range(TEST_ITERATIONS):
    xPosStorage.append(cur_pos[0])
    yPosStorage.append(cur_pos[1])

    # TODO: Get output vector from simulation

    # Simulate output vector from the simulator
    newVector = [random.uniform(-13.4, 13.4), random.uniform(-13.4, 13.4)]

    # Calculate new x and y coordinate based on last position
    xDelta = (newVector[0] * UPDATE_INTERVAL) + ((1 / 2) * ACCELERATION * (UPDATE_INTERVAL ** 2))
    yDelta = (newVector[1] * UPDATE_INTERVAL) + ((1 / 2) * ACCELERATION * (UPDATE_INTERVAL ** 2))

    cur_pos = [cur_pos[0] + xDelta, cur_pos[1] + yDelta]

    print(cur_pos)

# Map plot
plt.plot(xPosStorage, yPosStorage, ':')

for i in range(len(xPosStorage)):
    plt.annotate(i, (xPosStorage[i], yPosStorage[i]))

plt.show()

# TODO: Calculate current location in reference to new target location

# TODO: Determine magnitude and speed vector

# TODO: Determine what signals are needed to direct car SERVO

# TODO: Determine what signals are needed to direct car ESC

# TODO: Transmit signals to car through WiFi

# 12 turn, max power 40.24 watts @ 7772 RPM
