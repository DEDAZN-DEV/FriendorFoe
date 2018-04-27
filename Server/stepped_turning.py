"""
Authors: Julian Pryde and Jamey Combs

Purpose: To provide an alternative algorithm to the dubins path algorithm for decide how the car turns. This one sets
    three levels of angle differences between the current heading and the desired heading and assigns a specific servo
    command for each of them.

Usage: turn_signals <current heading> <desired heading> <speed in mph> <current x pos> <current y pos> <time step>
"""
import math
import pprint
import sys

import server_cfg as cfg


class Turning:
    def __init__(self, debug):
        self.debug = debug
        if self.debug:
            pass
        print('******INITIALIZED TURNING*******')

    @staticmethod
    def find_angular_difference(heading_1, heading_2):
        """
        Finds difference between two angles off of the same base heading
        :param heading_1:
        :param heading_2:
        :return: the difference
        """
        angular_difference = heading_2 - heading_1
        # print("Wide Angular Difference: " + str(angular_difference))
        if angular_difference >= 180:
            angular_difference -= 360
        elif angular_difference <= -180:
            angular_difference += 360

        return angular_difference

    def check_if_within_heading(self, current_heading, desired_heading, tolerance):
        """
        Check if an angle is less than or equal to a given tolerance
        :param current_heading:
        :param desired_heading:
        :param tolerance:
        :return:
        """
        angular_difference = self.find_angular_difference(current_heading, desired_heading)
        if abs(angular_difference) <= tolerance:
            within_tolerance = True
        else:
            within_tolerance = False
        print("Within tolerance of ", tolerance, " degrees: ", within_tolerance)
        # if debug:
        #     print("Angular Difference: " + str(angular_difference))
        #     print("Tolerance: " + str(tolerance))
        #     print("Within tolerance: " + str(within_tolerance) + "\n")
        return within_tolerance

    def check_right_turn(self, current_heading, desired_heading):
        """
        Check if the turn angle is to the right or the left
        :param current_heading:
        :param desired_heading:
        :return: boolean
        """
        angular_difference = self.find_angular_difference(current_heading, desired_heading)
        if angular_difference >= 0:
            # if debug:
            #     print("Right Turn")
            return True
        else:
            # if debug:
            #     print("Left Turn")
            return False

    def choose_wheel_turn_angle(self, current_heading, desired_heading):
        """
        Choose the angle at which the wheels have to turn
        :param current_heading:
        :param desired_heading:
        :return:
        """

        tolerance = 20
        half_circle_difference = desired_heading - current_heading

        if half_circle_difference > 180:
            half_circle_difference = half_circle_difference - 360
        elif half_circle_difference < -180:
            half_circle_difference = half_circle_difference + 360
        else:
            print("TURN ANGLE CHECK [OK]")

        if self.check_if_within_heading(current_heading, desired_heading, tolerance):
            print("Within Tolerance")
            turn_angle = half_circle_difference
            speed_coefficient = (25 - abs(turn_angle)) / 25
        elif half_circle_difference > 0:
            print("Less than 0 degrees")
            turn_angle = 20
            speed_coefficient = 0.1
        elif half_circle_difference < 0:
            print("More than 0 degrees")
            turn_angle = -20
            speed_coefficient = 0.1
        else:
            print("HOW?")
            turn_angle = 0
            speed_coefficient = 1

        return turn_angle, speed_coefficient

    def choose_wheel_turn_angle_and_direction(self, current_heading, desired_heading):
        """
        Choose direction and angle of the car's wheels
        :param current_heading:
        :param desired_heading:
        :return:
        """

        turn_angle, speed_coefficient = self.choose_wheel_turn_angle(current_heading, desired_heading)
        print("Turn Angle: ", turn_angle)
        print("Speed Coefficient: ", speed_coefficient)

        return turn_angle, speed_coefficient

    def find_advanced_position(self, car_data):
        """

        :param car_data:
        :return:
        """

        print("TIMESTEP: ", car_data["time_step"])
        car_data["final_heading"] = self.add_angles(car_data["current_heading"], car_data["turning_angle"])
        self.find_speed_components(car_data)

        car_data["advanced_x_position"] = car_data["initial_x_position"] + \
            car_data["time_step"] * car_data["x_speed_component"]
        car_data["advanced_y_position"] = car_data["initial_y_position"] + \
            car_data["time_step"] * car_data["y_speed_component"]

        if self.debug:
            pass
        printer = pprint.PrettyPrinter(indent=4)
        printer.pprint(car_data)
        print("\n")

        return car_data

    @staticmethod
    def find_speed_components(car_data):
        car_data["x_speed_component"] = \
            car_data["speed"] * math.sin(math.radians(car_data["final_heading"]))
        car_data["y_speed_component"] = \
            car_data["speed"] * math.cos(math.radians(car_data["final_heading"]))

    @staticmethod
    def add_angles(angle_1, angle_2):
        angle_sum = angle_1 + angle_2
        print("Angle Sum: ", angle_sum)

        if angle_sum < 0:
            angle_sum += 360
        elif angle_sum > 360:
            angle_sum -= 360

        print("Corrected Angle Sum: ", angle_sum)
        return angle_sum

    @staticmethod
    def subtract_angles(angle_1, angle_2):
        angle_difference = angle_1 - angle_2
        print("Angle Difference: ", angle_difference)

        if angle_difference < 0:
            angle_difference += 360

        print("Corrected Angle Difference: ", angle_difference)
        return angle_difference

    # Direction must be a string with either 'x' or 'y'
    @staticmethod
    def find_distance_component(car_data, direction):
        """

        :param car_data:
        :param direction:
        :return:
        """
        initial_position = "initial_" + direction + "_position"
        advanced_position = "advanced_" + direction + "_position"
        distance_component = car_data[advanced_position] - car_data[initial_position]
        return distance_component

    def find_distance_travelled(self, car_data):
        """

        :param car_data:
        :return:
        """
        x_distance_travelled = self.find_distance_component(car_data, 'x')
        y_distance_travelled = self.find_distance_component(car_data, 'y')
        car_data["distance_travelled"] = \
            math.sqrt(x_distance_travelled ** 2 + y_distance_travelled ** 2)  # Pythagorean Theorem

    def stepped_turning_algorithm(self, car_data):
        """

        :param car_data:
        :return:
        """
        no_turn = 0
        # if not self.check_if_within_heading(car_data["speed"], car_data["desired_heading"], tolerance=0.1):
        print("Current Heading: ", car_data["current_heading"])
        print("Desired Heading: ", car_data["desired_heading"])

        car_data["turning_angle"], speed_coefficient = self.choose_wheel_turn_angle_and_direction(
            car_data["current_heading"], car_data["desired_heading"])
        # else:
        #    car_data["turning_angle"] = no_turn
        #    speed_coefficient = 1

        car_data["speed"] *= speed_coefficient
        car_data = self.find_advanced_position(car_data)
        self.find_distance_travelled(car_data)

        return car_data

    def generate_servo_signals(self, cardata):
        """

        :param cardata:
        :return:
        """
        turn_signal = self.gen_turn_signal(cardata.TURNANGLE)
        speed_signal = self.gen_spd_signal(cardata.SPEED)

        return turn_signal, speed_signal

    @staticmethod
    def apply_turn_to_cardata(cardata, turn_data):
        cardata.DIST_TRAVELED = turn_data["distance_travelled"]
        cardata.TURNANGLE = turn_data["turning_angle"]
        cardata.SPEED = turn_data["speed"]
        cardata.TGTXPOS = turn_data["advanced_x_position"]
        cardata.TGTYPOS = turn_data["advanced_y_position"]

    def update_heading(self, cardata):
        print("XPOS: ", cardata.XPOS)
        print("XPOS_PREV: ", cardata.XPOS_PREV)
        print("YPOS: ", cardata.YPOS)
        print("YPOS_PREV: ", cardata.YPOS_PREV)
        new_heading = None

        velocity_vector = [cardata.XPOS - cardata.XPOS_PREV, cardata.YPOS - cardata.YPOS_PREV]

        if velocity_vector[0] != 0 or velocity_vector[1] != 0:
            new_heading = cardata.HEADING + cardata.TURNANGLE  # self.calculate_heading_from_velocity(velocity_vector)

        if cardata.XPOS - cardata.XPOS_PREV != 0 or cardata.YPOS - cardata.YPOS_PREV != 0:
            cardata.HEADING = new_heading
            print("Updated heading: ", new_heading)

    @staticmethod
    def find_vehicle_speed(cardata, velocity_vector):
        cardata.SPEED = math.sqrt(velocity_vector[0] ** 2 +
                                  velocity_vector[1] ** 2)

    @staticmethod
    def initialize_turn_data(cardata, desired_heading):
        turn_data = {
            "current_heading": cardata.HEADING,
            "desired_heading": desired_heading,
            "speed": cardata.SPEED,
            "initial_x_position": cardata.XPOS,
            "initial_y_position": cardata.YPOS,
            "time_step": cardata.INTERVAL_TIMER
        }
        return turn_data

    def calculate_heading_from_velocity(self, velocity_vector, prev_heading):
        self.fix_negative_zeros(velocity_vector)

        print("Velocity Vector: ", velocity_vector)
        output_heading = math.degrees(math.atan2(velocity_vector[0], velocity_vector[1]))

        if output_heading < 0:
            output_heading += 360

        if velocity_vector[0] == 0 and velocity_vector[1] == 0:
            output_heading = prev_heading

        if self.debug:
            print('Velocity vector: ', velocity_vector)
            print('Output Heading: ', output_heading)
        return output_heading

    @staticmethod
    def fix_negative_zeros(velocity_vector):
        if velocity_vector[0] == -0.0:
            velocity_vector[0] = 0.0
            print("fixed x zero: ", velocity_vector[0])
        if velocity_vector[1] == -0.0:
            velocity_vector[1] = 0.0
            print("fixed y zero: ", velocity_vector[1])

    def gen_turn_signal(self, angle):
        """
        Generates turn signal for MSC and transmits to drone
        :param angle: Float, angle of turn for drone
        :return: 0 on successful completion
        """

        if angle < -180 or angle > 180:
            raise ValueError

        # if angle < 0:
        #     turn_signal = int(round(cfg.CENTER + (abs(angle) * cfg.DEGREE_GRADIENT)))
        # else:
        turn_signal = int(round(cfg.CENTER - (angle * cfg.DEGREE_GRADIENT)))

        if turn_signal > cfg.MAX_LEFT:
            turn_signal = cfg.MAX_LEFT
        elif turn_signal < cfg.MAX_RIGHT:
            turn_signal = cfg.MAX_RIGHT

        if self.debug:
            pass
        print("Turn Signal: " + str(turn_signal))

        return turn_signal

    def gen_spd_signal(self, speed):
        """
        Generates speed signal for MSC and transmits to drone
        :param speed: Float, speed to be reached
        :return: 0 on successful completion
        """

        if speed == 0:
            speed_signal = cfg.NEUTRAL
        else:
            speed_signal = round(cfg.MIN_MOVE_SPEED + (speed * cfg.VELOCITY_GRADIENT))

            if speed_signal > cfg.MAX_SPEED:
                speed_signal = cfg.MAX_SPEED
            elif speed_signal < cfg.MIN_MOVE_SPEED:
                speed_signal = cfg.MIN_MOVE_SPEED

        if self.debug:
            pass
        print("Speed Signal: " + str(speed_signal))
        return speed_signal


if __name__ == "__main__":
    debug_mode = True
    if debug_mode:
        print("Current Heading: " + sys.argv[1] + "\nDesired Heading: " + sys.argv[2] + "\nSpeed: " + sys.argv[3] +
              "\nCurrent Position: (" + sys.argv[4] + ", " + sys.argv[5] + ")\nTime step: " + sys.argv[6])

    car = {
        "current_heading": float(sys.argv[1]),
        "desired_heading": float(sys.argv[2]),
        "speed": float(sys.argv[3]),
        "initial_x_position": float(sys.argv[4]),
        "initial_y_position": float(sys.argv[5]),
        "time_step": float(sys.argv[6])
    }

    turning = Turning(debug_mode)
    car = turning.stepped_turning_algorithm(car)

    if debug_mode:
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(car)
        print("Next Position: (" + str(car["advanced_x_position"]) + ", " + str(car["advanced_y_position"]) + ")")
        print("Turning Angle: " + str(car["turning_angle"]))
        print("Turn Speed: " + str(car["speed"]))
