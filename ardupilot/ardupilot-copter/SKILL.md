# ArduCopter Development Skill

Expert guidance for developing with ArduPilot's multicopter/helicopter platform.

## Quick Reference

### Key Source Locations

```
ArduCopter/
├── Copter.h                    # Main vehicle class
├── Copter.cpp                  # Main loop and scheduler
├── mode.h                      # Mode base class and all mode definitions
├── mode_*.cpp                  # Individual mode implementations
├── Attitude.cpp                # Attitude control helpers
├── crash_check.cpp             # Crash and thrust loss detection
├── ekf_check.cpp               # EKF failsafe checking
├── events.cpp                  # Failsafe event handling
├── failsafe.cpp                # Failsafe enable/disable
├── land_detector.cpp           # Landing detection
├── Parameters.h/cpp            # Parameter definitions
├── autoyaw.cpp                 # AutoYaw controller
├── GCS_MAVLink_Copter.cpp      # MAVLink message handling
└── heli.cpp                    # Traditional helicopter support

libraries/
├── AC_AttitudeControl/         # Attitude controllers
│   ├── AC_AttitudeControl_Multi.h  # Multicopter attitude
│   └── AC_AttitudeControl_Heli.h   # Helicopter attitude
├── AC_PosControl/              # Position controller
├── AC_WPNav/                   # Waypoint navigation
│   ├── AC_WPNav.h              # Waypoint navigation
│   ├── AC_Loiter.h             # Loiter control
│   └── AC_Circle.h             # Circle navigation
├── AP_Motors/                  # Motor output
│   ├── AP_MotorsMulticopter.h  # Multicopter motors
│   └── AP_MotorsHeli.h         # Helicopter motors
└── AP_SmartRTL/                # Smart RTL path tracking
```

### Flight Modes

| Mode | Number | GPS | Throttle | Autopilot | Description |
|------|--------|-----|----------|-----------|-------------|
| STABILIZE | 0 | No | Manual | No | Attitude stabilized |
| ACRO | 1 | No | Manual | No | Rate control |
| ALT_HOLD | 2 | No | Auto | No | Altitude hold |
| AUTO | 3 | Yes | Auto | Yes | Mission execution |
| GUIDED | 4 | Yes | Auto | Yes | GCS-commanded |
| LOITER | 5 | Yes | Auto | No | Position hold |
| RTL | 6 | Yes | Auto | Yes | Return to launch |
| CIRCLE | 7 | Yes | Auto | Yes | Circle around point |
| LAND | 9 | No | Auto | Yes | Automatic landing |
| DRIFT | 11 | Yes | Auto | No | Semi-auto position/yaw |
| SPORT | 13 | No | Auto | No | Earth-frame rate control |
| FLIP | 14 | No | Auto | No | Acrobatic flip |
| AUTOTUNE | 15 | No | Auto | No | Auto-tune PID gains |
| POSHOLD | 16 | Yes | Auto | No | Position hold + brake |
| BRAKE | 17 | Yes | Auto | Yes | Emergency stop |
| THROW | 18 | Yes | Auto | No | Throw to launch |
| AVOID_ADSB | 19 | Yes | Auto | Yes | ADSB avoidance |
| GUIDED_NOGPS | 20 | No | Auto | Yes | Guided without GPS |
| SMART_RTL | 21 | Yes | Auto | Yes | Retrace path home |
| FLOWHOLD | 22 | No | Auto | No | Optical flow hold |
| FOLLOW | 23 | Yes | Auto | Yes | Follow another vehicle |
| ZIGZAG | 24 | Yes | Auto | Yes | Zigzag pattern flight |
| SYSTEMID | 25 | No | Manual | No | System identification |
| AUTOROTATE | 26 | No | Auto | Yes | Heli autorotation |
| TURTLE | 28 | No | Manual | No | Flip over after crash |

### Frame Types

| Type | Description |
|------|-------------|
| MULTICOPTER_FRAME | Quad, Hexa, Octa, etc. |
| HELI_FRAME | Traditional helicopter |

### Control Architecture

