import cozmo
import asyncio

def pickup_cube(robot: cozmo.robot.Robot):
    print("Looking for a cube...")
    cube = robot.world.wait_for_observed_light_cube(timeout=10)
    if cube:
        print("Cube found! Attempting to pick up...")
        action = robot.pickup_object(cube, num_retries=3)
        action.wait_for_completed()
        print("Done! (Check if Cozmo is holding the cube)")
    else:
        print("No cube found.")

cozmo.run_program(pickup_cube)
