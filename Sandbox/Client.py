import socket
import sys
import time

import maestro
import serial
import serial.tools.list_ports

HOST = ''
PORT = 7777

COM_PORT = ''

STEERING = 5
MAX_LEFT = 4000
MAX_RIGHT = 8000
CENTER = 5800

ESC = 3
NEUTRAL = 6000
TEST_SPEED = 6320


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((HOST, PORT))
    except socket.error as emsg1:
        print(emsg1)
        sys.exit()

    sock.listen(5)

    print("SERIAL TESTING....Please Wait.")

    print(serial_debug())

    test_controller(COM_PORT)

    print("TESTING COMPLETE....")

    print("SERVER ESTABLISHED....")

    while True:
        try:
            (conn, address) = sock.accept()
            if conn.send("") == 0:  # ping server to see if connection is still valid, should return 0 on error
                servoCtl(ESC, NEUTRAL)
                servoCtl(STEERING, CENTER)
                sock.close()
            else:
                data = conn.recv(64)
                print("Received data from: " + conn.getpeername().__str__() + '\t\t' + data.__str__())
                testRun(data)

        except TimeoutError as nosig:
            servoCtl(ESC, NEUTRAL)
            servoCtl(STEERING, CENTER)
        except TypeError as emsg2:
            print(emsg2)
            sys.exit()


def serial_debug():
    global COM_PORT

    list = serial.tools.list_ports.comports()
    available = []
    for port in list:
        available.append(port.device)

    COM_PORT = available[1]

    return available


def test_controller(port):
    servo = maestro.Controller(port)
    print('SERVO CONNECTION ESTABLISHED....')

    # 3 ESC, 5 STEERING

    servo.setAccel(STEERING, 50)
    servo.setAccel(ESC, 100)
    # print(servo.getMin(STEERING), servo.getMax(STEERING))

    print('SENT SIGNAL....')

    servo.setTarget(STEERING, MAX_RIGHT)
    print(servo.getPosition(STEERING))
    time.sleep(1)
    servo.setTarget(STEERING, MAX_LEFT)
    print(servo.getPosition(STEERING))
    time.sleep(1)
    servo.setTarget(STEERING, MAX_RIGHT)
    print(servo.getPosition(STEERING))
    time.sleep(1)
    servo.setTarget(STEERING, CENTER)
    print('STEERING ARMED....')
    time.sleep(1)

    print(servo.getPosition(ESC))
    servo.setTarget(ESC, 8000)
    servo.setTarget(ESC, NEUTRAL)
    print(servo.getPosition(ESC))
    print('MOTOR ARMED....')
    time.sleep(1)


def servoCtl(servoNum, val):
    servo = maestro.Controller(COM_PORT)
    servo.setTarget(servoNum, val)


def testRun(arg):
    # arg = arg[2:len(arg)-1]
    print(arg)

    if arg == 'kill':
        servoCtl(ESC, NEUTRAL)
        servoCtl(STEERING, CENTER)
        sys.exit()
    elif arg == 'start':
        servoCtl(STEERING, MAX_RIGHT)
        servoCtl(ESC, TEST_SPEED)
    elif arg == 'stop':
        servoCtl(ESC, NEUTRAL)
        servoCtl(STEERING, CENTER)
    else:
        print("No test prompt received, Defaulting to raw input....")
        data1 = int(arg[0])
        data2 = int(arg[1:len(arg)])

        if 4000 <= data2 <= 8000:
            servoCtl(data1, data2)


main()
