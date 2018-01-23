import socket
import sys
import time

import serial
import serial.tools.list_ports

import global_cfg as cfg
import ip_mailerv2
import maestro as maestro


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((cfg.HOST, cfg.PORT))
    except socket.error as emsg1:
        print(emsg1)
        sys.exit()

    sock.listen(5)

    print('SERIAL TESTING....Please Wait.')

    print(serial_debug())

    test_controller(COM_PORT)

    print('TESTING COMPLETE....')

    print('SERVER ESTABLISHED....')

    ip_mailerv2.sendIP('stilwea1@my.erau.edu')

    while True:
        try:
            (conn, address) = sock.accept()
            # if len(conn.recv()) <= 0:  # ping server to see if connection is still valid, should return 0 on error
            #     servo_ctl(ESC, NEUTRAL)
            #     servo_ctl(STEERING, CENTER)
            #     print('Lost Connection...Idling....')
            #     sock.close()
            # else:
            data = conn.recv(64)
            print('Received data from: ' + conn.getpeername().__str__() + '\t\t' + data.__str__())
            test_run(data)

        # except TimeoutError as nosig:
        #     servo_ctl(ESC, NEUTRAL)
        #     servo_ctl(STEERING, CENTER)
        except TypeError as emsg2:
            print(emsg2)
            sys.exit()


def serial_debug():
    global COM_PORT

    comlist = serial.tools.list_ports.comports()
    available = []
    for port in comlist:
        available.append(port.device)

    COM_PORT = available[1]

    return available


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


def servo_ctl(servo_num, val):
    servo = maestro.Controller(COM_PORT)

    # TODO: Modify this to accomadate for speed
    servo.setAccel(cfg.STEERING, 50)
    servo.setAccel(cfg.ESC, 100)

    servo.setTarget(servo_num, val)


def test_run(arg):
    # arg = arg[2:len(arg)-1]
    print(arg)

    if arg == 'kill':
        servo_ctl(cfg.ESC, cfg.NEUTRAL)
        servo_ctl(cfg.STEERING, cfg.CENTER)
        sys.exit()
    elif arg == 'start':
        servo_ctl(cfg.STEERING, cfg.MAX_RIGHT)
        servo_ctl(cfg.ESC, cfg.TEST_SPEED)
    elif arg == 'stop':
        servo_ctl(cfg.ESC, cfg.NEUTRAL)
        servo_ctl(cfg.STEERING, cfg.CENTER)
    else:
        print('No test prompt received, Switching to raw input....')

        data1 = int(arg[0])
        data2 = int(arg[1:len(arg)])

        if 4000 <= data2 <= 8000:
            servo_ctl(data1, data2)


main()
