import random
import sys

import matplotlib.pyplot as plt


def printf(format, *args):
    sys.stdout.write(format % args)

# TODO: Get current GPS, speed, and heading for car
ORIGIN = [0, 0]
xPosStorage = []
yPosStorage = []

init_pos = ORIGIN

# while(True):
cur_pos = init_pos

for i in range(0, 25):
    xPosStorage.append(cur_pos[0])
    yPosStorage.append(cur_pos[1])
    cur_pos = [cur_pos[0] + random.randint(-5, 5), cur_pos[1] + random.randint(-5, 5)]

# Testing...1...2...3. Testing. This is a test.
plt.plot(xPosStorage, yPosStorage, ':')
plt.axhline(0, color='red')
plt.axvline(0, color='red')

for xy in zip(xPosStorage, yPosStorage):
    plt.annotate('(%s, %s)' % xy, xy=xy, textcoords='data')
plt.show()

# TODO: Get output vector from simulation

# TODO: Calculate current location in reference to new target location

# TODO: Determine magnitude and speed vector

# TODO: Determine what signals are needed to direct car SERVO

# TODO: Determine what signals are needed to direct car ESC

# TODO: Transmit signals to car through WiFi

# 12 turn, max power 40.24 watts @ 7772 RPM
