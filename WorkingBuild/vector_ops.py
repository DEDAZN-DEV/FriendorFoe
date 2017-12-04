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

    if zdiff > cfg.MAXVELOCITY / (cfg.UPDATE_INTERVAL / 1000):
        ratio = cfg.MAXVELOCITY / zdiff

        xcom = xdiff * ratio
        ycom = ydiff * ratio
    else:
        ratio = zdiff

        xcom = xdiff
        ycom = ydiff

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

        if newdata[2] > 180:
            newdata[2] = newdata[2] - 360

        newdata[3] = newhdg
    else:
        newdata[2] = 0

    if math.sqrt(vector[0] ** 2 + vector[1] ** 2) > cfg.MAXVELOCITY:
        newdata[4] = cfg.MAXVELOCITY
    else:
        newdata[4] = math.sqrt(vector[0] ** 2 + vector[1] ** 2)

    return newdata


def new_pos(stage, cardata):
    radius = 5

    if stage == 1:
        return [30, 20]
    elif stage == 2:
        return [40, 40]
    elif stage == 3:
        return [50, 65]
    elif stage > 3 and stage <= 25:
        circleangle = math.fmod(cardata[3] + 1, 360)

        x = 50 + radius * math.cos(math.radians(circleangle))
        y = 65 + radius * math.sin(math.radians(circleangle))

        return [x, y]
        #    return [45, 90]
        # elif stage == 5:
        #    return [55, 110]
    else:
        return [75, 110]
