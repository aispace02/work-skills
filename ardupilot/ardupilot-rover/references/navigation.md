# Rover Navigation

## AR_WPNav_OA

**Location**: `libraries/AR_WPNav/AR_WPNav.h`

Waypoint navigation with obstacle avoidance for rovers.

### Initialization

```cpp
void AR_WPNav::init() {
    // Set default parameters
    _speed_max = g.speed_cruise;
    _turn_radius = g2.turn_radius;
}
```

### Core Methods

```cpp
// Set destination
bool set_desired_location(const Location &destination);
bool set_desired_location_NED(const Vector3f &destination);

// Update navigation (call every loop)
void update(float dt);

// Get outputs
float get_turn_rate_rads() const;     // Turn rate (rad/s)
float get_lateral_accel() const;      // Lateral acceleration (m/s²)
float get_speed() const;              // Target speed (m/s)

// Status
bool reached_destination() const;
float get_distance_to_destination() const;
float get_bearing_to_destination() const;  // radians

// Speed control
void set_speed(float speed);          // Override target speed
float get_speed_max() const;

// Turn rate limits
float get_turn_max_rads() const;
void set_turn_max_rads(float rate);
```

### Usage Pattern

```cpp
void ModeAuto::update() {
    // Set destination (once)
    if (new_waypoint) {
        g2.wp_nav.set_desired_location(next_wp);
    }

    // Update navigation (every loop)
    g2.wp_nav.update(rover.G_Dt);

    // Get turn rate for steering
    float turn_rate = g2.wp_nav.get_turn_rate_rads();
    calc_steering_from_turn_rate(turn_rate);

    // Get speed for throttle
    float target_speed = g2.wp_nav.get_speed();
    calc_throttle(target_speed, true);

    // Check completion
    if (g2.wp_nav.reached_destination()) {
        advance_to_next_waypoint();
    }
}
```

## AR_PosControl

**Location**: `libraries/APM_Control/AR_PosControl.h`

Position feedback controller (alternative to waypoint navigation).

### Core Methods

```cpp
// Update
void update(float dt);

// Position inputs
void input_pos_target(const Location &target);
void input_pos_target(const Vector2f &target_NE);

// Velocity inputs
void input_vel_target(const Vector2f &vel);

// Outputs
float get_steering_out() const;
float get_throttle_out() const;
float get_desired_speed() const;
float get_desired_lat_accel() const;

// State
bool reached_destination() const;
float get_distance_to_destination() const;
```

### Usage Pattern

```cpp
void ModeGuided::update() {
    // Set target position
    g2.pos_control.input_pos_target(target_location);

    // Update controller
    g2.pos_control.update(rover.G_Dt);

    // Get outputs
    float steering = g2.pos_control.get_steering_out();
    float throttle = g2.pos_control.get_throttle_out();

    g2.motors.set_steering(steering);
    g2.motors.set_throttle(throttle);
}
```

## Mode Helper Methods

Available in all Mode classes for navigation.

### navigate_to_waypoint()

```cpp
void Mode::navigate_to_waypoint() {
    // Full navigation update
    g2.wp_nav.update(rover.G_Dt);

    // Get turn rate
    float turn_rate = g2.wp_nav.get_turn_rate_rads();

    // Apply steering
    calc_steering_from_turn_rate(turn_rate);

    // Apply throttle
    calc_throttle(g2.wp_nav.get_speed(), true);
}
```

### calc_steering_to_heading()

```cpp
void Mode::calc_steering_to_heading(
    float desired_heading_cd,  // centidegrees
    float rate_max_degs        // max turn rate deg/s
) {
    // Get turn rate from heading error
    float turn_rate = g2.attitude_control.get_turn_rate_from_heading(
        radians(desired_heading_cd * 0.01f),
        radians(rate_max_degs)
    );

    calc_steering_from_turn_rate(turn_rate);
}
```

### calc_steering_from_turn_rate()

```cpp
void Mode::calc_steering_from_turn_rate(float turn_rate) {
    float steering = g2.attitude_control.get_steering_out_rate(
        turn_rate,
        g2.motors.limit.steer_left,
        g2.motors.limit.steer_right,
        rover.G_Dt
    );

    // Handle reversing
    if (reversed()) {
        steering = -steering;
    }

    g2.motors.set_steering(steering);
}
```

### calc_throttle()

