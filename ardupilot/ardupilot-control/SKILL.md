---
name: ardupilot-control
description: |
  ArduPilot control libraries (AC_*, APM_Control, AR_*). Use when working with:
  attitude/position controllers, waypoint navigation, PID tuning, geofencing,
  obstacle avoidance, precision landing, auto-tuning, or vehicle-specific
  controllers (plane L1/TECS, rover steering, helicopter autorotation).
---

# ArduPilot Control Libraries

## Reference Lookup

| Topic | Libraries | Reference |
|-------|-----------|-----------|
| Attitude & Position Control | AC_AttitudeControl, AC_PosControl | [attitude-position.md](references/attitude-position.md) |
| Navigation & Waypoints | AC_WPNav, AC_Loiter, AC_Circle | [navigation.md](references/navigation.md) |
| PID Controllers | AC_PID, AC_P, AC_PID_2D | [pid.md](references/pid.md) |
| Geofencing & Avoidance | AC_Fence, AC_Avoid | [fence-avoid.md](references/fence-avoid.md) |
| Precision Landing | AC_PrecLand | [precision-landing.md](references/precision-landing.md) |
| Auto-Tuning | AC_AutoTune | [autotune.md](references/autotune.md) |
| Fixed-Wing Control | AP_L1_Control, AP_TECS, APM_Control | [plane.md](references/plane.md) |
| Rover Control | AR_AttitudeControl, AR_PosControl | [rover.md](references/rover.md) |
| Helicopter | AC_Autorotation, AC_InputManager | [helicopter.md](references/helicopter.md) |
| Specialized | AC_Sprayer, AC_CustomControl | [specialized.md](references/specialized.md) |

## Parameter Prefixes

| Prefix | Library |
|--------|---------|
| `ATC_` | AC_AttitudeControl |
| `PSC_` | AC_PosControl |
| `WPNAV_` | AC_WPNav |
| `LOITER_` | AC_Loiter |
| `CIRCLE_` | AC_Circle |
| `FENCE_` | AC_Fence |
| `AVOID_` | AC_Avoid |
| `PLND_` | AC_PrecLand |
| `NAVL1_` | AP_L1_Control |
| `TECS_` | AP_TECS |

## Control Hierarchy (Multicopter)

```
Navigation (AC_WPNav/AC_Loiter) → position targets
    ↓
Position (AC_PosControl) → roll/pitch angles
    ↓
Attitude (AC_AttitudeControl) → angular rates
    ↓
Rate Controller → AP_Motors → ESCs
```

## Scripts

- `scripts/find_control_params.py <library>` - Find parameters
- `scripts/control_hierarchy.py <vehicle>` - Visualize hierarchy

## File Locations

All control libraries are in `libraries/`:
- `AC_AttitudeControl/` - Attitude + position control
- `AC_WPNav/` - Navigation (includes AC_Loiter, AC_Circle)
- `AC_PID/` - PID controller variants
- `AC_Fence/`, `AC_Avoidance/` - Safety
- `AC_PrecLand/`, `AC_AutoTune/` - Features
- `APM_Control/` - Plane + Rover controllers
- `AP_L1_Control/`, `AP_TECS/` - Plane-specific
