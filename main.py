from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from cozmo_wrapper import CozmoEasy
import uvicorn
import threading
import re

app = FastAPI()
cozmo = CozmoEasy()

class Program(BaseModel):
    program: str

def parse_commands(lines):
    commands = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line.lower().startswith("repeat "):
            match = re.match(r"repeat (\d+):", line.lower())
            if match:
                count = int(match.group(1))
                i += 1
                block = []
                while i < len(lines) and (lines[i].startswith("  ") or lines[i].startswith("\t")):
                    block.append(lines[i].lstrip())
                    i += 1
                commands.append(("repeat", count, parse_commands(block)))
                continue
        if re.match(r'^if cube \d is tapped:', line.lower()):
            match = re.match(r'^if cube (\d) is tapped:', line.lower())
            cube_number = int(match.group(1))
            i += 1
            block = []
            while i < len(lines) and (lines[i].startswith("  ") or lines[i].startswith("\t")):
                block.append(lines[i].lstrip())
                i += 1
            commands.append(("if_cube_tap", cube_number, parse_commands(block)))
            continue
        if line != "":
            commands.append(("cmd", line))
        i += 1
    return commands

def execute_commands(commands, cozmo):
    for cmd in commands:
        if cmd[0] == "repeat":
            _, count, block = cmd
            for _ in range(count):
                execute_commands(block, cozmo)
        elif cmd[0] == "if_cube_tap":
            _, cube_number, block = cmd
            if cozmo.wait_for_cube_tap(cube_number):
                execute_commands(block, cozmo)
        elif cmd[0] == "cmd":
            line = cmd[1]
            # Use your usual one-line command handler:
            line = line.strip()
            if line.lower().startswith("show emotion "):
                emotion = line.split(" ")[2]
                cozmo.show_emotion(emotion)
            elif line.lower().startswith("say "):
                cozmo.say(line[4:].strip())
            elif line.lower().startswith("go "):
                parts = line.split()
                if len(parts) == 3:
                    cozmo.go(float(parts[1]), float(parts[2]))
            elif line.lower().startswith("turn "):
                parts = line.split()
                if len(parts) == 2:
                    cozmo.turn(float(parts[1]))
            elif line.lower().startswith("hand "):
                parts = line.split()
                if len(parts) == 2:
                    cozmo.hand(float(parts[1]))
            elif line.lower().startswith("head "):
                parts = line.split()
                if len(parts) == 2:
                    cozmo.head(float(parts[1]))
            elif line.lower() == "celebrate":
                cozmo.celebrate()
            elif line.lower() == "light on":
                cozmo.light_on()
            elif line.lower() == "light off":
                cozmo.light_off()
            elif line.lower().startswith("pickup cube"):
                parts = line.split()
                if len(parts) == 3:
                    cozmo.pickup_cube(parts[2])
                else:
                    cozmo.pickup_cube()
            elif line.lower() == "stop":
                cozmo.stop()
                break


@app.post("/run_program")
def run_program(prog: Program):
    lines = prog.program.strip().splitlines()
    commands = parse_commands(lines)
    cozmo.clear_stop()
    execute_commands(commands, cozmo)
    return {"status": "Program executed"}


@app.get("/ping")
def ping():
    return {"status": "ok"}

app.mount("/public", StaticFiles(directory="public"), name="public")

@app.get("/")
def serve_frontend():
    return FileResponse("public/index.html")

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

'''
def parse_when_blocks(lines):
    # Returns: (single_commands, when_blocks)
    single_commands = []
    when_blocks = []  # List of (cube_number, block_commands)
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        m = re.match(r'^when cube (\d) is tapped:', line.lower())
        if m:
            cube_number = int(m.group(1))
            i += 1
            block = []
            while i < len(lines) and (lines[i].startswith("  ") or lines[i].startswith("\t")):
                block.append(lines[i].lstrip())
                i += 1
            when_blocks.append((cube_number, parse_when_blocks(block)[0]))  # recursive parse for block
            continue
        # normal one-liner or repeat/if as before
        if line != "":
            single_commands.append(line)
        i += 1
    return (single_commands, when_blocks)

def run_program_event_driven(code, cozmo):
    lines = code.strip().splitlines()
    single_cmds, when_blocks = parse_when_blocks(lines)

    stop_flag = {"stopped": False}
    threads = []

    # Start threads for each when-cube block
    for cube_number, block in when_blocks:
        t = threading.Thread(target=cozmo.run_when_cube_tapped, args=(cube_number, block, stop_flag), daemon=True)
        t.start()
        threads.append(t)

    # Run single commands (not inside when-cube)
    cozmo._execute_commands(single_cmds, cozmo, stop_flag)

    # Keep main thread alive until stopped
    try:
        while not stop_flag["stopped"]:
            threading.Event().wait(0.5)
    except KeyboardInterrupt:
        stop_flag["stopped"] = True

def stop_all(cozmo, stop_flag):
    stop_flag["stopped"] = True
    cozmo.stop()

'''
