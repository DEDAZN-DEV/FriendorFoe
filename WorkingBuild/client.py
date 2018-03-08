import os
import socket
import sys
import time

import WorkingBuild.global_cfg as cfg
import WorkingBuild.maestro as maestro


def main():
    """
    Main executing function for client

    :return: <Exception> Will raise exception upon crash or disconnect: socket.error, TypeError, KeyboardInterrupt
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('', cfg.PORT))
    except socket.error as emsg1:
        print(emsg1)
        sys.exit()

    sock.listen(5)

    print('[NETWORK] SERVER ESTABLISHED....')

    test_controller('/dev/ttyACM0')

    print('[SERVO] TESTING COMPLETE....')

    while True:
        (conn, address) = sock.accept()
        try:
            while True:
                try:
                    data = conn.recv(64)
                    if data:
                        print('[DEBUG] Recieved data from: ' + conn.getpeername().__str__() + '\t\t' + data.__str__())
                        result = execute_data(data, conn)

                        if result == 404:
                            break

                except TypeError as emsg2:
                    print('[WARN] ' + str(emsg2))
                    conn.close()
                    sys.exit()
                except socket.error:
                    print('[WARN][NETWORK] Socket error')
                    break
        except KeyboardInterrupt:
            execute_data('stop', conn)


def test_controller(port):
    """
    Initial arming and testing of Maestro servo controller.

    :param port: <String> Consists of the RPi3 port that the servo controller is connected to
    :return: <Int> 0 on success
    """
    servo = maestro.Controller(port)
    print('[SERVO] SERVO CONNECTION ESTABLISHED....')

    # 3 ESC, 5 STEERING

    servo.setAccel(cfg.STEERING, 50)
    servo.setAccel(cfg.ESC, 100)
    print(servo.getMin(cfg.STEERING), servo.getMax(cfg.STEERING))

    print('[SERVO] SENT SIGNAL....')

    servo.setTarget(cfg.STEERING, cfg.MAX_RIGHT)
    print(servo.getPosition(cfg.STEERING))
    time.sleep(1)
    servo.setTarget(cfg.STEERING, cfg.MAX_LEFT)
    print(servo.getPosition(cfg.STEERING))
    time.sleep(1)
    servo.setTarget(cfg.STEERING, cfg.MAX_RIGHT)
    print(servo.getPosition(cfg.STEERING))
    time.sleep(1)
    servo.setTarget(cfg.STEERING, cfg.CENTER)
    print('[SERVO] STEERING ARMED....')
    time.sleep(1)

    print(servo.getPosition(cfg.ESC))
    servo.setTarget(cfg.ESC, 8000)
    servo.setTarget(cfg.ESC, cfg.NEUTRAL)
    print(servo.getPosition(cfg.ESC))
    print('[SERVO] MOTOR ARMED....')
    time.sleep(1)

    print('[DEBUG] Exiting test_controller function')

    return 0


def servo_ctl(servo_num, val):
    """
    Function to send signal to Maestro servo controller for execution

    :param servo_num: <Int> 3 for speed, 5 for steering
    :param val: <Int> qms pulse value for the servo to execute
    :return: <Int> 0 on success
    """
    servo = maestro.Controller('/dev/ttyACM0')

    # TODO: Modify this to accommodate for speed
    servo.setAccel(cfg.STEERING, 50)
    servo.setAccel(cfg.ESC, 100)

    servo.setTarget(servo_num, val)
    print('[DEBUG] Exiting servo_ctl function')

    return 0


def execute_data(data, conn):
    """
    Function to handle data processing and socket network disconnect

    :param data: <String> data to be processed
    :param conn: <Connection object> created after successful connect
    :return:    <Int> 404 if servo disconnects
                <Int> 0 on success
    """
    # data = data[2:len(data)-1]
    print(data)

    if data == 'kill':
        servo_ctl(cfg.ESC, cfg.NEUTRAL)
        servo_ctl(cfg.STEERING, cfg.CENTER)
        conn.close()
        print('[DEBUG] Terminating Client')
        sys.exit()
    elif data == 'start':
        servo_ctl(cfg.STEERING, cfg.MAX_RIGHT)
        servo_ctl(cfg.ESC, cfg.TEST_SPEED)
    elif data == 'stop':
        print('[DEBUG] ***** Stopping')
        servo_ctl(cfg.ESC, cfg.NEUTRAL)
        servo_ctl(cfg.STEERING, cfg.CENTER)
    elif data == 'gps':
        get_gps(conn)
    elif data == 'disconnect':
        servo_ctl(cfg.ESC, cfg.NEUTRAL)
        servo_ctl(cfg.STEERING, cfg.CENTER)
        print('[NETWORK] Disconnect')
        time.sleep(10)
        conn.close()
        return 404
    else:

        tgt = int(data[0])
        val = int(data[1:len(data)])

        # Guard statement to protect servossy
        if tgt == cfg.ESC and val > cfg.MAX_TEST_SPEED:
            print('[WARN] Speed would exceed testing limits!')
        else:
            if 4000 <= val <= 8000:
                print('[SERVO] Entering servo_ctl function with value of: ' + str(val))
                servo_ctl(tgt, val)

    print('[DEBUG] Exiting execute_data function')

    return 0


def get_gps(conn):
    """
    Polls the GPS chip from the RPi3 and sends it to the server

    :param conn: <Connection object> Created by successful socket connection
    :return: <Int> 0 on success
    """
    os.system('grep --line-buffered -m 1 GGA /dev/ttyACM2 > gps.txt')
    myfile = open('gps.txt', 'r')
    message = myfile.read()
    myfile.close()
    print('[GPS] ' + message)
    conn.sendall(message.encode())
    print('[GPS] GPS SENT')
    print('[DEBUG] Exiting get_gps function')

    return 0


if __name__ == "__main__":
    main()
