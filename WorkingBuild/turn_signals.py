"""
Authors: Julian Pryde and Jamey Combs

Purpose: To provide an alternative algorithm to the dubins path algorithm for decide how the car turns. This one sets
    three levels of angle differences between the current heading and the desired heading and assigns a specific servo
    command for each of them.

Usage: turn_signals <current heading> <desired heading>
"""
import sys


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
    left_turns = (1.4, 1.0, 0.5)
    right_turns = (1.6, 2.0, 2.5)
    speed_coefficients = (0.75, 0.50, 0.25)

    if check_right_turn(current_heading, desired_heading):
        chosen_direction = right_turns
    else:
        chosen_direction = left_turns
    turn_angle, speed_coefficient = choose_wheel_turn_angle(current_heading,
                                                            desired_heading,
                                                            chosen_direction,
                                                            speed_coefficients)
    return turn_angle


def simple_turning_algorithm(current_heading, desired_heading):
    no_turn = 1.5

    if not check_if_within_heading(current_heading, desired_heading, tolerance=0.1):
        turning_servo_command = choose_wheel_turn_angle_and_direction(current_heading, desired_heading)
        return turning_servo_command
    else:
        return no_turn


if __name__ == "__main__":
    global debug
    debug = True

    if debug:
        print("Current Heading: " + sys.argv[1] + "\nDesired Heading: " + sys.argv[2])

    servo_command = simple_turning_algorithm(float(sys.argv[1]), float(sys.argv[2]))

    if debug:
        print("Servo Command: " + str(servo_command))
