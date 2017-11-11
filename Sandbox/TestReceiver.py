import glob
import socket
import sys

import serial

HOST = ''
PORT = 7777


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

    print("TESTING COMPLETE...")
    print("SERVER ESTABLISHED...")

    while True:
        (conn, address) = sock.accept()
        data = conn.recv(64)

        try:
            print("Received data from: " + conn.getpeername().__str__() + '\t\t' + data.__str__())
        except TypeError as emsg2:
            print(emsg2)
            sys.exit()


def serial_debug():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unknown Platform')

    available = []

    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            available.append(port)
        except (OSError, serial.SerialException):
            pass

    return available
