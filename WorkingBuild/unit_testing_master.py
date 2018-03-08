import unittest

import WorkingBuild.global_cfg as cfg
import WorkingBuild.joystick_input as joystick
import WorkingBuild.server as server


class TestJoystickOutput(unittest.TestCase):

    def setUp(self):
        pass

    def test_key_inputs(self):
        self.assertAlmostEqual(joystick.gen_velocity_vector(1, 0)[1][0], cfg.MAXVELOCITY)
        self.assertAlmostEqual(joystick.gen_velocity_vector(-1, 0)[1][0], -cfg.MAXVELOCITY)
        self.assertAlmostEqual(joystick.gen_velocity_vector(0, -1)[1][1], -cfg.MAXVELOCITY)
        self.assertAlmostEqual(joystick.gen_velocity_vector(0, 1)[1][1], cfg.MAXVELOCITY)


class TestServerFunctions(unittest.TestCase):
    def setUp(self):
        pass

    def test_gen_turn_signal(self):
        self.assertEqual(server.gen_turn_signal(180), cfg.MAX_RIGHT)
        self.assertEqual(server.gen_turn_signal(0), cfg.CENTER)


if __name__ == '__main__':
    unittest.main()
