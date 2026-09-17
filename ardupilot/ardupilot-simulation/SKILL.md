# ArduPilot Simulation (SITL)

This skill provides comprehensive guidance for running ArduPilot simulations using SITL (Software In The Loop) and external simulators.

## Overview

SITL allows running ArduPilot firmware on a PC without hardware. The autopilot code is compiled as a native executable, enabling testing, debugging, and development without physical vehicles.

## Quick Start

### Basic Simulation

```bash
# From ArduPilot root directory
cd Tools/autotest

# Run Copter simulation with console and map
sim_vehicle.py -v ArduCopter --console --map

# Run Plane simulation
sim_vehicle.py -v ArduPlane --console --map

# Run Rover simulation
sim_vehicle.py -v Rover --console --map

# Run Sub simulation
sim_vehicle.py -v ArduSub --console --map
```

### Wipe Parameters (First Run)

```bash
sim_vehicle.py -v ArduCopter --console --map -w
```

## Supported Vehicles

| Vehicle | Command | Default Frame |
|---------|---------|---------------|
| ArduCopter | `-v ArduCopter` | quad |
| ArduPlane | `-v ArduPlane` | plane |
| Rover | `-v Rover` | rover |
| ArduSub | `-v ArduSub` | vectored |
| Blimp | `-v Blimp` | Blimp |
| AntennaTracker | `-v AntennaTracker` | tracker |
| Helicopter | `-v Helicopter` | heli |

## Common sim_vehicle.py Options

### Essential Options

| Option | Description |
|--------|-------------|
| `-v VEHICLE` | Vehicle type (ArduCopter, ArduPlane, Rover, etc.) |
| `-f FRAME` | Frame type (quad, hexa, plane, quadplane, etc.) |
| `--console` | Open MAVProxy console |
| `--map` | Open map window |
| `-w` | Wipe EEPROM parameters |
| `-L LOCATION` | Start location from locations.txt |
| `-l LAT,LON,ALT,HDG` | Custom start location |

### Build Options

| Option | Description |
|--------|-------------|
| `-N` | No rebuild (use existing binary) |
| `-D` | Debug build |
| `-c` | Clean before building |
| `-j N` | Number of build jobs |

### Simulation Options

| Option | Description |
|--------|-------------|
| `-S SPEED` | Speedup factor (default: 1) |
| `-I N` | Instance number (for multiple vehicles) |
| `-n COUNT` | Number of vehicle instances |
| `--auto-sysid` | Auto-assign MAV_SYSID per instance |
| `--mcast` | Use multicast for multi-vehicle |

### Debug Options

| Option | Description |
|--------|-------------|
| `-G` | Run with GDB |
| `-g` | GDB stopped at start |
| `-V` | Run with Valgrind |
| `--strace` | Run with strace |

## Frame Types

### Copter Frames
```bash
# Quadcopter (default)
sim_vehicle.py -v ArduCopter -f quad

# Hexacopter
sim_vehicle.py -v ArduCopter -f hexa

# Octocopter
sim_vehicle.py -v ArduCopter -f octa

# Y6
sim_vehicle.py -v ArduCopter -f y6

# Tricopter
sim_vehicle.py -v ArduCopter -f tri

# Traditional helicopter
sim_vehicle.py -v ArduCopter -f heli
```

### Plane Frames
```bash
# Standard plane
sim_vehicle.py -v ArduPlane -f plane

# QuadPlane
sim_vehicle.py -v ArduPlane -f quadplane

# Tailsitter
sim_vehicle.py -v ArduPlane -f plane-tailsitter

# Glider
sim_vehicle.py -v ArduPlane -f glider
```

### Rover Frames
```bash
# Standard rover
sim_vehicle.py -v Rover -f rover

# Skid steering
sim_vehicle.py -v Rover -f rover-skid

# Boat
sim_vehicle.py -v Rover -f motorboat

# Sailboat
sim_vehicle.py -v Rover -f sailboat

# Balance bot
sim_vehicle.py -v Rover -f balancebot
```

## Locations

Use predefined locations from `Tools/autotest/locations.txt`:

```bash
# CMAC (default)
sim_vehicle.py -v ArduCopter -L CMAC

# San Francisco Bay
sim_vehicle.py -v ArduCopter -L SFO_Bay

# Custom location
sim_vehicle.py -v ArduCopter -l 37.6256,-122.3324,0,90
```

## Multi-Vehicle Simulation

```bash
# 5 copters with auto system IDs
sim_vehicle.py -v ArduCopter --count 5 --auto-sysid --mcast -L CMAC

# Spaced along a line
sim_vehicle.py -v ArduCopter --count 5 --auto-sysid --mcast \
    -L CMAC --auto-offset-line 90,10
```

## External Simulators

| Simulator | Frame Option | Notes |
|-----------|--------------|-------|
| Gazebo | `gazebo-iris`, `gazebo-zephyr` | Best for robotics/ROS |
| X-Plane | `xplane` | Commercial flight sim |
| RealFlight | `flightaxis:IP` | Windows only |
| AirSim | `airsim-copter`, `airsim-rover` | Unreal Engine based |
| JSBSim | `jsbsim` | Open source physics |
| FlightGear | `--enable-fgview` | 3D visualization |

## MAVProxy Commands

Once simulation is running:

```bash
# Arm vehicle
arm throttle

# Set mode
mode GUIDED
mode LOITER
mode AUTO

# Takeoff (Copter)
takeoff 10

# Load mission
wp load mission.txt

# Start mission
mode AUTO

# Parameter commands
param show ARMING*
param set ARMING_CHECK 0
```

## Helper Scripts

```bash
# List available frames for a vehicle
python .claude/skills/ardupilot-simulation/scripts/list_frames.py ArduCopter

# List available locations
python .claude/skills/ardupilot-simulation/scripts/list_locations.py

# Quick simulation launcher
python .claude/skills/ardupilot-simulation/scripts/quick_sim.py copter
```

## Reference Documentation

- [Getting Started](references/getting-started.md) - Installation and setup
- [sim_vehicle.py Reference](references/sim-vehicle.md) - Complete options guide
- [Frames](references/frames.md) - All vehicle frame types
- [Locations](references/locations.md) - Start location configuration
- [Multi-Vehicle](references/multi-vehicle.md) - Swarm simulation
- [External Simulators](references/external-sims.md) - Gazebo, AirSim, etc.
- [Debugging](references/debugging.md) - GDB, Valgrind, testing
- [MAVProxy](references/mavproxy.md) - Ground station commands

## Troubleshooting

### Build Fails
```bash
# Clean and rebuild
sim_vehicle.py -v ArduCopter -c --console --map
```

### Map Not Loading
```bash
# Set map service
export MAP_SERVICE="MicrosoftHyb"
```

### Connection Issues
```bash
# Check if ports are in use
netstat -tulpn | grep 5760

# Kill stale processes
pkill -f arducopter
pkill -f mavproxy
```

### Update Dependencies
```bash
pip install --upgrade pymavlink MAVProxy --user
```
