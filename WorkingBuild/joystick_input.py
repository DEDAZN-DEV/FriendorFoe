import math

import pygame

import WorkingBuild.car_controller as controller
import WorkingBuild.global_cfg as cfg

# Globals
velocity_vector = [0, 0]

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


# This is a simple class that will help us print to the screen
# It has nothing to do with the joysticks, just outputting the
# information.
class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)
        self.x = 10
        self.y = 10
        self.line_height = 15

    def print(self, window, text_string):
        text_bitmap = self.font.render(text_string, True, BLACK)
        window.blit(text_bitmap, [self.x, self.y])
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10


def init_joystick():
    """
    Initialize joystick/keyboard for use and input

    :return: <Exception> KeyboardInterrupt upon completion
    """
    global velocity_vector

    speed_factor = 0.0

    pygame.init()

    # Set the width and height of the screen [width,height]
    size = [500, 700]
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("Joystick Input")

    # Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # Initialize the joysticks
    pygame.joystick.init()

    # Get ready to print
    textPrint = TextPrint()

    try:
        # -------- Main Program Loop -----------
        while ~done:
            # EVENT PROCESSING STEP
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    done = True  # Flag that we are done so we exit this loop

                # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
                if event.type == pygame.JOYBUTTONDOWN:
                    print("Joystick button pressed.")
                if event.type == pygame.JOYBUTTONUP:
                    print("Joystick button released.")

            # DRAWING STEP
            # First, clear the screen to white. Don't put other drawing commands
            # above this, or they will be erased with this command.
            screen.fill(WHITE)
            textPrint.reset()

            # Get count of joysticks
            joystick_count = pygame.joystick.get_count()

            textPrint.print(screen, "Number of joysticks: {}".format(joystick_count))

            # For each joystick:
            for i in range(joystick_count):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                textPrint.indent()
                textPrint.print(screen, "Joystick {}".format(i))

                # Get the name from the OS for the controller/joystick
                name = joystick.get_name()
                textPrint.print(screen, "Joystick name: {}".format(name))

                # Usually axis run in pairs, up/down for one, and left/right for
                # the other.
                axes = joystick.get_numaxes()
                textPrint.print(screen, "Number of axes: {}".format(axes))

                textPrint.indent()
                for j in range(axes):
                    axis = joystick.get_axis(j)
                    textPrint.print(screen, "Axis {} value: {:>6.3f}".format(j, axis))
                textPrint.unindent()

                # Print the outputted velocity vector
                y_axis = -joystick.get_axis(1)
                x_axis = joystick.get_axis(0)

                deg_angle, velocity_vector = gen_velocity_vector(x_axis, y_axis)

                textPrint.print(screen, "Joystick angle: {:>6.3f}".format(deg_angle))

                buttons = joystick.get_numbuttons()
                textPrint.print(screen, "Number of buttons: {}".format(buttons))

                textPrint.indent()
                for k in range(buttons):
                    button = joystick.get_button(k)
                    textPrint.print(screen, "Button {:>2} value: {}".format(k, button))
                textPrint.unindent()

                # Hat switch. All or nothing for direction, not like joysticks.
                # Value comes back in an array.
                hats = joystick.get_numhats()
                textPrint.print(screen, "Number of hats: {}".format(hats))

                textPrint.indent()
                for n in range(hats):
                    hat = joystick.get_hat(n)
                    textPrint.print(screen, "Hat {} value: {}".format(n, str(hat)))
                textPrint.unindent()

            if joystick_count == 0:
                textPrint.indent()
                textPrint.print(screen, "Arrow Key Input")

                # Arrow Key Input
                x_axis = 0
                y_axis = 0

                keys = pygame.key.get_pressed()

                if keys[pygame.K_LEFT]:
                    # velocity_vector[0] = -cfg.MAXVELOCITY
                    x_axis = -1

                if keys[pygame.K_RIGHT]:
                    # velocity_vector[0] = cfg.MAXVELOCITY
                    x_axis = 1

                if keys[pygame.K_UP]:
                    # velocity_vector[1] = cfg.MAXVELOCITY
                    y_axis = 1

                if keys[pygame.K_DOWN]:
                    # velocity_vector[1] = -cfg.MAXVELOCITY
                    y_axis = -1

                if keys[pygame.K_UP] == False and keys[pygame.K_DOWN] == False:
                    # velocity_vector[1] = 0
                    y_axis = 0

                if keys[pygame.K_LEFT] == False and keys[pygame.K_RIGHT] == False:
                    # velocity_vector[0] = 0
                    x_axis = 0

                if keys[pygame.K_w] and speed_factor < 1.0:
                    speed_factor = speed_factor + 0.005
                elif keys[pygame.K_s] and speed_factor > 0.0:
                    speed_factor = speed_factor - 0.005
                elif keys[pygame.K_1]:
                    speed_factor = 0.25
                elif keys[pygame.K_2]:
                    speed_factor = 0.5
                elif keys[pygame.K_3]:
                    speed_factor = 0.75
                elif keys[pygame.K_4]:
                    speed_factor = 1

                angle, velocity_vector = gen_velocity_vector(x_axis, y_axis)
                velocity_vector = [speed_factor * x for x in velocity_vector]

                textPrint.indent()
                textPrint.print(screen, "X-Axis: {:>d}".format(x_axis))
                textPrint.print(screen, "Y-Axis: {:>d}".format(y_axis))
                textPrint.print(screen, "Speed factor: {:>6.3f}x".format(speed_factor))

            # Velocity vector input to simulation
            controller.set_velocity_vectors(velocity_vector)

            # Display coordinates on screen
            [x, y] = controller.get_gps_data()
            if joystick_count == 0:
                textPrint.unindent()
            else:
                textPrint.indent()

            textPrint.print(screen, "")
            textPrint.print(screen, "*** OUTPUT ***")
            textPrint.print(screen, "Velocity vector: {:>6.3f} {:>6.3f}".
                            format(velocity_vector[0], velocity_vector[1]))

            textPrint.print(screen, "X: {:>6.3f} Y: {:>6.3f}".format(x, y))

            # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

            # Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

            # Limit to 20 frames per second
            clock.tick(120)

    except KeyboardInterrupt:
        # Close the window and quit.
        # If you forget this line, the program will 'hang'
        # on exit if running from IDLE.
        pygame.quit()


def get_vector():
    """
    Gets the vector from keyboard/joystick

    :return: <Vector> The generated vector created by input x,y
    """
    print(velocity_vector)
    return velocity_vector


def gen_velocity_vector(x_input, y_input):
    """
    Calculates the velocity vector based on angle

    :param x_input: <Float> [-1,1] from the x-axis of the input device
    :param y_input: <Float> [-1,1] from the y-axis of the input device
    :return: <List> Angle and velocity vector (x,y)
    """
    deg_angle = math.atan2(y_input, x_input) * 180 / math.pi

    if deg_angle < 0:
        deg_angle = deg_angle + 360

    if x_input != 0 or y_input != 0:
        vector = [math.cos(deg_angle * math.pi / 180) * cfg.MAXVELOCITY,
                  math.sin(deg_angle * math.pi / 180) * cfg.MAXVELOCITY]
    else:
        vector = [0, 0]

    return deg_angle, vector


def start():
    controller.start_server(velocity_vector, True)
    init_joystick()


start()
