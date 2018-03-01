import WorkingBuild.car_controller as controller
import time

if __name__ == '__main__':
    controller.start_server([2, 2])
    time.sleep(3)
    print(controller.get_gps_data())
    print(controller.set_velocity_vectors([1, 1]))