```cpp
void Mode::calc_throttle(float target_speed, bool avoidance_enabled) {
    // Apply speed nudge from pilot input (if allowed)
    target_speed = calc_speed_nudge(target_speed, reversed());

    // Apply avoidance deceleration
    if (avoidance_enabled) {
        target_speed = g2.avoid.adjust_speed(target_speed);
    }

    // Get throttle output
    float throttle = g2.attitude_control.get_throttle_out_speed(
        target_speed,
        g2.motors.limit.throttle_lower,
        g2.motors.limit.throttle_upper,
        g.speed_cruise,
        g.throttle_cruise * 0.01f,
        rover.G_Dt
    );

    g2.motors.set_throttle(throttle);
}
```

### stop_vehicle()

```cpp
bool Mode::stop_vehicle() {
    bool stopped = false;

    float throttle = g2.attitude_control.get_throttle_out_stop(
        g2.motors.limit.throttle_lower,
        g2.motors.limit.throttle_upper,
        g.speed_cruise,
        g.throttle_cruise * 0.01f,
        rover.G_Dt,
        stopped
    );

    g2.motors.set_throttle(throttle);

    // Keep steering centered or current
    g2.motors.set_steering(0);

    return stopped;
}
```

## Obstacle Avoidance

AR_WPNav_OA includes obstacle avoidance using AP_OAPathPlanner.

```cpp
// Avoidance is automatically applied when:
// - AVOID_ENABLE parameter is set
// - Valid proximity sensor data exists

// Path planning around obstacles
// Adjusts waypoint location to avoid obstacles
// Slows down when approaching obstacles
```

### Avoidance Methods

```cpp
// Speed adjustment for obstacles
float AP_Avoid::adjust_speed(float desired_speed);

// Check if obstacle ahead
bool AP_Avoid::proximity_check();

// Get modified destination around obstacle
bool AP_OAPathPlanner::get_destination(
    const Location &origin,
    const Location &destination,
    Location &result
);
```

## Waypoint Parameters (WP_)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `WP_SPEED` | Waypoint speed (m/s) | 2.0 |
| `WP_RADIUS` | Waypoint radius (m) | 2.0 |
| `WP_OVERSHOOT` | Max overshoot (m) | 2.0 |
| `WP_PIVOT_ANGLE` | Pivot vs drive-through angle | 60 |
| `WP_PIVOT_RATE` | Pivot turn rate (deg/s) | 60 |

## Turn Radius Parameters

| Parameter | Description |
|-----------|-------------|
| `TURN_RADIUS` | Vehicle turn radius (m) |
| `TURN_MAX_G` | Max lateral G |
| `ATC_STR_RAT_MAX` | Max steering rate (deg/s) |

## SmartRTL Navigation

**Location**: `libraries/AP_SmartRTL/AP_SmartRTL.h`

Records path for reversing back to home.

```cpp
// Initialize
void AP_SmartRTL::init();

// Update (records current position)
void AP_SmartRTL::update(bool position_ok, const Vector3f &current_pos);

// Get next point for return
bool AP_SmartRTL::pop_point(Vector3f &point);

// Check if path available
bool AP_SmartRTL::is_active() const;
uint16_t AP_SmartRTL::get_num_points() const;
```

### SmartRTL Parameters

| Parameter | Description |
|-----------|-------------|
| `SRTL_ACCURACY` | Position accuracy (m) |
| `SRTL_POINTS` | Max points to store |

## Navigation States

```cpp
// Common navigation state checks
bool Mode::reached_destination() const {
    return g2.wp_nav.reached_destination();
}

float Mode::get_distance_to_destination() const {
    return g2.wp_nav.get_distance_to_destination();
}

bool Mode::get_desired_location(Location &dest) const {
    return g2.wp_nav.get_desired_location(dest);
}
```

## Coordinate Systems

```cpp
// Location (geodetic)
Location loc;
loc.lat = 37.7749 * 1e7;  // Latitude in 1e-7 degrees
loc.lng = -122.4194 * 1e7; // Longitude in 1e-7 degrees
loc.alt = 100 * 100;       // Altitude in cm

// NED (North-East-Down) relative to home
Vector3f ned_pos;  // meters from home

// Conversion
Location::get_distance(loc1, loc2);       // Distance in meters
Location::get_bearing(loc1, loc2);        // Bearing in centidegrees
loc.offset_bearing(bearing, distance);    // Offset position
```
