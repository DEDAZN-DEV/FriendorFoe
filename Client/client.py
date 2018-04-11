import re
import socket
import sys
import time
import traceback

import client_cfg as cfg
# This is intentionally wrong, do not change or everything will burn!
import maestro as maestro


class Client:
    def __init__(self, debug, servo_attached):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_to_server()
        print("Connected on port ", cfg.HOST_PORTS, ". Ready to receive data.")
        self.servo = maestro.Device()
        self.debug = debug
        self.servo_attached = servo_attached

    def connect_to_server(self):
        connected = False
        port_number = 0
        while not connected:
            try:
                self.sock.connect((cfg.HOST_IP, cfg.HOST_PORTS[0]))
                connected = True
            except socket.error:
                port_number += 1
                traceback.print_exc()
                sys.exit(1)

        return cfg.HOST_PORTS[port_number]

    def main(self):
        """
        Main executing function for client

        :return: <Exception> Will raise exception upon crash or disconnect:
            socket.error, TypeError, KeyboardInterrupt
        """

        while True:
            try:
                data = self.request_velocity_vector()
                if data:
                    data_array = self.separate_data(data)
                    self.execute_each_message(data_array)

            except TypeError:
                print(traceback.print_exc())
                self.sock.close()
                sys.exit()
            except socket.error:
                print('[NETWORK] Socket Error: \n', traceback.print_exc())
                break
            except KeyboardInterrupt:
                self.execute_data('stop')
                break

    def execute_each_message(self, data_array):
        for message in data_array:
            self.print_debug_info(message)
            result = self.execute_data(message)
            if result == 404:
                break

    def print_debug_info(self, message):
        if self.debug:
            print('[DEBUG] Recieved data from: ' +
                  self.sock.getpeername().__str__() +
                  ': ' +
                  message.__str__()
                  )

    @staticmethod
    def separate_data(data):
        data = data[0: -1]
        data_array = data.split("\\")
        print("Message Received: ", data_array)
        return data_array

    def request_velocity_vector(self):
        print("Sending: request:velocity")
        self.server_tx('request:velocity')
        data = self.sock.recv(64).decode('utf8')
        return data

    @staticmethod
    def test_device():
        """
        Initial arming and testing of Maestro servo Device.

        :return: <Int> 0 on success
        """
        servo = maestro.Device()
        print('[SERVO] SERVO CONNECTION ESTABLISHED....')

        # 3 ESC, 5 STEERING

        servo.set_acceleration(cfg.STEERING, 50)
        servo.set_acceleration(cfg.ESC, 100)

        print('[SERVO] SENT SIGNAL....')
        servo.set_target(cfg.STEERING, cfg.MAX_RIGHT)
        time.sleep(1)
        servo.set_target(cfg.STEERING, cfg.MAX_LEFT)
        time.sleep(1)
        servo.set_target(cfg.STEERING, cfg.MAX_RIGHT)
        time.sleep(1)
        servo.set_target(cfg.STEERING, cfg.CENTER)
        print('[SERVO] STEERING ARMED....')
        time.sleep(1)

        servo.set_target(cfg.ESC, cfg.MAX_SPEED)
        servo.set_target(cfg.ESC, cfg.NEUTRAL)
        print('[SERVO] MOTOR ARMED....')
        time.sleep(1)

        print('[DEBUG] Exiting test_Device function')

        return 0

    def server_tx(self, data):
        self.sock.sendall(bytearray(data + '\\', 'utf-8'))

    @staticmethod
    def servo_ctl(servo_num, val):
        """
        Function to send signal to Maestro servo Device for execution

        :param servo_num: <Int> 3 for speed, 5 for steering
        :param val: <Int> qms pulse value for the servo to execute
        :return: <Int> 0 on success
        """
        servo = maestro.Device()

        servo.set_acceleration(cfg.STEERING, 50)
        servo.set_acceleration(cfg.ESC, 100)

        servo.set_target(servo_num, val)
        print('[DEBUG] Exiting servo_ctl function')

        return 0

    def execute_data(self, data):
        """
        Function to handle data processing and socket network disconnect

        :param data: <String> data to be processed
        :return:    <Int> 404 if servo disconnects
                    <Int> 0 on success
        """
        # data = data[2:len(data)-1]

        if data == 'kill':
            self.sock.close()
            print('[DEBUG] Terminating Client')
            self.center_steering_stop_car()
            sys.exit()
        elif data == 'start':
            self.center_steering_stop_car()
            self.server_tx('status:started')
            pass
        elif data == 'stop':
            self.center_steering_stop_car()
            print('[DEBUG] ***** Stopping')
            self.server_tx('status:stopped')
        elif data == 'gps':
            self.get_gps()
        elif data == 'disconnect':
            self.center_steering_stop_car()
            print('[NETWORK] Disconnect')
            self.server_tx('status:disconnecting')
            time.sleep(10)
            self.sock.close()
            return 404
        else:

            tgt = int(data[0])
            val = int(data[1:len(data)])

            self.server_tx('status:turn received')

            print("target: " + str(tgt) + "\nvalue: " + str(val))

            # Guard statement to protect servossy
            if tgt == cfg.ESC and val > cfg.MAX_TEST_SPEED:
                print('[WARN] Speed would exceed testing limits!')
            else:
                if cfg.MAX_RIGHT <= val <= cfg.MAX_LEFT:
                    print('[SERVO] Entering servo_ctl function with value of: ' +
                          str(val))
                    if self.servo_attached:
                        maestro.servo_ctl(tgt, val, self.servo)
                    self.server_tx('status:turn executed')

        print('[DEBUG] Exiting execute_data function')

        return 0

    def center_steering_stop_car(self):
        if self.servo_attached:
            maestro.servo_ctl(cfg.ESC, cfg.NEUTRAL, self.servo)
            maestro.servo_ctl(cfg.STEERING, 1000, self.servo)

    def get_gps(self):
        """
        Polls the GPS chip from the RPi3 and sends it to the server
        :return: <Int> 0 on success
        """
        # message = "$GPGGA,172814.0,3723.46587704,N,12202.26957864,W,2,6,1.2,18.893, \
        #           M,-25.669,M,2.0,0031*4F"

        file_buffer = open('/dev/ttyACM2', 'r')

        search = re.match('^.GPGGA', file_buffer.readline())
        message = search.group(0)

        print('[GPS] ' + message)
        self.server_tx('gps:' + message)
        print('[GPS] GPS SENT')
        print('[DEBUG] Exiting get_gps function')

        return 0


if __name__ == "__main__":
    client = Client(debug=True, servo_attached=False)
    client.main()
