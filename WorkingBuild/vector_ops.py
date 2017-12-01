import math
import random

# Car variables
ACCELERATION = 10  # m/s
UPDATE_INTERVAL = 0.5  # 2Hz refresh rate
DIRCHANGEFACTOR = 01.25  # % chance of changing velocity input
MAXVELOCITY = 13.4  # m/s


def gen_random_vector():
    """
    Creates a random velocity vector bounded by the max velocity of the RC car.
    @return: Returns a two element vector consisting of the x and y component of a velocity.
    """

    newvector = [random.uniform(-MAXVELOCITY, MAXVELOCITY), random.uniform(-MAXVELOCITY, MAXVELOCITY)]
    return newvector


def gen_targeted_vector(cardata, tgtxpos, tgtypos):
    """
    Creates a targeted vector towards a specific position.
    @return: Returns a two element vector consisiting of the x and y component of a velocity.
    """

    xdiff = abs(cardata[0] - tgtxpos)
    ydiff = abs(cardata[1] - tgtypos)
    zdiff = math.sqrt((xdiff ** 2) + (ydiff ** 2))
    newhdg = 0

    # checking quadrants for proper turn angle
    if xdiff > 0 and ydiff > 0:
        newhdg = math.degrees(math.atan(ydiff / xdiff))
    elif xdiff < 0 and ydiff > 0:
        newhdg = 360 + math.degrees(math.atan(ydiff / xdiff))
    elif xdiff < 0 and ydiff < 0:
        newhdg = 180 + math.degrees(math.atan(ydiff / xdiff))
    elif xdiff > 0 and ydiff < 0:
        newhdg = 180 + math.degrees(math.atan(ydiff / xdiff))

    if zdiff > MAXVELOCITY:
        xcom = math.cos(math.radians(newhdg) * MAXVELOCITY)
        ycom = math.sin(math.radians(newhdg) * MAXVELOCITY)
    else:
        xcom = math.cos(math.radians(newhdg) * zdiff)
        ycom = math.sin(math.radians(newhdg) * zdiff)

    print newhdg

    return [xcom, ycom]


def update_pos(vector, flag, data):
    """
    Updates the current position of the drone as well as the heading and turn angle.
    @param vector: The velocity vector (xv, yv).
    @param flag: Whether or not to update the heading and turn angle.
    @param data: Temp storage for the car data; 4 elements (xpos, ypos, angle, heading)
    @return: Returns the updated cardata.
    """

    xdelta = (vector[0] * UPDATE_INTERVAL) + ((1 / 2) * ACCELERATION * (UPDATE_INTERVAL ** 2))
    ydelta = (vector[1] * UPDATE_INTERVAL) + ((1 / 2) * ACCELERATION * (UPDATE_INTERVAL ** 2))

    newdata = data[:]

    newdata[0] = newdata[0] + xdelta  # xpos
    newdata[1] = newdata[1] + ydelta  # ypos

    if flag:
        if ydelta >= 0:
            newdata[2] = math.atan(xdelta / ydelta) * 180 / math.pi  # angle
        else:
            newdata[2] = (math.atan(xdelta / ydelta) * 180 / math.pi) - 180
        if vector[1] >= 0:
            newdata[3] = math.atan(vector[1] / vector[0]) * 180 / math.pi  # heading
        else:
            newdata[3] = (math.atan(vector[1] / vector[0]) * 180 / math.pi) - 180
    else:
        newdata[2] = 0.00

    if newdata[2] < -180:
        newdata[2] = newdata[2] + 360
    elif newdata[2] > 180:
        newdata[2] = newdata[2] - 360

    if newdata[3] < 0:
        newdata[3] = newdata[3] + 360
    elif newdata[3] > 360:
        newdata[3] = newdata[3] - 360

    return newdata


def test_vec(cardata):
    return [cardata[0] + random.randint(-5, 5), cardata[1] + random.randint(-5, 5)]
