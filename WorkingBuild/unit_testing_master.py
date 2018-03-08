import unittest

import WorkingBuild.global_cfg as cfg
import WorkingBuild.joystick_input as joystick
import WorkingBuild.mock_sim_inputs as mock
import WorkingBuild.server as server
import WorkingBuild.stepped_turning as turn


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
        self.assertEqual(server.gen_turn_signal(-180), cfg.MAX_LEFT)

        self.assertRaises(ValueError, server.gen_turn_signal, -190)
        self.assertRaises(ValueError, server.gen_turn_signal, 190)

        for angle in range(-180, 180):
            self.assertGreaterEqual(server.gen_turn_signal(angle), cfg.MAX_LEFT)
            self.assertLessEqual(server.gen_turn_signal(angle), cfg.MAX_RIGHT)

    # def test_gen_speed_signal(self):  # TODO: Fix speed signal generation
    #     self.assertEqual(server.gen_spd_signal(13.4, 0), cfg.TEST_SPEED)


class TestSteppedTurning(unittest.TestCase):
    def setUp(self):
        pass

    def test_find_angular_difference(self):
        for i in range(0, 360):
            for j in range(0, 360):
                self.assertGreaterEqual(turn.find_angular_difference(i, j), -180)
                self.assertLessEqual(turn.find_angular_difference(i, j), 180)

    def test_check_if_within_heading(self):
        for i in range(0, 360):
            for j in range(0, 360):
                self.assertGreaterEqual(turn.check_if_within_heading(i, j, 0.1), -180)
                self.assertLessEqual(turn.check_if_within_heading(i, j, 0.1), 180)

    def test_check_right_turn(self):
        self.assertFalse(turn.check_right_turn(0, 270))
        self.assertTrue(turn.check_right_turn(270, 0))
        self.assertTrue(turn.check_right_turn(0, 0))

    def test_choose_wheel_turn_angle(self):
        self.assertEqual(turn.choose_wheel_turn_angle(0, 5, (-5, -10, -15), (0.75, 0.50, 0.25)), (-5, 0.75))
        self.assertEqual(turn.choose_wheel_turn_angle(0, 20, (-5, -10, -15), (0.75, 0.50, 0.25)), (-10, 0.50))
        self.assertEqual(turn.choose_wheel_turn_angle(0, 90, (-5, -10, -15), (0.75, 0.50, 0.25)), (-15, 0.25))

        self.assertEqual(turn.choose_wheel_turn_angle(5, 0, (5, 10, 15), (0.75, 0.50, 0.25)), (5, 0.75))
        self.assertEqual(turn.choose_wheel_turn_angle(20, 0, (5, 10, 15), (0.75, 0.50, 0.25)), (10, 0.50))
        self.assertEqual(turn.choose_wheel_turn_angle(90, 0, (5, 10, 15), (0.75, 0.50, 0.25)), (15, 0.25))


class TestMockSimInputs(unittest.TestCase):
    # def test_calc_xy(self): # TODO: This calculation is now invalid due to the continuous updates instead of fixed
    #     self.assertEqual(mock.calc_xy(1, 1, 0, 0, 0), [])

    def test_gen_random_vector(self):
        self.assertLessEqual(mock.gen_random_vector(), [cfg.MAXVELOCITY, cfg.MAXVELOCITY])
        self.assertGreaterEqual(mock.gen_random_vector(), [-cfg.MAXVELOCITY, -cfg.MAXVELOCITY])

if __name__ == '__main__':
    unittest.main()
