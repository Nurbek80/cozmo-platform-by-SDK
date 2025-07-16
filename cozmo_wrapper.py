import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps
import threading
import time
class CozmoEasy:
    def __init__(self):
        self.robot = None
        self._connect_robot()

    def _connect_robot(self):
        def cozmo_program(robot: cozmo.robot.Robot):
            self.robot = robot
            print("✅ Cozmo connected!")
            while True:
                time.sleep(0.5)

        t = threading.Thread(target=cozmo.run_program, args=(cozmo_program,), daemon=True)
        t.start()
        # Wait for self.robot to be set
        for _ in range(60):
            if self.robot:
                break
            time.sleep(0.5)
        if not self.robot:
            print("❌ Cozmo robot connection failed.")

    def _wait_for_robot(self, timeout=10):
        """Wait for self.robot to be set (i.e., for connection), up to timeout seconds."""
        waited = 0
        while self.robot is None and waited < timeout:
            time.sleep(0.2)
            waited += 0.2
        return self.robot is not None

    # Movement and actions
    def say(self, text):
        print(f"🗣️ Saying: '{text}'")
        self.robot.say_text(text).wait_for_completed()

    def go(self, dist, speed):
        print(f"🚗 Driving {dist}mm at {speed}mm/s")
        self.robot.drive_straight(distance_mm(float(dist)), speed_mmps(float(speed))).wait_for_completed()

    def turn(self, angle):
        print(f"↪️ Turning {angle}°")
        self.robot.turn_in_place(degrees(float(angle))).wait_for_completed()

    def hand(self, pos):
        pos = min(max(float(pos), 0.0), 1.0)
        print(f"✋ Setting hand (lift) to {pos}")
        self.robot.set_lift_height(pos).wait_for_completed()

    def head(self, pos):
        pos = min(max(float(pos), 0.0), 1.0)
        angle = cozmo.robot.MIN_HEAD_ANGLE + (cozmo.robot.MAX_HEAD_ANGLE - cozmo.robot.MIN_HEAD_ANGLE) * pos
        print(f"⬆️ Setting head to {pos} ({angle.degrees}°)")
        self.robot.set_head_angle(angle).wait_for_completed()

    def light_on(self):
        print("💡 Backpack lights ON")
        self.robot.set_all_backpack_lights(cozmo.lights.green_light)

    def light_off(self):
        print("❌ Backpack lights OFF")
        self.robot.set_all_backpack_lights(cozmo.lights.off_light)

    def celebrate(self):
        print("🎉 Celebrating!")
        self.robot.play_anim("anim_fistbump_success_02").wait_for_completed()


    def show_emotion(self, emotion_name):
        EMOTIONS = {
            "happy": "anim_meetcozmo_celebration_02",
            "angry": "anim_driving_upset_loop_01",
            "sad": "anim_gotosleep_off_01",
            "surprised": "anim_reacttppl_surprise",
            "excited": "anim_sparking_success_01",
            "bored": "anim_bored_event_01",
            "tired": "anim_energy_failgetout_01",
            "amazed": "anim_reacttocliff_turtleroll_01",
            "disgusted": "anim_codelab_kitchen_yucky_01",
            "afraid": "anim_reacttocliff_turtlerollfail_01",
            "guilty": "anim_workout_lowenergy_getout_01",
            "disappointed": "anim_reacttoblock_frustrated_01",
            "embarrassed": "anim_hiccup_playercure_pickupreact",
            "annoyed": "anim_driving_upset_loop_02",
            "furious": "anim_memorymatch_failgame_cozmo_01",
            "suspicious": "anim_reacttocliff_turtlerollfail_02",
            "rejected": "anim_energy_failgetout_02",
            "confused": "anim_reacttocliff_pickup_02",
        }
        name = emotion_name.lower().strip()
        anim = EMOTIONS.get(name)
        if not anim:
            available = ", ".join(sorted(EMOTIONS))
            print(f"Emotion '{emotion_name}' not found. Available: {available}")
            self.robot.say_text(f"Sorry, I don't know the emotion {emotion_name}.").wait_for_completed()
            return
        print(f"Showing emotion: {name} (anim: {anim})")
        self.robot.play_anim(anim).wait_for_completed()

    def pickup_cube(self, cube_number=None):
        if not self._wait_for_robot():
            print("❌ Cozmo robot not ready.")
            return

        try:
            if cube_number is not None:
                # Get specific cube object
                cube_id = int(cube_number)
                if cube_id == 1:
                    cube = self.robot.world.get_light_cube(cozmo.objects.LightCube1Id)
                elif cube_id == 2:
                    cube = self.robot.world.get_light_cube(cozmo.objects.LightCube2Id)
                elif cube_id == 3:
                    cube = self.robot.world.get_light_cube(cozmo.objects.LightCube3Id)
                else:
                    raise ValueError("Cube number must be 1, 2, or 3.")
                if cube is None:
                    raise Exception(f"Cube {cube_id} is not connected or not visible.")
                # Wait for Cozmo to see it
                print(f"🔎 Waiting for Cube {cube_id} to be visible...")
                self.robot.world.wait_for_observed_light_cube(timeout=8)
            else:
                print("🔎 Looking for any cube...")
                cube = self.robot.world.wait_for_observed_light_cube(timeout=8)
                if cube is None:
                    raise Exception("No cube found.")

            print("🔲 Approaching and picking up the cube...")
            action = self.robot.pickup_object(cube, num_retries=2)
            action.wait_for_completed()
            print("🔼 Lifting the cube high!")
        except Exception as e:
            print("❌ Could not pick up a cube:", e)
            self.robot.say_text("I could not find or pick up the cube.").wait_for_completed()

    def stop(self):
        """Stop all current wheel and lift/head motion."""
        if not self._wait_for_robot():
            return
        try:
            self.robot.abort_all_actions()
            self.robot.drive_wheels(0, 0)
            print("🛑 All robot actions stopped.")
        except Exception as e:
            print(f"Error in stop: {e}")
