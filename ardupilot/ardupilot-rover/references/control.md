# Rover Control System

## AR_AttitudeControl

**Location**: `libraries/APM_Control/AR_AttitudeControl.h`

Primary steering and throttle PID controllers.

## Steering Control

### Heading Control

```cpp
// Get steering output from desired heading
float get_steering_out_heading(
    float heading_rad,         // Desired heading (radians)
    float rate_max_rads,       // Max turn rate (rad/s)
    bool motor_limit_left,     // Left motor at limit
    bool motor_limit_right,    // Right motor at limit
    float dt                   // Delta time
);
```

**Usage**:
```cpp
void hold_heading() {
    float target_heading = radians(90.0f);  // Face East
    float max_rate = radians(60.0f);        // 60 deg/s

    float steering = g2.attitude_control.get_steering_out_heading(
        target_heading,
        max_rate,
        g2.motors.limit.steer_left,
        g2.motors.limit.steer_right,
        rover.G_Dt
    );

    g2.motors.set_steering(steering);
}
```

### Rate Control

```cpp
// Get steering output from desired turn rate
float get_steering_out_rate(
    float desired_rate,        // Desired turn rate (rad/s)
    bool motor_limit_left,
    bool motor_limit_right,
    float dt
);
```

**Usage**:
```cpp
void turn_at_rate() {
    float turn_rate = radians(30.0f);  // 30 deg/s

    float steering = g2.attitude_control.get_steering_out_rate(
        turn_rate,
        g2.motors.limit.steer_left,
        g2.motors.limit.steer_right,
        rover.G_Dt
    );

    g2.motors.set_steering(steering);
}
```

### Lateral Acceleration Control

```cpp
// Get steering output from desired lateral acceleration
float get_steering_out_lat_accel(
    float desired_accel,       // Desired lateral accel (m/s²)
    bool motor_limit_left,
    bool motor_limit_right,
    float dt
);
```

### Helper Conversions

```cpp
// Convert heading error to turn rate
float get_turn_rate_from_heading(
    float heading_rad,         // Desired heading
    float rate_max_rads        // Max rate
) const;

// Convert lateral accel to turn rate
float get_turn_rate_from_lat_accel(
    float lat_accel,           // m/s²
    float speed                // Current speed m/s
) const;
```

## Throttle Control

### Speed Control

```cpp
// Get throttle output from desired speed
float get_throttle_out_speed(
    float desired_speed,       // m/s
    bool motor_limit_low,
    bool motor_limit_high,
    float cruise_speed,        // Cruise speed m/s
    float cruise_throttle,     // Cruise throttle (0-1)
    float dt
);
```

**Usage**:
```cpp
void maintain_speed() {
    float desired_speed = 2.0f;  // 2 m/s

    float throttle = g2.attitude_control.get_throttle_out_speed(
        desired_speed,
        g2.motors.limit.throttle_lower,
        g2.motors.limit.throttle_upper,
        g.speed_cruise,
        g.throttle_cruise * 0.01f,
        rover.G_Dt
    );

    g2.motors.set_throttle(throttle);
}
```

### Stop Control

```cpp
// Get throttle output for controlled stop
float get_throttle_out_stop(
    bool motor_limit_low,
    bool motor_limit_high,
    float cruise_speed,
    float cruise_throttle,
    float dt,
    bool &stopped              // Output: true when stopped
);
```

**Usage**:
```cpp
void stop_and_hold() {
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

    if (stopped) {
        // Vehicle has stopped, do something
    }
}
```

### Acceleration Limits

```cpp
// Set acceleration/deceleration limits
void set_throttle_limits(float accel_max, float decel_max);

// Get limits
float get_accel_max() const;
float get_decel_max() const;

// Get stopping distance at current speed
float get_stopping_distance(float speed) const;

// Get stop speed threshold
float get_stop_speed() const;
```

## Balance Bot Control

```cpp
// Get throttle from pitch for balance bots
float get_throttle_out_from_pitch(
    float desired_pitch,       // Desired pitch angle
    float pitch_max,           // Max pitch
    bool motor_limit,
    float dt
);
```