```
Pilot Input (RC/GCS)
         │
         ▼
    Simple/Super-Simple Mode Transform
         │
         ▼
    Mode Logic
         │
    ┌────┴────┐
    ▼         ▼
Attitude   Position
Control    Control
(AC_AttitudeControl)  (AC_PosControl)
    │         │
    └────┬────┘
         ▼
    Motor Mixing
    (AP_Motors)
         │
         ▼
    PWM Output
```

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ANGLE_MAX` | Max lean angle (centideg) | 3000 |
| `PILOT_SPEED_UP` | Max climb rate (cm/s) | 250 |
| `PILOT_SPEED_DN` | Max descent rate (cm/s) | 150 |
| `PILOT_ACCEL_Z` | Vertical acceleration (cm/s/s) | 250 |
| `PILOT_TKOFF_ALT` | Takeoff altitude (cm) | 0 (disabled) |
| `WPNAV_SPEED` | Horizontal speed (cm/s) | 500 |
| `WPNAV_SPEED_UP` | Climb speed (cm/s) | 250 |
| `WPNAV_SPEED_DN` | Descent speed (cm/s) | 150 |
| `FS_THR_ENABLE` | Radio failsafe action | 1 (RTL) |
| `FS_GCS_ENABLE` | GCS failsafe action | 0 (disabled) |
| `FS_EKF_ACTION` | EKF failsafe action | 1 (Land) |

## Detailed Documentation

- [Architecture Overview](references/architecture.md)
- [Flight Modes](references/modes.md)
- [Attitude Control](references/attitude-control.md)
- [Position Control](references/position-control.md)
- [Motor Configuration](references/motors.md)
- [Failsafe Systems](references/failsafe.md)
- [Parameters](references/parameters.md)
- [Extending ArduCopter](references/extending.md)

## Helper Scripts

- `scripts/find_copter_modes.py` - List all modes and properties
- `scripts/copter_params.py` - Find parameters by prefix/subsystem

## Common Development Tasks

### Adding a New Mode

1. Define mode number in `mode.h` enum
2. Create mode class in `mode.h`
3. Implement in `mode_<name>.cpp`
4. Add instance to `Copter.h`
5. Register in `mode.cpp` `mode_from_mode_num()`

### Adding a Parameter

```cpp
// Parameters.h
k_param_my_param = 250,  // Pick unused number

// In Parameters class
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
./waf copter
cd Tools/autotest
./sim_vehicle.py -v ArduCopter --console --map
```

## Copter-Specific Features

### Simple/Super-Simple Mode

Simplifies pilot orientation:
- **Simple**: Forward is always the heading at arm time
- **Super-Simple**: Forward is always toward home

```cpp
void update_simple_mode();
void update_super_simple_bearing(bool force_update);
```

### Air Mode

Allows full attitude control at zero throttle:

```cpp
enum class AirMode {
    AIRMODE_NONE,      // Not configured
    AIRMODE_DISABLED,  // Disabled
    AIRMODE_ENABLED,   // Full authority at zero throttle
};
```

### Throw Mode

Launch by throwing:
- Detects free-fall
- Stabilizes vehicle
- Transitions to position hold

### Precision Landing

Land on visual targets:

```cpp
#if AC_PRECLAND_ENABLED
    AC_PrecLand precland;
    AC_PrecLand_StateMachine precland_statemachine;
#endif
```

### Parachute

Emergency parachute release:

```cpp
#if HAL_PARACHUTE_ENABLED
    AP_Parachute parachute;
#endif
```

### Auto Yaw Modes

```cpp
enum class Mode {
    HOLD,              // Hold current yaw
    LOOK_AT_NEXT_WP,   // Face next waypoint
    ROI,               // Look at region of interest
    FIXED,             // Fixed heading
    LOOK_AHEAD,        // Face direction of travel
    RESET_TO_ARMED_YAW,// Face arming heading
    ANGLE_RATE,        // Turn at rate from angle
    RATE,              // Turn at fixed rate
    CIRCLE,            // Use circle nav yaw
    PILOT_RATE,        // Pilot controls rate
    WEATHERVANE,       // Yaw into wind
};
```
