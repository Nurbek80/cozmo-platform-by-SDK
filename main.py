from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from cozmo_wrapper import CozmoEasy
import uvicorn

app = FastAPI()
cozmo = CozmoEasy()

class Command(BaseModel):
    command: str

@app.post("/command")
def handle_command(cmd: Command):
    command = cmd.command.strip()
    print(f"📥 Received command: {command}")

    # EMOTIONS: friendly/character states only
    if command.lower().startswith("show_emotion "):
        parts = command.split(maxsplit=1)
        if len(parts) == 2:
            _, emotion = parts
            cozmo.show_emotion(emotion)
            return {"status": f"Emotion: {emotion}"}
        else:
            return {"status": "Usage: show_emotion <emotion_name>"}

    elif command.lower() == "list_emotions":
        emotions = cozmo.list_emotions()
        return {"status": "Available emotions", "emotions": emotions}

    # Movement, speech, special, etc.
    elif command.lower().startswith("say "):
        text = command[4:].strip()
        cozmo.say(text)
        return {"status": f"Said: {text}"}

    elif command.lower().startswith("go "):
        parts = command.split()
        if len(parts) == 3:
            _, dist, speed = parts
            try:
                cozmo.go(float(dist), float(speed))
                return {"status": f"Driving {dist}mm at {speed}mm/s"}
            except Exception as e:
                return {"status": f"Error: {e}"}
        else:
            return {"status": "Usage: go <distance_mm> <speed_mmps>"}

    elif command.lower().startswith("turn "):
        parts = command.split()
        if len(parts) == 2:
            _, angle = parts
            try:
                cozmo.turn(float(angle))
                return {"status": f"Turning {angle}°"}
            except Exception as e:
                return {"status": f"Error: {e}"}
        else:
            return {"status": "Usage: turn <angle_degrees>"}

    elif command.lower().startswith("hand "):
        parts = command.split()
        if len(parts) == 2:
            _, pos = parts
            try:
                cozmo.hand(float(pos))
                return {"status": f"Hand (lift) set to {pos}"}
            except Exception as e:
                return {"status": f"Error: {e}"}
        else:
            return {"status": "Usage: hand <pos (0.0-1.0)>"}

    elif command.lower().startswith("head "):
        parts = command.split()
        if len(parts) == 2:
            _, pos = parts
            try:
                cozmo.head(float(pos))
                return {"status": f"Head set to {pos}"}
            except Exception as e:
                return {"status": f"Error: {e}"}
        else:
            return {"status": "Usage: head <pos (0.0-1.0)>"}

    elif command.lower() == "celebrate":
        try:
            cozmo.celebrate()
            return {"status": "Cozmo is celebrating!"}
        except Exception as e:
            return {"status": f"Error: {e}"}

    elif command.lower() == "light on":
        try:
            cozmo.light_on()
            return {"status": "Lights ON"}
        except Exception as e:
            return {"status": f"Error: {e}"}

    elif command.lower() == "light off":
        try:
            cozmo.light_off()
            return {"status": "Lights OFF"}
        except Exception as e:
            return {"status": f"Error: {e}"}

    elif command.lower().startswith("pickup_cube"):
        parts = command.split()
        try:
            if len(parts) == 2:
                cube_number = parts[1]
                cozmo.pickup_cube(cube_number)
                return {"status": f"Tried to pick up cube {cube_number}!"}
            else:
                cozmo.pickup_cube()
                return {"status": "Tried to pick up any visible cube!"}
        except Exception as e:
            return {"status": f"Error: {e}"}

    elif command.lower() == "stop":
        try:
            cozmo.stop()
            return {"status": "Cozmo stopped."}
        except Exception as e:
            return {"status": f"Error: {e}"}

    return {"status": f"Unknown or invalid command: {command}"}

@app.get("/ping")
def ping():
    return {"status": "ok"}

app.mount("/public", StaticFiles(directory="public"), name="public")

@app.get("/")
def serve_frontend():
    return FileResponse("public/index.html")

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