## Sailboat Control

```cpp
// Get sail output from heel angle
float get_sail_out_from_heel(
    float desired_heel,        // Desired heel angle
    float dt
);
```

## State Queries

```cpp
// Get current desired values
float get_desired_turn_rate() const;
float get_desired_lat_accel() const;
float get_desired_speed() const;

// Get speed-limited desired speed
float get_desired_speed_accel_limited(float desired_speed, float dt) const;

// Controller state
bool speed_control_active() const;
bool steering_limit_left() const;
bool steering_limit_right() const;

// Reset integrators
void relax_I();
```

## Parameters (ATC_)

### Steering Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ATC_STR_ANG_P` | Steering angle P gain | 1.0 |
| `ATC_STR_RAT_P` | Steering rate P gain | 0.2 |
| `ATC_STR_RAT_I` | Steering rate I gain | 0.2 |
| `ATC_STR_RAT_D` | Steering rate D gain | 0.0 |
| `ATC_STR_RAT_IMAX` | Steering rate I max | 1.0 |
| `ATC_STR_RAT_FF` | Steering rate feedforward | 0.0 |
| `ATC_STR_RAT_FILT` | Steering rate filter (Hz) | 10.0 |
| `ATC_STR_RAT_MAX` | Max steering rate (deg/s) | 120 |

### Speed Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ATC_SPEED_P` | Speed P gain | 0.4 |
| `ATC_SPEED_I` | Speed I gain | 0.2 |
| `ATC_SPEED_D` | Speed D gain | 0.0 |
| `ATC_SPEED_IMAX` | Speed I max | 1.0 |
| `ATC_SPEED_FF` | Speed feedforward | 0.0 |
| `ATC_SPEED_FILT` | Speed filter (Hz) | 5.0 |
| `ATC_ACCEL_MAX` | Max acceleration (m/s²) | 2.0 |
| `ATC_DECEL_MAX` | Max deceleration (m/s²) | 2.0 |

### Other Parameters

| Parameter | Description |
|-----------|-------------|
| `ATC_TURN_MAX_G` | Max lateral G during turns |
| `ATC_BAL_PIT_MAX` | Balance bot max pitch |
| `ATC_BAL_P` | Balance bot P gain |
| `ATC_BAL_I` | Balance bot I gain |
| `ATC_BAL_D` | Balance bot D gain |
| `ATC_SAIL_*` | Sailboat heel control gains |

## Control Flow Diagram

```
Desired State (heading, speed)
        │
        ▼
┌───────────────────────────────────┐
│     AR_AttitudeControl            │
│  ┌─────────────────────────────┐  │
│  │ Heading → Rate → Steering   │  │
│  │    P        PID             │  │
│  └─────────────────────────────┘  │
│  ┌─────────────────────────────┐  │
│  │ Speed → Throttle            │  │
│  │      PID + FF               │  │
│  └─────────────────────────────┘  │
└───────────────────────────────────┘
        │
        ▼
    AP_MotorsUGV
        │
        ▼
    Servo/ESC Output
```

## Tuning Guide

### Steering Tuning

1. Start with low P gains
2. Increase `ATC_STR_RAT_P` until steering responds crisply
3. Add `ATC_STR_RAT_I` to eliminate steady-state error
4. Add `ATC_STR_RAT_D` if oscillation occurs (usually not needed)

### Speed Tuning

1. Set `ATC_ACCEL_MAX` and `ATC_DECEL_MAX` conservatively
2. Increase `ATC_SPEED_P` for faster response
3. Add `ATC_SPEED_I` for accurate speed hold
4. Use `ATC_SPEED_FF` for feed-forward compensation

### Common Issues

| Issue | Solution |
|-------|----------|
| Oscillating steering | Lower `ATC_STR_RAT_P` |
| Slow heading response | Increase `ATC_STR_ANG_P` |
| Speed hunting | Lower `ATC_SPEED_P`, add `ATC_SPEED_FF` |
| Slow acceleration | Increase `ATC_ACCEL_MAX` |
| Jerky stops | Increase `ATC_DECEL_MAX` filter |
