import socket
import sys
import time

import serial
import serial.tools.list_ports
import maestro

HOST = ''
PORT = 7777

COM_PORT = ''
MAX_LEFT = 4000
MAX_RIGHT = 8000
CENTER = 6000

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

    #while True:
    #    (conn, address) = sock.accept()
    #    data = conn.recv(64)

    #    try:
    #        print("Received data from: " + conn.getpeername().__str__() + '\t\t' + data.__str__())
    #    except TypeError as emsg2:
    #        print(emsg2)
    #        sys.exit()


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
main()
