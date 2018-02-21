"""
Authors: Julian Pryde and Jamey Combs

Purpose: To provide an alternative algorithm to the dubins path algorithm for decide how the car turns. This one sets
    three levels of angle differences between the current heading and the desired heading and assigns a specific servo
    command for each of them.

Usage: turn_signals <current heading> <desired heading> <speed in mph> <current x pos> <current y pos>
"""
import sys
import math


def find_angular_difference(heading_1, heading_2):
    angular_difference = heading_2 - heading_1
    print("Wide Angular Difference: " + str(angular_difference))
    if angular_difference >= 180:
        angular_difference -= 360
    elif angular_difference <= -180:
        angular_difference += 360

    return angular_difference


def check_if_within_heading(current_heading, desired_heading, tolerance):
    angular_difference = find_angular_difference(current_heading, desired_heading)
    within_tolerance = abs(angular_difference) <= tolerance

    if debug:
        print("Angular Difference: " + str(angular_difference))
        print("Tolerance: " + str(tolerance))
        print("Within tolerance: " + str(within_tolerance) + "\n")
    return within_tolerance


def check_right_turn(current_heading, desired_heading):
    angular_difference = find_angular_difference(current_heading, desired_heading)
    if angular_difference >= 0:
        if debug:
            print("Right Turn")
        return True
    else:
        if debug:
            print("Left Turn")
        return False


def choose_wheel_turn_angle(current_heading, desired_heading, turn_angles, speed_coefficients):
    tolerance_for_small_turn = 5
    tolerance_for_large_turn = 45

    if check_if_within_heading(current_heading, desired_heading, tolerance=tolerance_for_small_turn):
        print("\nWithin 5 degrees")
        return turn_angles[0], speed_coefficients[0]

    elif check_if_within_heading(current_heading, desired_heading, tolerance=tolerance_for_large_turn):
        print("\nWithin 45 degrees")
        return turn_angles[1], speed_coefficients[1]

    else:
        print("\nMore than 45 degrees")
        return turn_angles[2], speed_coefficients[2]


def choose_wheel_turn_angle_and_direction(current_heading, desired_heading):
    left_turns = (-5, -10, -15)
    right_turns = (5, 10, 15)
    speed_coefficients = (0.75, 0.50, 0.25)

    if check_right_turn(current_heading, desired_heading):
        chosen_direction = right_turns
    else:
        chosen_direction = left_turns
    turn_angle, speed_coefficient = choose_wheel_turn_angle(current_heading,
                                                            desired_heading,
                                                            chosen_direction,
                                                            speed_coefficients)
    return turn_angle, speed_coefficient


def find_advanced_position(car_data):
    car_data["final_direction"] = car_data["current_heading"] + car_data["turning_angle"]
    if car_data["final_direction"] < 0:
        car_data["final_direction"] += 360

    car_data["x_speed_component"] = car_data["speed"] * math.sin(car_data["final_direction"])
    car_data["y_speed_component"] = car_data["speed"] * math.cos(car_data["final_direction"])

    car_data["advanced_x_position"] = car_data["initial_x_position"] + \
        car_data["time_step"] * car_data["x_speed_component"]
    car_data["advanced_y_position"] = car_data["initial_y_position"] + \
        car_data["time_step"] * car_data["y_speed_component"]

    if debug:
        print(str(car_data) + "\n")

    return car_data


# Direction must be a string with either 'x' or 'y'
def find_distance_component(car_data, direction):
    initial_position = "initial_" + direction + "_position"
    advanced_position = "advanced_" + direction + "_position"
    distance_component = car_data[advanced_position] - car_data[initial_position]
    return distance_component


def find_distance_travelled(car_data):
    x_distance_travelled = find_distance_component(car_data, 'x')
    y_distance_travelled = find_distance_component(car_data, 'y')
    car_data["distance_travelled"] = math.sqrt(x_distance_travelled**2 + y_distance_travelled**2)  # Pythagorean Theorem


def stepped_turning_algorithm(car_data):
    no_turn = 0
    if not check_if_within_heading(car_data["speed"], car["desired_heading"], tolerance=0.1):
        car_data["turning_angle"], speed_coefficient = choose_wheel_turn_angle_and_direction(
            car["current_heading"], car_data["desired_heading"])
    else:
        car_data["turning_angle"] = no_turn
        speed_coefficient = 1

    car_data["speed"] *= speed_coefficient
    car_data = find_advanced_position(car_data)
    find_distance_travelled(car_data)

    return car_data


if __name__ == "__main__":
    global debug
    debug = True

    if debug:
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

    car = stepped_turning_algorithm(car)

    if debug:
        print(str(car) + "\n")
        print("Next Position: (" + str(car["advanced_x_position"]) + ", " + str(car["advanced_y_position"]) + ")")
        print("Turning Angle: " + str(car["turning_angle"]))
        print("Turn Speed: " + str(car["speed"]))
