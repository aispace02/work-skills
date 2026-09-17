# MAVProxy Commands

## Overview

MAVProxy is the ground control software launched by sim_vehicle.py. It provides command-line control of the simulated vehicle.

## Basic Commands

### Arming/Disarming

```bash
# Arm
arm throttle

# Force arm (bypass checks)
arm throttle force

# Disarm
disarm

# Force disarm
disarm force
```

### Mode Changes

```bash
# Set mode by name
mode STABILIZE
mode LOITER
mode GUIDED
mode AUTO
mode RTL
mode LAND

# Set mode by number
mode 0   # STABILIZE
mode 5   # LOITER
```

### Takeoff (Copter)

```bash
# Arm and takeoff
arm throttle
mode GUIDED
takeoff 10  # 10 meters
```

### RC Control

```bash
# Set RC channel (1000-2000)
rc 1 1500  # Roll
rc 2 1500  # Pitch
rc 3 1500  # Throttle
rc 4 1500  # Yaw
```

## Parameter Commands

### View Parameters

```bash
# Show all parameters
param show *

# Show specific parameter
param show ARMING_CHECK

# Pattern matching
param show ARMING*
param show *GPS*
```

### Set Parameters

```bash
# Set parameter
param set ARMING_CHECK 0

# Set and save
param set ARMING_CHECK 0
param save
```

### Parameter Files

```bash
# Save to file
param save my_params.parm

# Load from file
param load my_params.parm

# Diff against defaults
param diff
```

## Mission Commands

### Load/Save Missions

```bash
# Load waypoints
wp load mission.txt

# Save waypoints
wp save current_mission.txt

# List waypoints
wp list
```

### Mission Control

```bash
# Start mission
mode AUTO

# Set current waypoint
wp set 3

# Clear mission
wp clear
```

### Create Waypoints

```bash
# Add waypoint at current location
wp add

# Set home
wp sethome
```

## Guided Mode Commands

### Fly to Location

```bash
mode GUIDED

# Fly to GPS coordinates
guided LAT LON ALT
guided -35.363261 149.165230 50

# Fly to relative position
guided_posvel N E D
```

### Position Hold

```bash
mode GUIDED
position 0 0 0  # Hold current position
```

## Geofence Commands

```bash
# Load fence
fence load fence.txt

# Enable fence
fence enable

# Disable fence
fence disable

# List fence points
fence list
```

## Rally Points

```bash
# Load rally points
rally load rally.txt

# List rally points
rally list
```

## Logging

### Start/Stop Logging

```bash
# Logs are automatic, but you can control:
log list
log download 1
```

## Graphing

### Load Graph Module

```bash
module load graph
```

### Graph Values

```bash
# Graph RC input
graph RC_CHANNELS.chan3_raw

# Graph attitude
graph ATTITUDE.roll ATTITUDE.pitch

# Multiple values
graph VFR_HUD.airspeed VFR_HUD.groundspeed
```

### Graph Aliases

Common aliases (from `~/.mavinit.scr`):
```bash
graph altitude  # Graph altitude
graph rc        # Graph RC channels
```

## Modules

### Load Modules

```bash
module load console
module load map
module load graph
module load joystick
module load tracker
module load cesium
```

### List Modules

```bash
module list
```

## Output Forwarding

```bash
# Add UDP output
output add 192.168.1.100:14550

# Add serial output
output add /dev/ttyUSB0:57600

# List outputs
output list

# Remove output
output remove 192.168.1.100:14550
```

## Status Commands

```bash
# Vehicle status
status

# GPS status
gps

# Battery status
battery

# Sensor status
sensors

# System status
status HEARTBEAT
```

## Scripting

### Run Script

```bash
script my_script.scr
```

Script file format:
```bash
# my_script.scr
arm throttle
mode GUIDED
takeoff 10
delay 5
mode LOITER
```

### Aliases

Create in `~/.mavinit.scr`:
```bash
alias arm "arm throttle"
alias takeoff10 "mode GUIDED; takeoff 10"
```

## Keyboard Shortcuts

In console:
- `Ctrl+C` - Quit
- `Tab` - Autocomplete
- `Up/Down` - Command history

## Watch Expressions

```bash
# Watch parameter continuously
watch VFR_HUD.alt
watch ATTITUDE

# Stop watching
nowatch
```

## Message Rates

```bash
# Set message rate
set streamrate 10

# Set specific stream
set streamrate-position 10
```

## MAVProxy Configuration

### Init Script

`~/.mavinit.scr`:
```bash
# Load modules
module load console
module load map
module load graph

# Set defaults
set moddebug 0
set streamrate 10

# Define aliases
alias arm "arm throttle"
alias land "mode LAND"
```

### Environment Variables

```bash
# Map service
export MAP_SERVICE="MicrosoftHyb"

# Console settings
export MAVPROXY_CONSOLE=1
```

## Vehicle-Specific Commands

### Copter

```bash
mode STABILIZE
mode ALT_HOLD
mode LOITER
mode GUIDED
mode AUTO
mode RTL
mode LAND
takeoff 10
```

### Plane

```bash
mode MANUAL
mode STABILIZE
mode FBWA
mode FBWB
mode CRUISE
mode AUTO
mode RTL
mode LOITER
```

### Rover

```bash
mode MANUAL
mode STEERING
mode HOLD
mode AUTO
mode GUIDED
mode RTL
```

### Sub

```bash
mode MANUAL
mode STABILIZE
mode DEPTH_HOLD
mode GUIDED
mode AUTO
dive 10
surface
```

## Multi-Vehicle

```bash
# Select vehicle
vehicle 1
vehicle 2

# Send to specific vehicle
sysid 1 arm throttle

# Broadcast to all
alllinks arm throttle
```
