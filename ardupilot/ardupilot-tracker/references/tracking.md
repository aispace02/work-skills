# Vehicle Tracking System

## Overview

The tracking system receives vehicle position data via MAVLink and calculates the required pointing angles for the antenna.

**File**: `tracking.cpp`

## Data Flow

```
MAVLink Position → Position Estimation → Bearing/Distance → Target Angles → Servo Control
```

## Vehicle State

```cpp
struct VehicleState {
    Location location;          // Current position
    Vector3f vel;               // Velocity (m/s NED)
    uint32_t location_time_ms;  // Last update timestamp
    bool location_valid;        // Position is valid
    bool initialised;           // Tracking initialized
};
```

## Position Estimation

Vehicle position is extrapolated using velocity to account for telemetry latency:

```cpp
void Tracker::update_vehicle_pos_estimate() {
    // Time since last position update
    float dt = (AP_HAL::millis() - vehicle.location_time_ms) * 0.001f;

    // Extrapolate position using velocity
    // vehicle_location = last_known_location + velocity * dt
    current_loc = vehicle.location;
    current_loc.offset(vehicle.vel.x * dt, vehicle.vel.y * dt);
    current_loc.set_alt_cm(current_loc.alt + vehicle.vel.z * dt * 100,
                           current_loc.get_alt_frame());
}
```

## Bearing and Distance Calculation

```cpp
void Tracker::update_bearing_and_distance() {
    // Get tracker location
    Location tracker_loc;
    if (!get_current_location(tracker_loc)) {
        return;
    }

    // Calculate bearing (degrees)
    nav_status.bearing = tracker_loc.get_bearing_to(current_loc) * 0.01f;

    // Calculate distance (meters)
    nav_status.distance = tracker_loc.get_distance(current_loc);

    // Calculate pitch angle
    float alt_diff = (current_loc.alt - tracker_loc.alt) * 0.01f;  // meters
    nav_status.pitch = degrees(atan2f(alt_diff, nav_status.distance));
}
```

## Tracker Location Sources

The tracker's own location can come from multiple sources:

### GPS Location
```cpp
bool Tracker::get_current_location(Location &loc) {
    if (ahrs.get_location(loc)) {
        return true;
    }
    // Fall back to configured start location
    loc = start_location;
    return start_location_set;
}
```

### Configured Start Location
```cpp
// Parameters for stationary tracker without GPS
AP_Float start_latitude;   // START_LATITUDE
AP_Float start_longitude;  // START_LONGITUDE
```

## Altitude Source

Controlled by `ALT_SOURCE` parameter:

| Value | Source | Description |
|-------|--------|-------------|
| 0 | Barometer | Tracker barometer for altitude |
| 1 | GPS | Tracker GPS for altitude |
| 2 | GPS Vehicle Only | Use vehicle GPS altitude only |

```cpp
void Tracker::update_altitude() {
    switch (g.alt_source) {
    case ALT_SOURCE_BARO:
        current_loc.set_alt_cm(baro.get_altitude() * 100, Location::AltFrame::ABOVE_HOME);
        break;
    case ALT_SOURCE_GPS:
        current_loc.set_alt_cm(gps.location().alt, Location::AltFrame::ABSOLUTE);
        break;
    case ALT_SOURCE_GPS_VEH_ONLY:
        // Don't update tracker altitude
        break;
    }
}
```

## MAVLink Vehicle Updates

### Position Update

```cpp
void GCS_MAVLINK_Tracker::handle_global_position_int(const mavlink_message_t &msg) {
    mavlink_global_position_int_t packet;
    mavlink_msg_global_position_int_decode(&msg, &packet);

    // Update vehicle location
    tracker.vehicle.location.lat = packet.lat;
    tracker.vehicle.location.lng = packet.lon;
    tracker.vehicle.location.set_alt_cm(packet.alt / 10, Location::AltFrame::ABSOLUTE);

    // Update velocity
    tracker.vehicle.vel.x = packet.vx * 0.01f;
    tracker.vehicle.vel.y = packet.vy * 0.01f;
    tracker.vehicle.vel.z = packet.vz * 0.01f;

    // Mark position as valid
    tracker.vehicle.location_time_ms = AP_HAL::millis();
    tracker.vehicle.location_valid = true;
}
```

### Target System Selection

```cpp
// SYSID_TARGET parameter
// 0 = auto-detect (track first vehicle seen)
// 1-255 = track specific MAVLink system ID
AP_Int16 sysid_target;
```

## Minimum Distance Filter

Tracking is disabled when vehicle is too close:

```cpp
// In mode.cpp update_auto()
if ((g.distance_min <= 0) ||
    (nav_status.distance >= g.distance_min) ||
    !tracker.vehicle.location_valid) {
    tracker.update_pitch_servo(bf_pitch);
    tracker.update_yaw_servo(bf_yaw);
}
```

**Parameter**: `DISTANCE_MIN` (default: varies)

## NavStatus Structure

Holds computed tracking data:

```cpp
struct NavStatus {
    float bearing;              // Target bearing (0-360 degrees)
    float distance;             // Target distance (meters)
    float pitch;                // Target pitch angle (degrees)
    float angle_error_pitch;    // Pitch error (centidegrees)
    float angle_error_yaw;      // Yaw error (centidegrees)
    bool manual_control_yaw;    // Manual yaw override active
    bool manual_control_pitch;  // Manual pitch override active
    bool scan_reverse_yaw;      // Scan direction flag
    bool scan_reverse_pitch;    // Scan direction flag
};
```

## Guided Mode Targeting

For direct GCS control:

```cpp
struct GuidedTarget {
    Location location;          // Target location
    bool valid;                 // Target is set
    uint32_t time_ms;           // When target was set
};

void GCS_MAVLINK_Tracker::handle_set_attitude_target(const mavlink_message_t &msg) {
    // Set specific yaw/pitch angles directly
    mavlink_set_attitude_target_t packet;
    mavlink_msg_set_attitude_target_decode(&msg, &packet);

    // Convert quaternion to euler angles
    // Apply to nav_status
}
```

## Update Rates

| Function | Rate | Purpose |
|----------|------|---------|
| `update_vehicle_pos_estimate()` | 50 Hz | Position extrapolation |
| `update_bearing_and_distance()` | 50 Hz | Angle calculation |
| MAVLink position reception | 1-10 Hz | Vehicle telemetry |

The `MAV_UPDATE_RATE` parameter controls expected MAVLink update rate.

## Position Validity

Position becomes invalid if:
- No MAVLink updates for timeout period
- Vehicle not yet acquired
- Target system ID doesn't match

```cpp
bool vehicle_position_valid() {
    // Check if position is fresh
    uint32_t age_ms = AP_HAL::millis() - vehicle.location_time_ms;
    return vehicle.location_valid && (age_ms < POSITION_TIMEOUT_MS);
}
```

## Tracking Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `SYSID_TARGET` | Vehicle MAVLink ID (0=auto) | 0 |
| `DISTANCE_MIN` | Minimum tracking distance (m) | - |
| `ALT_SOURCE` | Altitude source selection | 0 |
| `MAV_UPDATE_RATE` | Expected MAVLink rate (Hz) | 1 |
| `START_LATITUDE` | Fixed tracker latitude (deg) | 0 |
| `START_LONGITUDE` | Fixed tracker longitude (deg) | 0 |
