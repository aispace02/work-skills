# Rover Control

Control libraries for ground vehicles (Rover).

## AR_AttitudeControl

**Location**: `libraries/APM_Control/AR_AttitudeControl.h`

**Singleton**: `AR_AttitudeControl::get_singleton()`

### Steering Control

```cpp
// Heading control - returns steering output (-1 to +1)
float get_steering_out_heading(
    float heading_rad,                        // Desired heading (rad)
    float rate_max_rads,                      // Max turn rate (rad/s)
    bool motor_limit_left,                    // Left motor at limit
    bool motor_limit_right,                   // Right motor at limit
    float dt
);

// Rate control - direct turn rate
float get_steering_out_rate(
    float desired_rate,                       // Desired turn rate (rad/s)
    bool motor_limit_left,
    bool motor_limit_right,
    float dt
);

// Lateral acceleration control
float get_steering_out_lat_accel(
    float desired_accel,                      // Desired lateral accel (m/s²)
    bool motor_limit_left,
    bool motor_limit_right,
    float dt
);

// Helpers
float get_turn_rate_from_heading(float heading_rad, float rate_max_rads) const;
float get_turn_rate_from_lat_accel(float lat_accel, float speed) const;
```

### Speed/Throttle Control

```cpp
// Speed control - returns throttle output (-1 to +1)
float get_throttle_out_speed(
    float desired_speed,                      // m/s
    bool motor_limit_low,
    bool motor_limit_high,
    float cruise_speed,
    float cruise_throttle,
    float dt
);

// Stop control - controlled deceleration
float get_throttle_out_stop(
    bool motor_limit_low,
    bool motor_limit_high,
    float cruise_speed,
    float cruise_throttle,
    float dt,
    bool &stopped                             // Output: true when stopped
);

// Speed limits
void set_throttle_limits(float throttle_accel_max, float throttle_decel_max);
float get_accel_max() const;
float get_decel_max() const;
float get_stopping_distance(float speed) const;
float get_stop_speed() const;
```

### Special Modes

```cpp
// BalanceBot - pitch-based throttle
float get_throttle_out_from_pitch(
    float desired_pitch,
    float pitch_max,
    bool motor_limit,
    float dt
);

// Sailboat - heel control
float get_sail_out_from_heel(float desired_heel, float dt);
```

### State Queries

```cpp
float get_desired_turn_rate() const;
float get_desired_lat_accel() const;
float get_desired_speed() const;
float get_desired_speed_accel_limited(float desired_speed, float dt) const;
bool speed_control_active() const;
bool steering_limit_left() const;
bool steering_limit_right() const;
void relax_I();
```

### Parameters (ATC_)

| Parameter | Description |
|-----------|-------------|
| `ATC_STR_ANG_P` | Steering angle P gain |
| `ATC_STR_RAT_P/I/D` | Steering rate PID |
| `ATC_STR_RAT_MAX` | Max steering rate (deg/s) |
| `ATC_SPEED_P/I/D` | Speed PID |
| `ATC_ACCEL_MAX` | Max acceleration (m/s²) |
| `ATC_DECEL_MAX` | Max deceleration (m/s²) |
| `ATC_TURN_MAX_G` | Max lateral G |
| `ATC_BAL_*` | BalanceBot parameters |

---

## AR_PosControl

**Location**: `libraries/APM_Control/AR_PosControl.h`

Position control for rovers (used in Auto, Guided modes).

### Core Methods

```cpp
// Update
void update(float dt);

// Inputs
void input_pos_target(const Location &target_loc);
void input_pos_target(const Vector2f &target_pos_m);
void input_vel_target(const Vector2f &target_vel_m);

// Outputs
float get_steering_out();
float get_throttle_out();
float get_desired_speed() const;
float get_desired_lat_accel() const;

// State
bool reached_destination() const;
float get_distance_to_destination() const;
```

---

## Usage Patterns

### Basic Steering

```cpp
void rover_manual_run() {
    AR_AttitudeControl *att = AR_AttitudeControl::get_singleton();

    // Get pilot steering input
    float desired_turn_rate = channel_steer->get_control_in() * max_turn_rate;

    // Get steering output
    float steering = att->get_steering_out_rate(
        desired_turn_rate,
        g2.motors.limit.steer_left,
        g2.motors.limit.steer_right,
        dt
    );

    // Apply
    g2.motors.set_steering(steering);
}
```

### Heading Hold

```cpp
void rover_hold_heading() {
    AR_AttitudeControl *att = AR_AttitudeControl::get_singleton();

    float target_heading = radians(90.0f);  // Face East
    float max_rate = radians(60.0f);        // 60 deg/s max

    float steering = att->get_steering_out_heading(
        target_heading,
        max_rate,
        g2.motors.limit.steer_left,
        g2.motors.limit.steer_right,
        dt
    );

    g2.motors.set_steering(steering);
}
```

### Speed Control

```cpp
void rover_speed_control() {
    AR_AttitudeControl *att = AR_AttitudeControl::get_singleton();

    float desired_speed = 2.0f;  // 2 m/s

    float throttle = att->get_throttle_out_speed(
        desired_speed,
        g2.motors.limit.throttle_lower,
        g2.motors.limit.throttle_upper,
        g.speed_cruise,
        g.throttle_cruise * 0.01f,
        dt
    );

    g2.motors.set_throttle(throttle);
}
```

### Stopping

```cpp
void rover_stop() {
    AR_AttitudeControl *att = AR_AttitudeControl::get_singleton();

    bool stopped = false;
    float throttle = att->get_throttle_out_stop(
        g2.motors.limit.throttle_lower,
        g2.motors.limit.throttle_upper,
        g.speed_cruise,
        g.throttle_cruise * 0.01f,
        dt,
        stopped
    );

    if (stopped) {
        // Vehicle has stopped, can transition to next state
    }

    g2.motors.set_throttle(throttle);
}
```

### Auto Mode

```cpp
void rover_auto_run() {
    AR_PosControl *pos = &g2.pos_control;
    AR_AttitudeControl *att = AR_AttitudeControl::get_singleton();

    // Set target from mission
    pos->input_pos_target(next_waypoint);

    // Update position controller
    pos->update(dt);

    // Get outputs
    float steering = pos->get_steering_out();
    float throttle = pos->get_throttle_out();

    // Apply
    g2.motors.set_steering(steering);
    g2.motors.set_throttle(throttle);

    // Check completion
    if (pos->reached_destination()) {
        advance_to_next_waypoint();
    }
}
```

## Control Hierarchy (Rover)

```
Navigation (AR_WPNav / Mode)
    ↓ position/heading targets
AR_PosControl or AR_AttitudeControl
    ↓ steering, throttle
AR_Motors
    ↓
Servos/ESCs (wheels, steering servo)
```
