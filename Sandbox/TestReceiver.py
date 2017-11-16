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
CENTER = 6000

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

    print("SERIAL TESTING...Please Wait.")

    print(serial_debug())

    test_controller(COM_PORT)

    print("TESTING COMPLETE...")

    print("SERVER ESTABLISHED...")

    while True:
        (conn, address) = sock.accept()
        data = conn.recv(64)

        try:
            print("Received data from: " + conn.getpeername().__str__() + '\t\t' + data.__str__())
            testRunCircle(data.__str__())
        except TypeError as emsg2:
            print(emsg2)
            sys.exit()


def serial_debug():
    global COM_PORT

    list = serial.tools.list_ports.comports()
    available = []
    for port in list:
        available.append(port.device)

    # COM_PORT = available[0]

    return available


def test_controller(port):
    servo = maestro.Controller(port)
    print('SERVO CONNECTION')

    # 3 ESC, 5 STEERING

    servo.setAccel(5, 0)
    servo.setAccel(3, 0)
    print(servo.getMin(5), servo.getMax(5))

    print('SENT SIGNAL')

    servo.setTarget(5, MAX_RIGHT)
    print(servo.getPosition(5))
    time.sleep(1)
    servo.setTarget(5, MAX_LEFT)
    print(servo.getPosition(5))
    time.sleep(1)
    servo.setTarget(5, MAX_RIGHT)
    print(servo.getPosition(5))
    time.sleep(1)
    servo.setTarget(5, CENTER)

    servo.close()

def servoCtl(port, servoNum, val):
    servo = maestro.Controller(port)
    servo.setTarget(servoNum, val)


def testRunCircle(arg):
    arg = arg[2:len(arg)-1]
    print(arg)
    if arg == 'start':
        servoCtl(COM_PORT, STEERING, MAX_RIGHT)
        servoCtl(COM_PORT, ESC, TEST_SPEED)
    elif arg == 'stop':
        servoCtl(COM_PORT, ESC, NEUTRAL)
        servoCtl(COM_PORT, STEERING, CENTER)
    else:
        print("Invalid arguments...")
        sys.exit()


main()
