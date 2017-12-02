import math
import random

import global_cfg as cfg

CIRCLETGTANGLE = 0


def gen_random_vector():
    """
    Creates a random velocity vector bounded by the max velocity of the RC car.
    @return: Returns a two element vector consisting of the x and y component of a velocity.
    """

    newvector = [random.uniform(-cfg.MAXVELOCITY, cfg.MAXVELOCITY), random.uniform(-cfg.MAXVELOCITY, cfg.MAXVELOCITY)]
    return newvector


def gen_targeted_vector(cardata, tgtxpos, tgtypos):
    """
    Creates a targeted vector towards a specific position.
    @return: Returns a two element vector consisiting of the x and y component of a velocity.
    """

    xdiff = tgtxpos - cardata[0]
    ydiff = tgtypos - cardata[1]
    zdiff = math.sqrt((xdiff ** 2) + (ydiff ** 2))

    # checking quadrants for proper turn angle
    newhdg = math.degrees(math.atan2(ydiff, xdiff))

    if newhdg < 0:
        newhdg = newhdg + 360

    if zdiff > cfg.MAXVELOCITY:
        ratio = zdiff / cfg.MAXVELOCITY
    else:
        ratio = zdiff

    xcom = xdiff / ratio
    ycom = ydiff / ratio

    print("HDG: " + str(newhdg))
    print(xdiff, ydiff, zdiff)

    return [xcom, ycom]


def update_pos(vector, data):
    """
    Updates the current position of the drone as well as the heading and turn angle.
    @param vector: The velocity vector (xv, yv).
    @param data: Temp storage for the car data; 4 elements (xpos, ypos, angle, heading)
    @return: Returns the updated cardata.
    """

    xdelta = (vector[0] * cfg.UPDATE_INTERVAL) + ((1 / 2) * cfg.ACCELERATION * (cfg.UPDATE_INTERVAL ** 2))
    ydelta = (vector[1] * cfg.UPDATE_INTERVAL) + ((1 / 2) * cfg.ACCELERATION * (cfg.UPDATE_INTERVAL ** 2))

    newdata = data[:]

    newdata[0] = newdata[0] + xdelta  # xpos
    newdata[1] = newdata[1] + ydelta  # ypos

    newhdg = 0

    print(xdelta, ydelta)

    newhdg = math.degrees(math.atan2(ydelta, xdelta))

    if newhdg < 0:
        newhdg = newhdg + 360

    if newdata[3] != newhdg:
        newdata[2] = newdata[3] - newhdg  # <-- This is what needs to be sent to the car.
        newdata[3] = newhdg
    else:
        newdata[2] = 0

    newdata[4] = math.sqrt(vector[0] ** 2 + vector[1] ** 2)

    return newdata


def new_pos(stage, cardata):
    global CIRCLETGTANGLE

    radius = 5

    if stage == 1:
        return [30, 20]
    elif stage == 2:
        return [40, 40]
    elif stage == 3:
        return [50, 65]
    elif stage == 4:
        return [45, 90]
    elif stage == 5:
        return [55, 110]
