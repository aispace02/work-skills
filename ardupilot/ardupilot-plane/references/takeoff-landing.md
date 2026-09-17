# Takeoff and Landing

## Automatic Takeoff

### Takeoff Mode

**Mode**: `TAKEOFF` (mode 13)
**File**: `mode_takeoff.cpp`

```cpp
class ModeTakeoff : public Mode {
    // Parameters
    AP_Int16 target_alt;      // Target altitude (m)
    AP_Int16 level_alt;       // Altitude to level off (m)
    AP_Float ground_pitch;    // Ground pitch angle
    AP_Int16 target_dist;     // Target distance (m)
    AP_Int8 level_pitch;      // Level-off pitch
};
```

### Takeoff Sequence

1. **Ground Roll**: Accelerate down runway at `TKOFF_THR_MAX`
2. **Rotation**: When airspeed reaches `TKOFF_ROTATE_SPD`, pitch up to `TKOFF_LVL_PITCH`
3. **Climb**: Climb at `TKOFF_LVL_PITCH` until `TKOFF_LVL_ALT`
4. **Level Off**: Transition to normal climb to `TKOFF_ALT`
5. **Complete**: Switch to mission or RTL

### Takeoff Parameters (TKOFF_)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `TKOFF_THR_DELAY` | Delay before full throttle (s) | 2 |
| `TKOFF_THR_MAX` | Max throttle during takeoff | 100 |
| `TKOFF_THR_MIN` | Min throttle during takeoff | 0 |
| `TKOFF_ROTATE_SPD` | Rotation speed (m/s) | 0 |
| `TKOFF_THR_SLEW` | Throttle slew rate | 0 |
| `TKOFF_PLIM_SEC` | Pitch limit release time | 2 |
| `TKOFF_FLAP_PCNT` | Flap percentage for takeoff | 0 |
| `TKOFF_ALT` | Target takeoff altitude (m) | 50 |
| `TKOFF_LVL_ALT` | Level-off altitude (m) | 5 |
| `TKOFF_LVL_PITCH` | Level-off pitch (deg) | 15 |
| `TKOFF_DIST` | Takeoff waypoint distance (m) | 200 |
| `TKOFF_GND_PITCH` | Ground pitch angle (deg) | 5 |

### Mission Takeoff Command

```cpp
// NAV_TAKEOFF command
MAV_CMD_NAV_TAKEOFF
  param1: min_pitch     // Minimum pitch (deg)
  param4: yaw           // Desired heading
  x, y: lat, lon        // Takeoff position
  z: altitude           // Target altitude
```

---

## Automatic Landing

### AP_Landing Library

**Location**: `libraries/AP_Landing/`

### Landing Stages

```cpp
enum LandingStage {
    APPROACH,     // Descending to final approach
    LOITER_TO_ALT,// Loiter down to approach altitude
    FINAL,        // Final approach descent
    FLARE,        // Pre-touchdown flare
    TOUCHDOWN,    // On ground
    ABORT         // Go-around
};
```

### Landing Sequence

1. **Approach**: Navigate to landing waypoint, descend
2. **Final Approach**: Follow glide slope to runway
3. **Flare**: Pitch up, reduce throttle before touchdown
4. **Touchdown**: Detect ground contact, apply brakes

### Landing Parameters (LAND_)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `LAND_FLARE_ALT` | Flare altitude (m) | 3.0 |
| `LAND_FLARE_SEC` | Flare time (s) | 2.0 |
| `LAND_DISARMDELAY` | Disarm delay after landing (s) | 20 |
| `LAND_THEN_NEUTRL` | Neutral after landing | 0 |
| `LAND_ABORT_THR` | Throttle for abort | 75 |
| `LAND_FLAP_PERCNT` | Flap percentage for landing | 100 |
| `LAND_TYPE` | Landing type (0=normal, 1=slope) | 0 |
| `LAND_SLOPE_RCALC` | Slope recalculation | 0 |
| `LAND_PF_ALT` | Pre-flare altitude (m) | 2.0 |
| `LAND_PF_ARSPD` | Pre-flare airspeed (m/s) | 0 |
| `LAND_PF_SEC` | Pre-flare time (s) | 0 |

