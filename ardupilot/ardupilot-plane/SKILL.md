---
name: ardupilot-plane
description: |
  ArduPilot Plane (fixed-wing aircraft) development. Use when working with:
  flight modes (Manual, FBWA, FBWB, Cruise, Auto, RTL, Loiter, etc.),
  TECS (altitude/speed control), L1 navigation, automatic takeoff/landing,
  QuadPlane/VTOL support, autotune, or adding new Plane functionality.
---

# ArduPilot Plane (Fixed-Wing Aircraft)

## Reference Lookup

| Topic | Key Files | Reference |
|-------|-----------|-----------|
| Architecture & Main Loop | Plane.h/cpp | [architecture.md](references/architecture.md) |
| Flight Modes | mode.h, mode_*.cpp | [modes.md](references/modes.md) |
| TECS Controller | AP_TECS | [tecs.md](references/tecs.md) |
| L1 Navigation | AP_L1_Control | [navigation.md](references/navigation.md) |
| Attitude Control | APM_Control | [attitude.md](references/attitude.md) |
| Takeoff & Landing | takeoff.cpp, landing | [takeoff-landing.md](references/takeoff-landing.md) |
| QuadPlane/VTOL | quadplane.h/cpp | [quadplane.md](references/quadplane.md) |
| Parameters | Parameters.h/cpp | [parameters.md](references/parameters.md) |
| Extending | Examples & patterns | [extending.md](references/extending.md) |

## Source Locations

```
ArduPlane/                      # Main vehicle directory
├── Plane.h/cpp                 # Main vehicle class, scheduler
├── mode.h/cpp                  # Mode base class
├── mode_manual.cpp             # Direct RC control
├── mode_stabilize.cpp          # Level flight assist
├── mode_fbwa.cpp               # Fly-By-Wire A (roll/pitch stabilized)
├── mode_fbwb.cpp               # Fly-By-Wire B (altitude hold)
├── mode_cruise.cpp             # Heading + altitude hold
├── mode_auto.cpp               # Mission execution
├── mode_guided.cpp             # External control
├── mode_rtl.cpp                # Return to launch
├── mode_loiter.cpp             # Circle at point
├── mode_circle.cpp             # Circle mode
├── mode_acro.cpp               # Aerobatic mode
├── mode_training.cpp           # Training mode
├── mode_autotune.cpp           # Auto PID tuning
├── mode_takeoff.cpp            # Automatic takeoff
├── mode_autoland.cpp           # Automatic landing
├── mode_thermal.cpp            # Thermal soaring
├── mode_qstabilize.cpp         # QuadPlane stabilize
├── mode_qhover.cpp             # QuadPlane hover
├── mode_qloiter.cpp            # QuadPlane loiter
├── mode_qland.cpp              # QuadPlane land
├── mode_qrtl.cpp               # QuadPlane RTL
├── quadplane.h/cpp             # QuadPlane VTOL support
├── tiltrotor.h                 # Tiltrotor support
├── tailsitter.h                # Tailsitter support
├── Parameters.h/cpp            # All parameters
├── GCS_MAVLink_Plane.h/cpp     # MAVLink handling
├── Attitude.cpp                # Attitude stabilization
├── altitude.cpp                # Altitude control
├── commands_logic.cpp          # Mission command handlers
├── failsafe.cpp                # Failsafe handling
├── takeoff.cpp                 # Takeoff logic
├── Log.cpp                     # Logging
└── defines.h                   # Constants, enums
```

## Key Libraries

| Library | Location | Purpose |
|---------|----------|---------|
| AP_TECS | `libraries/AP_TECS/` | Total Energy Control (alt/speed) |
| AP_L1_Control | `libraries/AP_L1_Control/` | Lateral navigation |
| AP_RollController | `libraries/APM_Control/` | Roll PID |
| AP_PitchController | `libraries/APM_Control/` | Pitch PID |
| AP_YawController | `libraries/APM_Control/` | Yaw damper |
| AP_Landing | `libraries/AP_Landing/` | Landing approach |
| AP_Soaring | `libraries/AP_Soaring/` | Thermal detection |

## Mode Numbers

