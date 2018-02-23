import os
import socket
import sys
import time

import global_cfg as cfg
import maestro as maestro


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('', cfg.PORT))
    except socket.error as emsg1:
        print(emsg1)
        sys.exit()

    sock.listen(5)

    test_controller('/dev/ttyACM0')

    print('TESTING COMPLETE....')

    print('SERVER ESTABLISHED....')
    while True:
        (conn, address) = sock.accept()
        while True:
            try:
        # if len(conn.recv()) <= 0:  # ping server to see if connection is still valid, should return 0 on error
        #     servo_ctl(ESC, NEUTRAL)
        #     servo_ctl(STEERING, CENTER)
        #     print('Lost Connection...Idling....')
        #     sock.close()
        # else: 
                data = conn.recv(64)
                if data:
                    print('Recieved data from: ' + conn.getpeername().__str__() + '\t\t' + data.__str__())
                    result = test_run(data, conn)

                    if result == 404:
                        break

        # except TimeoutError as nosig:
        #     servo_ctl(ESC, NEUTRAL)
        #     servo_ctl(STEERING, CENTER)
            except TypeError as emsg2:
                print(emsg2)
                conn.close()
                sys.exit()
            except socket.error:
                break


def test_controller(port):
    servo = maestro.Controller(port)
    print('SERVO CONNECTION ESTABLISHED....')

    # 3 ESC, 5 STEERING

    servo.setAccel(cfg.STEERING, 50)
    servo.setAccel(cfg.ESC, 100)
    # print(servo.getMin(STEERING), servo.getMax(STEERING))

    print('SENT SIGNAL....')

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
    print('STEERING ARMED....')
    time.sleep(1)

    print(servo.getPosition(cfg.ESC))
    servo.setTarget(cfg.ESC, 8000)
    servo.setTarget(cfg.ESC, cfg.NEUTRAL)
    print(servo.getPosition(cfg.ESC))
    print('MOTOR ARMED....')
    time.sleep(1)

    print('Exiting test_controller function')


def servo_ctl(servo_num, val):
    servo = maestro.Controller('/dev/ttyACM1')

    # TODO: Modify this to accommodate for speed
    servo.setAccel(cfg.STEERING, 50)
    servo.setAccel(cfg.ESC, 100)

    servo.setTarget(servo_num, val)
    print('Exiting servo_ctl function')

def test_run(arg, conn):
    # arg = arg[2:len(arg)-1]
    print(arg)

    if arg == 'kill':
        servo_ctl(cfg.ESC, cfg.NEUTRAL)
        servo_ctl(cfg.STEERING, cfg.CENTER)
        conn.close()
        print('Terminating Client')
        sys.exit()
    elif arg == 'start':
        servo_ctl(cfg.STEERING, cfg.MAX_RIGHT)
        servo_ctl(cfg.ESC, cfg.TEST_SPEED)
    elif arg == 'stop':
        print('***** Stopping')
        servo_ctl(cfg.ESC, cfg.NEUTRAL)
        servo_ctl(cfg.STEERING, cfg.CENTER)
    elif arg == 'gps':
        get_gps(conn)
    elif arg == 'disconnect':
        servo_ctl(cfg.ESC, cfg.NEUTRAL)
        servo_ctl(cfg.STEERING, cfg.CENTER)
        print('Disconnect')
        time.sleep(10)
        conn.close()
        return 404
    else:
        print('No test prompt received, Switching to raw input....')

        tgt = int(arg[0])
        val = int(arg[1:len(arg)])

        # Guard statement to protect servos
        if 4000 <= val <= 8000:
            servo_ctl(tgt, val)

    print('Exiting test_run function')

def get_gps(conn):
    os.system('grep --line-buffered -m 1 GGA /dev/ttyACM2 > gps.txt')
    myfile = open('gps.txt', 'r')
    message = myfile.read()
    myfile.close()
    print(message)
    conn.sendall(message.encode())
    print('GPS SENT')
    print('Exiting get_gps function')


main()
