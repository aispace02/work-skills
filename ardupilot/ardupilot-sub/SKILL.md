# ArduSub Development Skill

Expert guidance for developing with ArduPilot's submarine/ROV platform.

## Quick Reference

### Key Source Locations

```
ArduSub/
├── Sub.h                    # Main vehicle class
├── Sub.cpp                  # Main loop and scheduler
├── mode.h                   # Mode base class and definitions
├── mode_*.cpp               # Individual mode implementations
├── motors.cpp               # Thruster output handling
├── joystick.cpp             # Gamepad/joystick input
├── failsafe.cpp             # Failsafe handling
├── Parameters.h/cpp         # Parameter definitions
├── surface_bottom_detector.cpp  # Surface/bottom detection
├── GCS_MAVLink_Sub.cpp      # MAVLink message handling
└── commands_logic.cpp       # Mission command execution

libraries/
├── AP_Motors/AP_Motors6DOF.h/cpp  # 6DOF thruster mixing
├── AC_AttitudeControl/AC_AttitudeControl_Sub.h  # Sub-specific attitude control
└── AP_JSButton/AP_JSButton.h  # Joystick button configuration
```

### Flight Modes

| Mode | Number | GPS | Depth | Description |
|------|--------|-----|-------|-------------|
| MANUAL | 19 | No | No | Direct thruster control |
| STABILIZE | 0 | No | No | Attitude stabilized, manual throttle |
| ACRO | 1 | No | No | Rate-based attitude control |
| ALT_HOLD | 2 | No | Yes | Depth hold with attitude stabilization |
| POSHOLD | 16 | Yes | Yes | 3D position hold |
| AUTO | 3 | Yes | Yes | Waypoint mission execution |
| GUIDED | 4 | Yes | Yes | GCS-commanded position/velocity |
| CIRCLE | 7 | Yes | Yes | Circular path around point |
| SURFACE | 9 | No | No | Ascend to surface |
| MOTOR_DETECT | 20 | No | No | Automatic motor detection |
| SURFTRAK | 21 | No | Yes | Rangefinder-based terrain following |

### Frame Types (FRAME_CONFIG)

| Value | Type | Motors | Description |
|-------|------|--------|-------------|
| 0 | SUB_FRAME_BLUEROV1 | 6 | Original BlueROV |
| 1 | SUB_FRAME_VECTORED | 6 | BlueROV2 vectored |
| 2 | SUB_FRAME_VECTORED_6DOF | 8 | Full 6DOF control |
| 3 | SUB_FRAME_VECTORED_6DOF_90DEG | 8 | 6DOF 90-degree layout |
| 4 | SUB_FRAME_SIMPLEROV_3 | 3 | 3-motor simple ROV |
| 5 | SUB_FRAME_SIMPLEROV_4 | 4 | 4-motor simple ROV |
| 6 | SUB_FRAME_SIMPLEROV_5 | 5 | 5-motor simple ROV |
| 7 | SUB_FRAME_CUSTOM | - | Custom configuration |

### Control Architecture

```
Pilot Input (Joystick/RC)
         │
         ▼
    Gain Scaling
         │
         ▼
    Mode Logic
         │
    ┌────┴────┐
    ▼         ▼
Attitude   Position
Control    Control
    │         │
    └────┬────┘
         ▼
    Thruster Mixing
    (AP_Motors6DOF)
         │
         ▼
    PWM Output
```

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `FRAME_CONFIG` | Frame type | 1 |
| `SURFACE_DEPTH` | Surface detection depth (cm) | -10 |
| `JS_GAIN_DEFAULT` | Default pilot gain | 0.5 |
| `JS_GAIN_MIN` | Minimum gain | 0.25 |
| `JS_GAIN_MAX` | Maximum gain | 1.0 |
| `PILOT_SPEED_UP` | Max ascent rate (cm/s) | 100 |
| `PILOT_SPEED_DN` | Max descent rate (cm/s) | 100 |
| `FS_LEAK_ENABLE` | Leak failsafe | 1 |
| `FS_PRESS_ENABLE` | Pressure failsafe | 1 |
| `FS_TEMP_ENABLE` | Temperature failsafe | 1 |

## Detailed Documentation

- [Architecture Overview](references/architecture.md)
- [Flight Modes](references/modes.md)
- [Depth Control](references/depth-control.md)
- [Thruster Configuration](references/thrusters.md)
- [Joystick Control](references/joystick.md)
- [Failsafe Systems](references/failsafe.md)
- [Parameters](references/parameters.md)
- [Extending ArduSub](references/extending.md)

## Helper Scripts

- `scripts/find_sub_modes.py` - List all modes and properties
- `scripts/sub_params.py` - Find parameters by prefix/subsystem

## Common Development Tasks

### Adding a New Mode

1. Define mode number in `mode.h` enum
2. Create mode class in `mode.h`
3. Implement in `mode_<name>.cpp`
4. Add instance to `Sub.h`
5. Register in `mode.cpp` `mode_from_mode_num()`

### Adding a Parameter

```cpp
// Parameters.h
AP_Float my_param;

// Parameters.cpp
// @Param: MY_PARAM
// @DisplayName: My Parameter
// @Description: Description here
// @Range: 0 100
GSCALAR(my_param, "MY_PARAM", 50.0f),

// Usage
float val = g.my_param.get();
```

### Running SITL

```bash
./waf configure --board sitl
./waf sub
cd Tools/autotest
./sim_vehicle.py -v ArduSub --console --map
```

## Sub-Specific Features

### 6 Degrees of Freedom

ArduSub controls motion in all 6 axes:
- **Surge** (forward/backward): `channel_forward`
- **Sway** (left/right): `channel_lateral`
- **Heave** (up/down): `channel_throttle`
- **Roll**: `channel_roll`
- **Pitch**: `channel_pitch`
- **Yaw**: `channel_yaw`

### Depth Sensor

Uses barometer as depth sensor (pressure-based):
- Detected at boot: `ap.depth_sensor_present`
- Health checked: `sensor_health.depth`
- Required for ALT_HOLD and position modes

### Surface/Bottom Detection

- `ap.at_surface`: True when above `SURFACE_DEPTH`
- `ap.at_bottom`: True when throttle limit hit at bottom
- Auto-detected based on velocity and throttle limits

### Leak Detection

- Multiple leak sensors supported
- Configurable failsafe actions
- Logged and reported to GCS
