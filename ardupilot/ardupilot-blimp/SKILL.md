# Blimp Development Skill

Expert guidance for developing with ArduPilot's blimp/airship platform.

## Quick Reference

### Key Source Locations

```
Blimp/
├── Blimp.h                     # Main vehicle class
├── Blimp.cpp                   # Main loop and scheduler
├── mode.h                      # Mode base class and definitions
├── mode_*.cpp                  # Individual mode implementations
├── Fins.h/cpp                  # Fin/actuator control (oscillating fins)
├── Loiter.h/cpp                # Position/velocity controller
├── Parameters.h/cpp            # Parameter definitions
├── events.cpp                  # Failsafe event handling
├── failsafe.cpp                # Failsafe enable/disable
├── ekf_check.cpp               # EKF failsafe checking
├── GCS_MAVLink_Blimp.cpp       # MAVLink message handling
└── radio.cpp                   # RC input handling
```

### Flight Modes

| Mode | Number | GPS | Manual | Description |
|------|--------|-----|--------|-------------|
| LAND | 0 | No | Yes | Stops movement (failsafe) |
| MANUAL | 1 | No | Yes | Direct fin control |
| VELOCITY | 2 | Yes | No | Velocity-based control |
| LOITER | 3 | Yes | No | Position hold |
| RTL | 4 | Yes | No | Return to launch |

### Control Architecture

Blimp uses oscillating fins rather than traditional motors/propellers:

```
Pilot Input (RC)
         │
         ▼
    Mode Logic
         │
    ┌────┴────┐
    ▼         ▼
Position   Velocity
  PIDs       PIDs
    │         │
    └────┬────┘
         ▼
    Fin Output
   (right, front,
    down, yaw)
         │
         ▼
  Sine Wave Generator
  (amplitude + offset)
         │
         ▼
    Servo PWM
```

### Input Channels

| Channel | Function | Range |
|---------|----------|-------|
| Right | Lateral movement | -1 to +1 |
| Front | Forward/backward | -1 to +1 |
| Up | Vertical (down positive) | -1 to +1 |
| Yaw | Rotation | -1 to +1 |

### Fin Configuration

4 fins with amplitude and offset control:

```
Fin 0 (Back):  Front amp, Down amp+off
Fin 1 (Front): -Front amp, Down amp+off
Fin 2 (Right): -Right amp, Yaw amp+off
Fin 3 (Left):  Right amp, -Yaw amp+off
```

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `FINS_FREQ_HZ` | Fin oscillation frequency | 3 Hz |
| `FINS_TURBO_MODE` | Double speed on high offset | 0 |
| `MAX_VEL_XY` | Max horizontal velocity (m/s) | - |
| `MAX_VEL_Z` | Max vertical velocity (m/s) | - |
| `MAX_VEL_YAW` | Max yaw rate (rad/s) | - |
| `MAX_POS_XY` | Max position offset (m) | - |
| `MAX_POS_Z` | Max vertical offset (m) | - |
| `MAX_POS_YAW` | Max yaw offset (rad) | - |
| `SIMPLE_MODE` | Simple mode enable | 0 |
| `DIS_MASK` | Axis disable mask | 0 |
| `PID_DZ` | PID deadzone | - |

## Detailed Documentation

- [Architecture Overview](references/architecture.md)
- [Flight Modes](references/modes.md)
- [Fin Control System](references/fins.md)
- [Position/Velocity Control](references/loiter.md)
- [Parameters](references/parameters.md)
- [Extending Blimp](references/extending.md)

## Helper Scripts

- `scripts/find_blimp_modes.py` - List all modes and properties
- `scripts/blimp_params.py` - Find parameters by prefix

## Common Development Tasks

### Adding a New Mode

1. Define mode number in `mode.h` enum
2. Create mode class in `mode.h`
3. Implement in `mode_<name>.cpp`
4. Add instance to `Blimp.h`
5. Register in `mode.cpp` `mode_from_mode_num()`

### Adding a Parameter

```cpp
// Parameters.h - add enum
k_param_my_param = 250,

// Parameters class - add variable
AP_Float my_param;

// Parameters.cpp - add definition
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
./waf blimp
cd Tools/autotest
./sim_vehicle.py -v Blimp --console --map
```

## Blimp-Specific Features

### Oscillating Fin System

Unlike multicopters with spinning propellers, Blimp uses oscillating fins:

```cpp
// Fin output combines amplitude and offset
_pos[i] = _amp[i] * cosf(freq_hz * _time * 2 * M_PI) + _off[i];
```

- **Amplitude**: Controls thrust magnitude (how hard the fin flaps)
- **Offset**: Controls average position (directional bias)
- **Frequency**: Oscillation rate (default 3 Hz)

### Turbo Mode

When offset is high and amplitude is low, fin frequency doubles:

```cpp
if (_amp[i] <= 0.6 && fabsf(_off[i]) >= 0.4) {
    _freq[i] = 2;  // Double frequency
}
```

### Simple Mode

When enabled, pilot input is in earth frame (north/east) rather than body frame.

### Cascaded PID Control

Position mode uses cascaded PIDs:
1. Position PID -> Target velocity
2. Velocity PID -> Fin output

### Vector4b Axis Control

Each axis (x, y, z, yaw) can be independently enabled/disabled:

```cpp
struct Vector4b {
    bool x;    // Forward/backward
    bool y;    // Right/left
    bool z;    // Up/down
    bool yaw;  // Rotation
};
```

### Disable Mask

Individual axes can be disabled via `DIS_MASK` parameter:
- Bit 0: Y axis (right/left)
- Bit 1: X axis (front/back)
- Bit 2: Z axis (up/down)
- Bit 3: Yaw axis