### Mission Landing Commands

```cpp
// DO_LAND_START - marks beginning of landing sequence
MAV_CMD_DO_LAND_START
  // Just a marker, no parameters

// NAV_LAND - actual landing command
MAV_CMD_NAV_LAND
  param1: abort_alt     // Abort altitude
  x, y: lat, lon        // Landing position
  z: altitude           // Target altitude at touchdown

// NAV_LOITER_TO_ALT - descend in loiter before approach
MAV_CMD_NAV_LOITER_TO_ALT
  param1: heading       // Required heading
  param2: radius        // Loiter radius
  x, y: lat, lon        // Loiter position
  z: altitude           // Target altitude
```

### Rangefinder for Landing

```cpp
// Enable rangefinder for landing
RNGFND_LANDING = 1

// Parameters
LAND_FLARE_ALT  // Can use rangefinder instead of baro
```

---

## AutoLand Mode

**Mode**: `AUTOLAND` (mode 26)
**File**: `mode_autoland.cpp`

Emergency landing mode that can be triggered by switch.

### AutoLand Stages

```cpp
enum class AutoLandStage {
    CLIMB,    // Climb to safe altitude
    LOITER,   // Loiter to align with landing direction
    LANDING   // Execute landing
};
```

### AutoLand Parameters

| Parameter | Description |
|-----------|-------------|
| `AUTOLAND_WP_ALT` | Final approach altitude |
| `AUTOLAND_WP_DIST` | Distance to final waypoint |
| `AUTOLAND_DIR_OFF` | Direction offset from current heading |

---

## RTL with Landing

### RTL_AUTOLAND Parameter

```cpp
enum class RtlAutoland {
    RTL_DISABLE = 0,              // RTL only, no landing
    RTL_THEN_DO_LAND_START = 1,   // RTL, then execute DO_LAND_START
    RTL_IMMEDIATE_DO_LAND_START = 2, // Skip RTL, go to landing
    NO_RTL_GO_AROUND = 3,         // Go around current position
};
```

---

## QuadPlane Landing

### QLAND Mode

For VTOL landing:

```cpp
// Transition to VTOL, then descend vertically
if (plane.quadplane.available()) {
    plane.set_mode(plane.mode_qland, ModeReason::UNKNOWN);
}
```

### QRTL Mode

Return to launch with VTOL landing:

```cpp
// Fly back as plane, transition to VTOL near home
// Land vertically
```

### Loiter to QLAND

**Mode**: `LOITER_ALT_QLAND` (mode 25)

Loiter down to specific altitude, then switch to QLAND.

---

## Landing Abort

### Abort Conditions

- Pilot commands abort (throttle > `LAND_ABORT_THR`)
- Altitude too low for safe approach
- Excessive crosswind

### Go-Around

```cpp
void Plane::landing_abort() {
    // Apply full throttle
    SRV_Channels::set_output_scaled(SRV_Channel::k_throttle, 100);

    // Pitch up
    nav_pitch_cd = LAND_ABORT_PITCH_CD;

    // Retract flaps
    landing.set_flaps_override(false);

    // Return to approach waypoint
    mission.restart_current_nav_cmd();
}
```

---

## Deep Stall Landing

For aircraft with deep stall capability:

### Parameters (DSPOILER_)

| Parameter | Description |
|-----------|-------------|
| `DSPOILER_CROW_W1` | Crow flap weight |
| `DSPOILER_CROW_W2` | Progressive crow weight |
| `LAND_DS_*` | Deep stall parameters |

### Deep Stall Sequence

1. Enter deep stall at high altitude
2. Maintain stable descent angle
3. Minimal flare needed at touchdown
