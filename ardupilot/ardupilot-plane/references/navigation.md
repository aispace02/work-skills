# L1 Navigation Controller

## Overview

**Location**: `libraries/AP_L1_Control/AP_L1_Control.h`

The L1 controller provides lateral (roll) guidance for waypoint navigation. It calculates the roll angle needed to follow a path between waypoints.

## L1 Concept

The L1 controller uses a "look-ahead" point on the desired path. The aircraft aims toward this point, which is L1 distance ahead. This creates smooth path following.

```
                    L1 distance
    Aircraft  ←─────────────────→  L1 point on path
        ↘                           ↙
         ↘      (Turn toward)      ↙
          ↘                       ↙
           ↘                     ↙
            →→→  Path to follow →→→
```

## Core API

```cpp
class AP_L1_Control : public AP_Navigation {
public:
    // Waypoint following
    void update_waypoint(const Location &prev_WP, const Location &next_WP);

    // Loiter (circle)
    void update_loiter(const Location &center, float radius, int8_t direction);

    // Heading hold
    void update_heading(float heading_cd);

    // Get outputs
    int32_t nav_roll_cd() const;          // Target roll in centidegrees
    float nav_bearing_cd() const;         // Navigation bearing
    float lateral_acceleration() const;   // Lateral accel demand

    // Status
    float crosstrack_error() const;       // Distance from path (m)
    float distance_to_waypoint() const;   // Distance to next WP (m)
    bool reached_waypoint() const;

    // Configuration
    void set_L1_period(float period);
    void set_L1_damping(float damping);
};
```

## Usage Patterns

### Waypoint Navigation

```cpp
void ModeAuto::navigate() {
    // Update L1 controller with waypoints
    plane.nav_controller->update_waypoint(
        plane.prev_WP_loc,    // Previous waypoint
        plane.next_WP_loc     // Target waypoint
    );

    // Get roll command
    plane.nav_roll_cd = plane.nav_controller->nav_roll_cd();

    // Check if reached
    if (plane.nav_controller->reached_waypoint()) {
        advance_to_next_waypoint();
    }
}
```

### Loiter (Circle)

```cpp
void ModeLoiter::navigate() {
    // Circle around center point
    plane.nav_controller->update_loiter(
        plane.next_WP_loc,        // Center point
        plane.aparm.loiter_radius, // Radius in meters
        plane.loiter.direction     // 1=CW, -1=CCW
    );

    plane.nav_roll_cd = plane.nav_controller->nav_roll_cd();
}
```

### Heading Hold

```cpp
void ModeCruise::navigate() {
    if (locked_heading) {
        // Hold specific heading
        plane.nav_controller->update_heading(locked_heading_cd);
        plane.nav_roll_cd = plane.nav_controller->nav_roll_cd();
    }
}
```

## Parameters (NAVL1_)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `NAVL1_PERIOD` | L1 navigation period (s) | 17 |
| `NAVL1_DAMPING` | L1 damping | 0.75 |
| `NAVL1_XTRACK_I` | Crosstrack error integrator gain | 0.02 |
| `NAVL1_LIM_BANK` | Maximum bank angle (deg) | 0 (use LIM_ROLL_CD) |

## Tuning

### L1 Period (`NAVL1_PERIOD`)

- **Smaller value**: More aggressive turns, tighter path tracking
- **Larger value**: Smoother turns, may cut corners

**Rule of thumb**: Set to roughly 1.5-2x the aircraft's turn radius at cruise speed.

### L1 Damping (`NAVL1_DAMPING`)

- **Higher value**: Reduces oscillation, smoother response
- **Lower value**: More responsive but may oscillate

**Typical range**: 0.7 - 0.85

### Crosstrack Integrator (`NAVL1_XTRACK_I`)

- Corrects steady-state crosstrack errors (e.g., from wind)
- Start low and increase if wind causes persistent offset

## Roll Limit

```cpp
// Roll is limited by LIM_ROLL_CD parameter
plane.nav_roll_cd = constrain_int32(
    plane.nav_controller->nav_roll_cd(),
    -plane.roll_limit_cd,
    plane.roll_limit_cd
);
```

## Integration with TECS

L1 handles lateral guidance, TECS handles longitudinal:

```
Navigation Input
      │
      ├───► L1 Controller ───► Roll Angle
      │     (lateral)
      │
      └───► TECS Controller
            (longitudinal)
                  │
                  ├───► Pitch Angle
                  └───► Throttle
```

## Crosstrack Error

The controller reports distance from the ideal path:

```cpp
float xtrack = plane.nav_controller->crosstrack_error();
// Positive = right of path, Negative = left of path

// Used for logging and display
gcs().send_text(MAV_SEVERITY_INFO, "XTrack: %.1fm", xtrack);
```

## Waypoint Acceptance

Waypoint is considered reached when:

```cpp
bool reached_waypoint() const {
    // Within acceptance radius
    if (distance_to_waypoint() < WP_RADIUS) {
        return true;
    }
    // Or passed the waypoint (for overshoot cases)
    if (has_passed_waypoint()) {
        return true;
    }
    return false;
}
```

## Logging

L1 logs to `NTUN` message:

| Field | Description |
|-------|-------------|
| wp_dist | Distance to waypoint (m) |
| target_bearing | Target bearing (deg) |
| nav_bearing | Actual navigation bearing |
| xtrack | Crosstrack error (m) |
| nav_roll | Commanded roll (deg) |
| nav_pitch | Commanded pitch (deg) |
