import math

import pygame

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
        textPrint.indent()

        # For each joystick:
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()

            textPrint.print(screen, "Joystick {}".format(i))
            textPrint.indent()

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

            deg_angle = math.atan2(y_axis, x_axis) * 180 / math.pi

            if deg_angle < 0:
                deg_angle = deg_angle + 360

            textPrint.print(screen, "Joystick angle: {:>6.3f}".format(deg_angle))
            if y_axis != 0 and y_axis != 0:
                velocity_vector = [math.cos(deg_angle * math.pi / 180) * cfg.MAXVELOCITY,
                                   math.sin(deg_angle * math.pi / 180) * cfg.MAXVELOCITY]
            else:
                velocity_vector = [0, 0]

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

            textPrint.unindent()

        # WASD Input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            velocity_vector[0] = -1
        elif keys[pygame.K_RIGHT]:
            velocity_vector[0] = 1
        else:
            velocity_vector[0] = 0

        if keys[pygame.K_UP]:
            velocity_vector[1] = 1
        elif keys[pygame.K_DOWN]:
            velocity_vector[1] = -1
        else:
            velocity_vector[1] = 0

        textPrint.print(screen, "Velocity vector: {:>6.3f} {:>6.3f}". \
                        format(velocity_vector[0], velocity_vector[1]))

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
    print(velocity_vector)
    return velocity_vector
