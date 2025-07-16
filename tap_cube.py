import cozmo
import time

def wait_for_tap(robot: cozmo.robot.Robot):
    robot.set_lift_height(0.0).wait_for_completed()
    cube = robot.world.wait_for_observed_light_cube(timeout=10)
    if not cube:
        print("No cube found!")
        return

    print("Waiting for tap on cube...")
    tap = cube.wait_for_tap(timeout=10)
    if tap:
        print("Cube tapped! Cozmo says yay!")
        robot.say_text("Yay!").wait_for_completed()
        action = robot.pickup_object(cube, num_retries=3).wait_for_completed()
        cube.set_lights(cozmo.lights.green_light)
        time.sleep(4)
        cube.set_lights_off()
    else:
        print("Cube was not tapped.")

cozmo.run_program(wait_for_tap)
