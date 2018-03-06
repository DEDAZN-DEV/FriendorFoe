import math

import WorkingBuild.global_cfg as cfg

BASE_X = 0
BASE_Y = 0
X_RATIO = 1
Y_RATIO = 1


def parse_gps_msg(message):
    """
    Gets the current GPS coordinates from the RC car. Currently generates a random GPS coordinate +/- error factor
    @return: Returns the lat and long.
    """

    separator = []

    for char in range(0, len(message)):
        if message[char] == ',':
            separator.append(char)

    print(separator)

    dlat = ''
    mlat = ''
    dlong = ''
    mlong = ''

    # bytes 17 - 26
    print(message)
    for i in range(separator[1] + 1, separator[1] + 3):
        dlat = dlat + message[i]
    for j in range(separator[1] + 3, separator[2]):
        mlat = mlat + message[j]

    dlat = int(dlat)
    mlat = float(mlat)
    mlat = mlat / 60
    latitude = dlat + mlat

    if message[separator[2] + 1] == 'S':
        latitude = -latitude

    print(latitude)

    # bytes 30 - 40
    for k in range(separator[3] + 1, separator[3] + 4):
        dlong = dlong + message[k]
    for n in range(separator[3] + 4, separator[4]):
        mlong = mlong + message[n]

    dlong = int(dlong)
    mlong = float(mlong)
    mlong = mlong / 60
    longitude = dlong + mlong

    if message[separator[4] + 1] == 'W':
        longitude = -longitude

    print(longitude)

    data = scale_xy(gps_to_xy(latitude, longitude))

    return data


def gps_to_xy(lat, lon):
    """

    @param lat:
    @param lon:
    @return:
    """

    calc_originxy()

    radlat = math.radians(lat)
    radlong = math.radians(lon)

    x = radlong - math.radians(cfg.ORIGIN_LONGITUDE)
    y = math.log(math.tan(radlat) + (1 / math.cos(radlat)))

    rot_x = x * math.cos(math.radians(cfg.ROTATION_ANGLE)) - y * math.sin(math.radians(cfg.ROTATION_ANGLE))
    rot_y = y * math.cos(math.radians(cfg.ROTATION_ANGLE)) + x * math.sin(math.radians(cfg.ROTATION_ANGLE))

    xy = [rot_x - BASE_X, rot_y - BASE_Y]

    return xy


def scale_xy(xy):
    set_xy_ratio()

    xy[0] = xy[0] / X_RATIO
    xy[1] = xy[1] / Y_RATIO

    return xy


def deg_to_seconds(val):
    return val * 60 * 60


def gps_debug():
    calc_originxy()
    set_xy_ratio()

    print(parse_gps_msg(''))
    print("----------------")

    corner = gps_to_xy(cfg.CORNER_LAT, cfg.CORNER_LONG)
    print("*** Corner ***")
    print(corner)
    print(scale_xy(corner))

    print("\n*** Center ***")
    center = gps_to_xy((cfg.ORIGIN_LATITUDE + cfg.CORNER_LAT) / 2, (cfg.ORIGIN_LONGITUDE + cfg.CORNER_LONG) / 2)
    print(center)
    print(scale_xy(center))

    print("\n*** Origin ***")
    origin = gps_to_xy(cfg.ORIGIN_LATITUDE, cfg.ORIGIN_LONGITUDE)
    print(origin)
    print(scale_xy(origin))

    print("\n*** Test ***")
    testlat = input('Enter Test Latitude: ')
    testlong = input('Enter Test Longitude: ')
    test = gps_to_xy(float(testlat), float(testlong))
    print(test)
    print(scale_xy(test))


def calc_originxy():
    global BASE_X
    global BASE_Y

    temp = gps_to_xy(cfg.ORIGIN_LATITUDE, cfg.ORIGIN_LONGITUDE)
    BASE_X = temp[0]
    BASE_Y = temp[1]

    return BASE_X, BASE_Y


def set_xy_ratio():
    global X_RATIO
    global Y_RATIO

    temp = gps_to_xy(cfg.CORNER_LAT, cfg.CORNER_LONG)
    Y_RATIO = temp[1] / cfg.LENGTH_Y
    X_RATIO = temp[0] / cfg.LENGTH_X

    return X_RATIO, Y_RATIO
