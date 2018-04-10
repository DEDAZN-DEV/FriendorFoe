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

from Server import server_cfg as cfg


class Turning:
    def __init__(self, debug):
        self.debug = debug
        if self.debug:
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
        within_tolerance = abs(angular_difference) <= tolerance

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

    def choose_wheel_turn_angle(self, current_heading, desired_heading, turn_angles, speed_coefficients):
        """
        Choose the angle at which the wheels have to turn
        :param current_heading:
        :param desired_heading:
        :param turn_angles:
        :param speed_coefficients:
        :return:
        """
        tolerance_for_small_turn = 5
        tolerance_for_large_turn = 45

        if self.check_if_within_heading(current_heading, desired_heading, tolerance=tolerance_for_small_turn):
            # print("\nWithin 5 degrees")
            return turn_angles[0], speed_coefficients[0]

        elif self.check_if_within_heading(current_heading, desired_heading, tolerance=tolerance_for_large_turn):
            # print("\nWithin 45 degrees")
            return turn_angles[1], speed_coefficients[1]

        else:
            # print("\nMore than 45 degrees")
            return turn_angles[2], speed_coefficients[2]

    def choose_wheel_turn_angle_and_direction(self, current_heading, desired_heading):
        """
        Choose direction and angle of the car's wheels
        :param current_heading:
        :param desired_heading:
        :return:
        """
        left_turns = (-5, -10, -15)
        right_turns = (5, 10, 15)
        speed_coefficients = (0.75, 0.50, 0.25)

        if self.check_right_turn(current_heading, desired_heading):
            chosen_direction = right_turns
        else:
            chosen_direction = left_turns
        turn_angle, speed_coefficient = self.choose_wheel_turn_angle(current_heading,
                                                                     desired_heading,
                                                                     chosen_direction,
                                                                     speed_coefficients
                                                                     )
        return turn_angle, speed_coefficient

    def find_advanced_position(self, car_data):
        """

        :param car_data:
        :return:
        """
        car_data["final_heading"] = self.add_angles(car_data["current_heading"], car_data["turning_angle"])
        self.find_speed_components(car_data)

        car_data["advanced_x_position"] = car_data["initial_x_position"] + \
                                          car_data["time_step"] * car_data["x_speed_component"]
        car_data["advanced_y_position"] = car_data["initial_y_position"] + \
                                          car_data["time_step"] * car_data["y_speed_component"]

        if self.debug:
            printer = pprint.PrettyPrinter(indent=4)
            printer.pprint(car_data)
            print("\n")

        return car_data

    @staticmethod
    def find_speed_components(car_data):
        car_data["x_speed_component"] = car_data["speed"] * math.sin(math.radians(car_data["final_heading"]))
        car_data["y_speed_component"] = car_data["speed"] * math.cos(math.radians(car_data["final_heading"]))

    @staticmethod
    def add_angles(angle_1, angle_2):
        angle_sum = angle_1 + angle_2
        if angle_sum < 0:
            angle_sum += 360

        return angle_sum

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
        if not self.check_if_within_heading(car_data["speed"], car_data["desired_heading"], tolerance=0.1):
            car_data["turning_angle"], speed_coefficient = self.choose_wheel_turn_angle_and_direction(
                car_data["current_heading"], car_data["desired_heading"])
        else:
            car_data["turning_angle"] = no_turn
            speed_coefficient = 1

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
        cardata.HEADING = turn_data["final_heading"]
        cardata.SPEED = turn_data["speed"]
        cardata.TGTXPOS = turn_data["advanced_x_position"]
        cardata.TGTYPOS = turn_data["advanced_y_position"]

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
            "time_step": cfg.UPDATE_INTERVAL  # TODO: Revise this because we don't have a fixed interval
            # TODO: Possibly implement a timer between start and finish of entire interval execution
        }
        return turn_data

    @staticmethod
    def calculate_desired_heading(self, cardata):
        desired_heading = math.atan2((cardata.TGTYPOS - cardata.YPOS), (cardata.TGTXPOS - cardata.XPOS))
        if self.debug:
            print('Last Angle Orientation: ', math.degrees(desired_heading))
        return desired_heading

    @staticmethod
    def gen_turn_signal(angle):
        """
        Generates turn signal for MSC and transmits to drone
        :param angle: Float, angle of turn for drone
        :return: 0 on successful completion
        """

        if angle < -180 or angle > 180:
            raise ValueError

        if angle < 0:
            turn_signal = int(round(cfg.CENTER + (abs(angle) * cfg.DEGREE_GRADIENT)))
        else:
            turn_signal = int(round(cfg.CENTER - (angle * cfg.DEGREE_GRADIENT)))

        if turn_signal > cfg.MAX_LEFT:
            turn_signal = cfg.MAX_LEFT
        elif turn_signal < cfg.MAX_RIGHT:
            turn_signal = cfg.MAX_RIGHT

        print("Turn Signal: " + str(turn_signal))

        return turn_signal

    @staticmethod
    def gen_spd_signal(speed):
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

        print("Turn Signal: " + str(speed_signal))
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
