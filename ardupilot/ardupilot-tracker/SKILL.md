# ArduPilot Antenna Tracker Development

This skill provides guidance for developing and modifying the ArduPilot AntennaTracker firmware.

## Overview

AntennaTracker is a ground-based system for automatically pointing a directional antenna at a moving vehicle. It tracks aircraft, drones, and other vehicles using MAVLink telemetry to maintain optimal communication links.

## Source Location

**Main directory**: `AntennaTracker/`

## Key Components

| Component | File(s) | Purpose |
|-----------|---------|---------|
| Main class | `Tracker.h/cpp` | Core tracker logic |
| Modes | `mode.h`, `mode_*.cpp` | 7 operation modes |
| Servos | `servos.cpp` | Pan/tilt servo control |
| Tracking | `tracking.cpp` | Vehicle position tracking |
| Parameters | `Parameters.h/cpp` | Configuration parameters |
| MAVLink | `GCS_MAVLink_Tracker.cpp` | Vehicle communication |

## Operation Modes

| # | Mode | Description |
|---|------|-------------|
| 0 | MANUAL | Direct RC pass-through |
| 1 | STOP | Servos held/zeroed |
| 2 | SCAN | Continuous pan/tilt sweep |
| 3 | SERVOTEST | Servo diagnostics |
| 4 | GUIDED | GCS-commanded pointing |
| 10 | AUTO | Automatic vehicle tracking |
| 16 | INITIALISING | Startup initialization |

## Servo Types

Three servo types are supported:
- **Position (0)**: Standard position servos with PID control
- **On/Off (1)**: Simple on/off control for relay-based systems
- **Continuous Rotation (2)**: CR servos with rate control

## Core Concepts

### Vehicle Tracking
```
MAVLink Position → Bearing/Distance Calc → Target Angles → PID → Servo Output
```

### Coordinate Frames
- **Earth Frame**: Yaw (heading), Pitch (elevation)
- **Body Frame**: Converted for non-level mounting
- Automatic frame conversion handles tracker tilt

### PID Controllers
- `pidPitch2Srv`: Pitch angle to servo
- `pidYaw2Srv`: Yaw angle to servo

## Quick Reference

### Finding Modes
```bash
python .claude/skills/ardupilot-tracker/scripts/find_tracker_modes.py
```

### Finding Parameters
```bash
python .claude/skills/ardupilot-tracker/scripts/tracker_params.py [PREFIX]
python .claude/skills/ardupilot-tracker/scripts/tracker_params.py --subsystem servo
```

### Building for SITL
```bash
./waf configure --board sitl
./waf antennatracker
```

### Running Simulation
```bash
cd Tools/autotest
./sim_vehicle.py -v AntennaTracker --console --map
```

## Reference Documentation

- [Architecture](references/architecture.md) - System design and components
- [Modes](references/modes.md) - Operation mode details
- [Servos](references/servos.md) - Servo control system
- [Tracking](references/tracking.md) - Vehicle tracking algorithms
- [Parameters](references/parameters.md) - Configuration parameters
- [Extending](references/extending.md) - Adding new features

## Common Tasks

### Add a New Mode
1. Add enum value to `mode.h` Number enum
2. Create mode class inheriting from Mode
3. Implement `update()` method
4. Register in `Tracker::mode_from_mode_num()`
5. Add mode instance to Tracker class

### Add a Parameter
1. Add enum in `Parameters.h`
2. Declare variable in Parameters class
3. Define with GSCALAR in `Parameters.cpp`
4. Access via `g.param_name.get()`

### Modify Tracking Behavior
- Edit `tracking.cpp` for position calculation
- Edit `mode.cpp` for angle calculation
- Adjust PID gains via `PITCH2SRV_*` and `YAW2SRV_*` parameters

## Key Parameters

| Parameter | Description |
|-----------|-------------|
| `SYSID_TARGET` | Vehicle MAVLink ID to track |
| `SERVO_YAW_TYPE` | Yaw servo type (0=Pos, 1=OnOff, 2=CR) |
| `SERVO_PITCH_TYPE` | Pitch servo type |
| `YAW_RANGE` | Total yaw movement range (deg) |
| `PITCH_MIN/MAX` | Pitch angle limits (deg) |
| `DISTANCE_MIN` | Minimum tracking distance (m) |
| `INITIAL_MODE` | Startup mode |

## Hardware Configuration

### Servo Channels
- `SERVO5` (default): Yaw (k_tracker_yaw)
- `SERVO6` (default): Pitch (k_tracker_pitch)

### Required Sensors
- Compass for heading reference
- GPS (optional, for location)
- Barometer (optional, for altitude)
