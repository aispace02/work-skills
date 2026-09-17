---
name: ardupilot-rover
description: |
  ArduPilot Rover vehicle development. Use when working with: ground vehicles,
  boats, balance bots, flight modes (Manual, Auto, Guided, RTL, SmartRTL, etc.),
  motor control (AP_MotorsUGV), waypoint navigation (AR_WPNav), steering/throttle
  control, sailboat features, RC input handling, or adding new Rover functionality.
---

# ArduPilot Rover Vehicle

## Reference Lookup

| Topic | Key Files | Reference |
|-------|-----------|-----------|
| Architecture & Main Loop | Rover.h/cpp, system.cpp | [architecture.md](references/architecture.md) |
| Flight Modes | mode.h, mode_*.cpp | [modes.md](references/modes.md) |
| Motor Control | AP_MotorsUGV | [motors.md](references/motors.md) |
| Navigation | AR_WPNav, AR_PosControl | [navigation.md](references/navigation.md) |
| Steering & Throttle | AR_AttitudeControl | [control.md](references/control.md) |
| Parameters | Parameters.h/cpp | [parameters.md](references/parameters.md) |
| MAVLink & GCS | GCS_MAVLink_Rover | [mavlink.md](references/mavlink.md) |
| Sailboat | sailboat.h/cpp | [sailboat.md](references/sailboat.md) |
| Adding Features | Examples & patterns | [extending.md](references/extending.md) |

## Source Locations

```
Rover/                          # Main vehicle directory
├── Rover.h/cpp                 # Main vehicle class, scheduler
├── mode.h/cpp                  # Mode base class, common methods
├── mode_manual.cpp             # Direct RC control
├── mode_auto.cpp               # Mission execution
├── mode_guided.cpp             # External control
├── mode_rtl.cpp                # Return to launch
├── mode_smartrtl.cpp           # Reverse path return
├── mode_steering.cpp           # Heading + speed
├── mode_loiter.cpp             # Position hold
├── mode_hold.cpp               # Stop and hold
├── mode_acro.cpp               # Acrobatic steering
├── mode_circle.cpp             # Circle a point
├── mode_follow.cpp             # Follow vehicle
├── mode_dock.cpp               # Autonomous docking
├── mode_simple.cpp             # Simplified control
├── Parameters.h/cpp            # All parameters
├── GCS_MAVLink_Rover.h/cpp     # MAVLink handling
├── sailboat.h/cpp              # Sailboat support
├── RC_Channel_Rover.h/cpp      # RC input
├── AP_Arming_Rover.h/cpp       # Arming checks
├── Steering.cpp                # Motor output
├── commands.cpp                # Home position
├── failsafe.cpp                # Failsafe handling
├── sensors.cpp                 # Sensor updates
├── Log.cpp                     # Logging
├── system.cpp                  # Init, mode switching
└── defines.h                   # Constants, enums
```

## Key Libraries

| Library | Location | Purpose |
|---------|----------|---------|
| AP_MotorsUGV | `libraries/AP_Motors/` | Motor mixing and output |
| AR_AttitudeControl | `libraries/APM_Control/` | Steering/throttle PID |
| AR_WPNav | `libraries/AR_WPNav/` | Waypoint navigation |
| AR_PosControl | `libraries/APM_Control/` | Position control |
| AP_SmartRTL | `libraries/AP_SmartRTL/` | Path recording/replay |

## Frame Types

| FRAME_CLASS | Value | Description |
|-------------|-------|-------------|
| ROVER | 1 | Land vehicle with steering/throttle |
| BOAT | 2 | Watercraft, supports sailboat |
| BALANCEBOT | 3 | Two-wheel self-balancing |

## Mode Numbers

| Mode | Number | Type |
|------|--------|------|
| MANUAL | 0 | Manual |
| ACRO | 1 | Semi-Auto |
| STEERING | 3 | Semi-Auto |
| HOLD | 4 | Failsafe |
| LOITER | 5 | Autonomous |
| FOLLOW | 6 | Autonomous |
| SIMPLE | 7 | Semi-Auto |
| DOCK | 8 | Autonomous |
| CIRCLE | 9 | Autonomous |
| AUTO | 10 | Autonomous |
| RTL | 11 | Autonomous |
| SMART_RTL | 12 | Autonomous |
| GUIDED | 15 | Autonomous |
| INITIALISING | 16 | Startup |

## Quick Patterns

### Access Rover Singleton
```cpp
Rover &rover = AP::rover();
// Or from mode: rover (already available as reference)
```

### Set Motor Output
```cpp
g2.motors.set_steering(steering);  // -4500 to +4500
g2.motors.set_throttle(throttle);  // -100 to +100
g2.motors.set_lateral(lateral);    // -100 to +100 (boats)
```

### Navigate to Waypoint
```cpp
g2.wp_nav.set_desired_location(dest);
g2.wp_nav.update(rover.G_Dt);
float turn_rate = g2.wp_nav.get_turn_rate_rads();
calc_steering_from_turn_rate(turn_rate);
calc_throttle(g2.wp_nav.get_speed(), true);
```

### Get Pilot Input
```cpp
float steering, throttle;
get_pilot_desired_steering_and_throttle(steering, throttle);
```

## Parameter Prefixes

| Prefix | Subsystem |
|--------|-----------|
| `CRUISE_*` | Cruise speed/throttle |
| `WP_*` | Waypoint navigation |
| `ATC_*` | Attitude control |
| `MOT_*` | Motors |
| `TURN_*` | Turning |
| `FS_*` | Failsafe |
| `SAIL_*` | Sailboat |
| `SIMPLE_*` | Simple mode |
| `CIRC_*` | Circle mode |
| `DOCK_*` | Dock mode |
| `SRTL_*` | SmartRTL |

## Scheduler (400Hz Main Loop)

| Task | Rate | Purpose |
|------|------|---------|
| read_radio | 50Hz | RC input |
| ahrs_update | 400Hz | Attitude |
| update_current_mode | 400Hz | Mode control |
| set_servos | 400Hz | Motor output |
| update_GPS | 50Hz | Position |
| update_compass | 10Hz | Heading |
| failsafe_check | 10Hz | Safety |

## Scripts

- `scripts/find_rover_modes.py` - List all modes and their properties
- `scripts/rover_params.py <mode>` - Find mode-specific parameters
