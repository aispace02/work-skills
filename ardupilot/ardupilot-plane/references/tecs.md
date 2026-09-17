# TECS - Total Energy Control System

## Overview

**Location**: `libraries/AP_TECS/AP_TECS.h`

TECS controls both airspeed and altitude simultaneously by managing the aircraft's total energy (kinetic + potential). It outputs pitch angle and throttle commands.

## Concept

```
Total Energy = Kinetic Energy + Potential Energy
             = ½mv² + mgh

Energy Rate = Power - Drag
            = Throttle × Engine Power - Drag(v)

Pitch controls energy distribution:
  - Pitch up: converts speed to altitude
  - Pitch down: converts altitude to speed

Throttle controls total energy:
  - More throttle: more total energy
  - Less throttle: less total energy
```

## Core API

```cpp
class AP_TECS {
public:
    // Main update function
    void update_pitch_throttle(
        int32_t target_alt_cm,        // Target altitude
        float target_airspeed_cm,     // Target airspeed (or 0 for auto)
        AP_FixedWing::FlightStage stage, // Current flight stage
        float distance_beyond_land,   // Distance past landing point
        int32_t takeoff_pitch_cd,     // Takeoff pitch limit
        float throttle_nudge,         // Throttle nudge factor
        float pitch_min_cd,           // Min pitch angle
        float pitch_max_cd            // Max pitch angle
    );

    // Get outputs
    int32_t get_pitch_demand();       // Pitch in centidegrees
    float get_throttle_demand();      // Throttle 0-1

    // Set targets
    void set_target_climbrate(float rate); // For FBWB mode
    void set_target_altitude(float alt);

    // Status
    bool reached_target_altitude() const;
    float get_altitude_error() const;
    float get_speed_error() const;

    // Limits
    float get_max_climbrate() const;
    float get_max_sinkrate() const;
};
```

## Usage Pattern

```cpp
// In altitude.cpp update_speed_height()
void Plane::update_speed_height() {
    // Get target altitude
    int32_t target_alt_cm = get_target_altitude_cm();

    // Get target airspeed
    float target_aspd_cm = get_target_airspeed_cm();

    // Run TECS
    TECS_controller.update_pitch_throttle(
        target_alt_cm,
        target_aspd_cm,
        get_flight_stage(),
        landing.get_distance_remaining_beyond_point(current_loc),
        get_takeoff_pitch_min_cd(),
        throttle_nudge_value(),
        get_pitch_min_cd(),
        get_pitch_max_cd()
    );

    // Apply outputs
    nav_pitch_cd = TECS_controller.get_pitch_demand();
    // Throttle applied in set_throttle()
}
```

## Flight Stages

```cpp
enum class FlightStage {
    TAKEOFF,      // During takeoff climb
    VTOL,         // VTOL flight (QuadPlane)
    NORMAL,       // Normal flight
    LAND,         // Landing approach
    FINAL,        // Final landing flare
};
```

## Parameters (TECS_)

### Speed Control

| Parameter | Description | Default |
|-----------|-------------|---------|
| `TECS_SPDWEIGHT` | Speed/height priority (0=height, 2=speed) | 1.0 |
| `TECS_TIME_CONST` | Control time constant | 5.0 |
| `TECS_THR_DAMP` | Throttle damping | 0.5 |
| `TECS_INTEG_GAIN` | Integrator gain | 0.3 |

### Pitch Control

| Parameter | Description | Default |
|-----------|-------------|---------|
| `TECS_PTCH_DAMP` | Pitch damping | 0.0 |
| `TECS_PTCH_FF_K` | Pitch feed-forward from speed error | 0.0 |
| `TECS_PTCH_FF_V0` | Speed at zero feed-forward | 12.0 |

### Climb/Descent

| Parameter | Description | Default |
|-----------|-------------|---------|
| `TECS_CLMB_MAX` | Max climb rate (m/s) | 5.0 |
| `TECS_SINK_MIN` | Min sink rate (m/s) | 2.0 |
| `TECS_SINK_MAX` | Max sink rate (m/s) | 5.0 |

### Throttle

| Parameter | Description | Default |
|-----------|-------------|---------|
| `TECS_THR_FF` | Throttle feed-forward | 0.0 |
| `THR_MAX` | Maximum throttle % | 75 |
| `THR_MIN` | Minimum throttle % | 0 |
| `TRIM_THROTTLE` | Cruise throttle % | 45 |

### Airspeed

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ARSPD_FBW_MIN` | Minimum airspeed (m/s) | 9 |
| `ARSPD_FBW_MAX` | Maximum airspeed (m/s) | 22 |
| `TRIM_ARSPD_CM` | Target airspeed (cm/s) | 1200 |

## TECS Tuning

### Basic Tuning Steps

1. **Set cruise throttle**: `TRIM_THROTTLE` should maintain level flight at cruise speed
2. **Set climb rate**: `TECS_CLMB_MAX` based on aircraft capability
3. **Set time constant**: `TECS_TIME_CONST` (smaller = more aggressive)
4. **Tune damping**: `TECS_THR_DAMP` to reduce oscillations

### Common Issues

| Issue | Solution |
|-------|----------|
| Altitude oscillation | Increase `TECS_TIME_CONST` |
| Slow altitude response | Decrease `TECS_TIME_CONST` |
| Speed hunting | Adjust `TECS_SPDWEIGHT` |
| Throttle oscillation | Increase `TECS_THR_DAMP` |
| Can't maintain altitude | Check `THR_MAX`, `TECS_CLMB_MAX` |

## Integration with Modes

### FBWB Mode
```cpp
// Pitch stick controls climb rate
float climb_rate = stick_input * TECS_CLMB_MAX;
TECS_controller.set_target_climbrate(climb_rate);
```

### Auto Mode
```cpp
// Mission sets target altitude
TECS_controller.update_pitch_throttle(
    mission_altitude,
    cruise_airspeed,
    FlightStage::NORMAL,
    ...
);
```

### Landing
```cpp
// Use sink rate for landing
TECS_controller.update_pitch_throttle(
    target_alt,
    approach_speed,
    FlightStage::LAND,  // Special landing logic
    ...
);
```

## Logging

TECS logs to `TECS` message:

| Field | Description |
|-------|-------------|
| h | Height above target |
| dh | Height rate |
| hdem | Height demand |
| dhdem | Height rate demand |
| spdem | Speed demand |
| sp | Current speed |
| dsp | Speed rate |
| th | Throttle output |
| ph | Pitch output |
| flags | Status flags |