| Mode | Number | Type | Description |
|------|--------|------|-------------|
| MANUAL | 0 | Manual | Direct RC passthrough |
| CIRCLE | 1 | Auto | Circle at location |
| STABILIZE | 2 | Assisted | Level flight |
| TRAINING | 3 | Assisted | Training mode |
| ACRO | 4 | Manual | Aerobatic |
| FLY_BY_WIRE_A | 5 | Assisted | Roll/pitch stabilized |
| FLY_BY_WIRE_B | 6 | Assisted | Altitude hold |
| CRUISE | 7 | Assisted | Heading + altitude |
| AUTOTUNE | 8 | Auto | PID auto-tuning |
| AUTO | 10 | Auto | Mission execution |
| RTL | 11 | Auto | Return to launch |
| LOITER | 12 | Auto | Circle and hold |
| TAKEOFF | 13 | Auto | Automatic takeoff |
| AVOID_ADSB | 14 | Auto | ADSB avoidance |
| GUIDED | 15 | Auto | External control |
| QSTABILIZE | 17 | VTOL | QuadPlane stabilize |
| QHOVER | 18 | VTOL | QuadPlane hover |
| QLOITER | 19 | VTOL | QuadPlane loiter |
| QLAND | 20 | VTOL | QuadPlane land |
| QRTL | 21 | VTOL | QuadPlane RTL |
| QAUTOTUNE | 22 | VTOL | QuadPlane autotune |
| QACRO | 23 | VTOL | QuadPlane acro |
| THERMAL | 24 | Auto | Thermal soaring |
| LOITER_ALT_QLAND | 25 | VTOL | Loiter then QLAND |
| AUTOLAND | 26 | Auto | Automatic landing |

## Quick Patterns

### Access Plane Singleton
```cpp
Plane &plane = *Plane::get_singleton();
// Or from mode: plane (already available as reference)
```

### Set Servo Output
```cpp
SRV_Channels::set_output_scaled(SRV_Channel::k_aileron, value);
SRV_Channels::set_output_scaled(SRV_Channel::k_elevator, value);
SRV_Channels::set_output_scaled(SRV_Channel::k_throttle, value);
SRV_Channels::set_output_scaled(SRV_Channel::k_rudder, value);
```

### TECS Speed/Height Control
```cpp
TECS_controller.update_pitch_throttle(
    target_alt_cm,
    target_airspeed_cm,
    flight_stage,
    distance_beyond_land,
    get_takeoff_pitch_min_cd(),
    throttle_nudge,
    tecs_pitch_min,
    tecs_pitch_max
);
```

### L1 Navigation
```cpp
nav_controller->update_waypoint(prev_WP_loc, next_WP_loc);
float nav_roll = nav_controller->nav_roll_cd();
float nav_bearing = nav_controller->nav_bearing_cd();
```

## Control Hierarchy

```
Mode (update)
    │
    ├─► L1 Navigation (lateral)
    │       └─► Target roll angle
    │
    └─► TECS (longitudinal)
            ├─► Target pitch angle
            └─► Throttle output
                    │
                    ▼
            Attitude Controllers
            (Roll, Pitch, Yaw PIDs)
                    │
                    ▼
            Servo Outputs
```

## Parameter Prefixes

| Prefix | Subsystem |
|--------|-----------|
| `ARSPD_` | Airspeed sensor |
| `TECS_` | Speed/height control |
| `NAVL1_` | L1 navigation |
| `RLL_` | Roll controller |
| `PTCH_` | Pitch controller |
| `YAW_` | Yaw damper |
| `TKOFF_` | Takeoff |
| `LAND_` | Landing |
| `RTL_` | Return to launch |
| `LIM_` | Flight limits |
| `TRIM_` | Trim values |
| `Q_` | QuadPlane |
| `FLTMODE_` | Flight mode channels |

## Scheduler (400Hz Main Loop)

| Task | Rate | Purpose |
|------|------|---------|
| read_radio | 50Hz | RC input |
| update_speed_height | 50Hz | TECS update |
| navigate | 10Hz | L1 navigation |
| update_compass | 10Hz | Heading |
| calc_airspeed_errors | 10Hz | Airspeed |
| update_alt | 10Hz | Altitude |
| one_second_loop | 1Hz | Housekeeping |

## Scripts

- `scripts/find_plane_modes.py` - List all modes and properties
- `scripts/plane_params.py <prefix>` - Find parameters by prefix
