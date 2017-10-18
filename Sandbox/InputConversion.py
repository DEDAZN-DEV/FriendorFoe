import random
import sys

import matplotlib.pyplot as plt


def printf(format, *args):
    sys.stdout.write(format % args)


# TODO: Get current GPS, speed, and heading for car
# ADJUSTABLE VARIABLES
A_ORIGIN = [0, 0]
A_ACCELERATION = 10  # m/s
A_UPDATE_INTERVAL = 0.003  # 3ms between vector update
A_TEST_ITERATIONS = 25
A_POSMAPBUFFERSIZE = 250
A_DIRCHANGEFACTOR = .15  # % chance of changing direction

# FLAGS
F_INIT = True

# STORAGE LISTS
xPosStorage = []
yPosStorage = []

cur_pos = A_ORIGIN

# Initial setup for mapping
plt.axhline(0, color='red')
plt.axvline(0, color='red')
plt.ion()

while True:
    # for iteration in range(TEST_ITERATIONS):
    xPosStorage.append(cur_pos[0])
    yPosStorage.append(cur_pos[1])

    # Remove oldest data
    if len(xPosStorage) > A_POSMAPBUFFERSIZE:
        xPosStorage.pop(0)
        yPosStorage.pop(0)

    # print(xPosStorage)

    # Map plot
    plt.plot(xPosStorage, yPosStorage, color='black', linewidth=1.25)
    plt.axis([0.0, 64.0, 0.0, 100.0])
    # plt.axis([0.0, 16.0, 0.0, 25.0])  # test values for axis
    plt.autoscale(False)
    plt.pause(0.003)
    plt.clf()
    plt.draw()

    # TODO: Get output vector from simulation

    # Simulate output vector from the simulator
    if random.uniform(0, 1) < A_DIRCHANGEFACTOR or F_INIT is True:
        newVector = [random.uniform(-13.4, 13.4), random.uniform(-13.4, 13.4)]
        F_INIT = False

    # Calculate new x and y coordinate based on last position
    xDelta = (newVector[0] * A_UPDATE_INTERVAL) + ((1 / 2) * A_ACCELERATION * (A_UPDATE_INTERVAL ** 2))
    yDelta = (newVector[1] * A_UPDATE_INTERVAL) + ((1 / 2) * A_ACCELERATION * (A_UPDATE_INTERVAL ** 2))

    temp_pos = cur_pos
    cur_pos = [cur_pos[0] + xDelta, cur_pos[1] + yDelta]

    while cur_pos[0] < 0.0 or cur_pos[1] < 0.0:
        cur_pos = temp_pos
        newVector = [random.uniform(-13.4, 13.4), random.uniform(-13.4, 13.4)]
        xDelta = (newVector[0] * A_UPDATE_INTERVAL) + ((1 / 2) * A_ACCELERATION * (A_UPDATE_INTERVAL ** 2))
        yDelta = (newVector[1] * A_UPDATE_INTERVAL) + ((1 / 2) * A_ACCELERATION * (A_UPDATE_INTERVAL ** 2))
        cur_pos = [cur_pos[0] + xDelta, cur_pos[1] + yDelta]

    # print(cur_pos)

# TODO: Calculate current location in reference to new target location

# TODO: Determine magnitude and speed vector

# TODO: Determine what signals are needed to direct car SERVO

# TODO: Determine what signals are needed to direct car ESC

# TODO: Transmit signals to car through WiFi

# 12 turn, max power 40.24 watts @ 7772 RPM
