# Copter Simulation Cheat Sheet

## Quick Start Flight

```bash
# 1. Arm the motors
arm throttle

# 2. Take off to 10 meters
mode GUIDED
takeoff 10

# 3. Fly around (see commands below)

# 4. Land
mode LAND

# 5. Disarm (after landing)
disarm
```

## Flight Modes

| Command | Description |
|---------|-------------|
| `mode STABILIZE` | Manual flight, self-levels |
| `mode ALT_HOLD` | Holds altitude, manual position |
| `mode LOITER` | Holds position and altitude (GPS) |
| `mode GUIDED` | Fly to commanded positions |
| `mode AUTO` | Follow waypoint mission |
| `mode RTL` | Return to launch point |
| `mode LAND` | Land at current position |

## Movement Commands (GUIDED Mode)

```bash
# Fly to GPS coordinates at 50m altitude
guided -35.363 149.165 50

# Fly to relative position (North, East, Down in meters)
# Go 20m North, 10m East, stay at current alt
position 20 10 0

# Set velocity (North, East, Down in m/s)
# Fly North at 5 m/s
velocity 5 0 0

# Change altitude (relative)
takeoff 20    # Go to 20m
```

## RC Stick Simulation

```bash
# RC channels: 1=Roll, 2=Pitch, 3=Throttle, 4=Yaw
# Range: 1000-2000, center=1500

# Throttle up (climb in STABILIZE/ALT_HOLD)
rc 3 1600

# Throttle down
rc 3 1400

# Roll right
rc 1 1600

# Roll left
rc 1 1400

# Pitch forward
rc 2 1400

# Pitch back
rc 2 1600

# Yaw right
rc 4 1600

# Yaw left
rc 4 1400

# Center all sticks
rc 1 1500
rc 2 1500
rc 3 1500
rc 4 1500
```

## Arming & Safety

```bash
# Arm
arm throttle

# Force arm (bypass checks)
arm throttle force

# Disarm
disarm

# Force disarm (emergency)
disarm force

# Check arming status
status HEARTBEAT
```

## Missions

```bash
# Load mission from file
wp load mission.txt

# List waypoints
wp list

# Start mission
mode AUTO

# Jump to waypoint 3
wp set 3

# Pause mission
mode LOITER

# Resume
mode AUTO
```

## Useful Commands

```bash
# Show all parameters
param show *

# Show specific parameter
param show ARMING*

# Set parameter
param set ARMING_CHECK 0

# Get current position
position

# Get altitude
altitude

# Get attitude (roll/pitch/yaw)
attitude

# Get speed
speed

# Get battery
battery

# Status overview
status
```

## Map Controls

- **Left click**: Set GUIDED target
- **Right click**: Context menu
- **Scroll**: Zoom in/out
- **Drag**: Pan map

## Quick Missions

### Circle at Location
```bash
mode GUIDED
takeoff 20
# Click on map to fly there
mode CIRCLE
```

### Return Home
```bash
mode RTL
```

### Hover in Place
```bash
mode LOITER
```

## Emergency

```bash
# Immediate land
mode LAND

# Kill motors (DANGER - drops from sky)
disarm force

# Return home
mode RTL
```

## Simulation Control

```bash
# Speed up simulation
param set SIM_SPEEDUP 5

# Reset to normal speed
param set SIM_SPEEDUP 1

# Pause (in terminal, not MAVProxy)
Ctrl+C  # then restart

# Quit MAVProxy
quit
```

## Example Flight Session

```bash
# Start simulation
python .claude/skills/ardupilot-simulation/scripts/quick_sim.py copter

# In MAVProxy console:
arm throttle
mode GUIDED
takeoff 15
# Wait for altitude...
# Click on map to fly to location
# Or use:
guided -35.362 149.166 15
# Fly around...
mode LOITER          # Hold position
mode RTL             # Go home
# Wait for landing...
disarm
quit
```
