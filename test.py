import cozmo
# pip uninstall cozmoclad
# pip install https://raw.githubusercontent.com/DDLbots/cozmo-python-sdk/refs/heads/master/cozmoclad/cozmoclad-3.6.6-py3-none-any.whl

def print_anim_names(robot: cozmo.robot.Robot):
    anim_names = robot.anim_names
    print(anim_names)

cozmo.run_program(print_anim_names)



