# Attitude Control

## Overview

ArduCopter uses `AC_AttitudeControl` for attitude stabilization and rate control.

**Files**:
- `libraries/AC_AttitudeControl/AC_AttitudeControl.h`
- `libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.h`
- `libraries/AC_AttitudeControl/AC_AttitudeControl_Heli.h`

## Controller Types

### Multicopter (AC_AttitudeControl_Multi)

Standard multicopter attitude control with PID rate loops.

### Helicopter (AC_AttitudeControl_Heli)

Traditional helicopter with collective pitch control.

## Control Methods

### Euler Angle + Rate Control

Most common for position modes:

```cpp
// Roll/pitch angle, yaw rate
void input_euler_angle_roll_pitch_euler_rate_yaw_rad(
    float euler_roll_angle_rad,
    float euler_pitch_angle_rad,
    float euler_yaw_rate_rads
);

// Roll/pitch/yaw angles
void input_euler_angle_roll_pitch_yaw_rad(
    float euler_roll_angle_rad,
    float euler_pitch_angle_rad,
    float euler_yaw_angle_rad,
    bool slew_yaw
);
```

### Body Frame Rate Control

Used in ACRO mode:

```cpp
void input_rate_bf_roll_pitch_yaw_rads(
    float roll_rate_bf_rads,
    float pitch_rate_bf_rads,
    float yaw_rate_bf_rads
);
```

### Thrust Vector Control

Used in position modes for pointing thrust:

```cpp
// Thrust vector with yaw rate
void input_thrust_vector_rate_heading_rads(
    const Vector3f& thrust_vector,
    float heading_rate_rads,
    bool slew_yaw
);

// Thrust vector with heading angle
void input_thrust_vector_heading_rads(
    const Vector3f& thrust_vector,
    float heading_angle_rad
);
```

## Rate Controllers

### PID Structure

Each axis has a PID rate controller:

```cpp
// Rate controller PIDs
AC_PID _pid_rate_roll;
AC_PID _pid_rate_pitch;
AC_PID _pid_rate_yaw;
```

### Rate Loop

```cpp
void rate_controller_run() {
    // Get rate targets
    Vector3f rate_target_rads = _rate_target_ang_vel_rads;

    // Get rate error
    Vector3f rate_error = rate_target_rads - gyro_latest;

    // PID calculation
    _motors.set_roll(pid_rate_roll.update_all(rate_target_rads.x, gyro.x, ...));
    _motors.set_pitch(pid_rate_pitch.update_all(rate_target_rads.y, gyro.y, ...));
    _motors.set_yaw(pid_rate_yaw.update_all(rate_target_rads.z, gyro.z, ...));
}
```

## Angle Limits

### Maximum Lean Angle

```cpp
// Get maximum lean angle (radians)
float lean_angle_max_rad() const;

// Get altitude hold max lean angle (may be different)
float get_althold_lean_angle_max_rad() const;
```

### Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ANGLE_MAX` | Max lean angle (centideg) | 3000 |
| `ATC_ACCEL_R_MAX` | Max roll acceleration | 110000 |
| `ATC_ACCEL_P_MAX` | Max pitch acceleration | 110000 |
| `ATC_ACCEL_Y_MAX` | Max yaw acceleration | 27000 |
| `ATC_RATE_R_MAX` | Max roll rate | 0 (unlimited) |
| `ATC_RATE_P_MAX` | Max pitch rate | 0 (unlimited) |
| `ATC_RATE_Y_MAX` | Max yaw rate | 0 (unlimited) |

## Throttle Control

### Setting Throttle

```cpp
// Set throttle output
void set_throttle_out(
    float throttle_in,      // 0-1 throttle
    bool apply_angle_boost, // Add boost for lean angle
    float filt_cutoff       // Filter cutoff frequency
);
```

### Throttle Hover

```cpp
// Get/set throttle for hover
float get_throttle_hover() const;
void set_throttle_hover(float throttle);

// Update hover throttle estimate
void update_throttle_hover();
```

### Angle Boost

Increases throttle to compensate for reduced vertical thrust when leaning:

```cpp
float get_throttle_boosted(float throttle_in) {
    // Boost = 1 / cos(lean_angle)
    float cos_tilt = ahrs.cos_pitch() * ahrs.cos_roll();
    return throttle_in / constrain_float(cos_tilt, 0.5f, 1.0f);
}
```

## Controller Reset

### I-term Reset

```cpp
// Full reset
void reset_rate_controller_I_terms();

// Smooth reset for transitions
void reset_rate_controller_I_terms_smoothly();
```

### Yaw Reset

```cpp
// Reset yaw target to current heading
void reset_yaw_target_and_rate();

// Shift yaw target by amount
void shift_ef_yaw_target_rad(float yaw_shift_rad);
```

## Relax Controllers

When landed or motors stopped:

```cpp
// Relax attitude controllers
void relax_attitude_controllers();

// Relax with specific rate decay
void relax_attitude_controllers(float decay_rate);
```

## Feedforward

### Rate Feedforward

```cpp
// Enable/disable body-frame feedforward
void set_bf_feedforward(bool enable);
bool get_bf_feedforward() const;
```

### Input Shaping

Controls command acceleration for smooth response:

```cpp
// Input shaping parameters
float _input_tc;  // Time constant for input shaping
```

## Stabilize Mode Helpers

### Pilot Input

```cpp
// Get pilot desired lean angles
void get_pilot_desired_lean_angles_rad(
    float &roll_out_rad,
    float &pitch_out_rad,
    float angle_max_rad,
    float angle_limit_rad
) const;

// Get pilot desired yaw rate
float get_pilot_desired_yaw_rate_rads() const;
```

### Expo Curves

Applied to pilot inputs:

```cpp
// Apply expo curve
float expo_curve(float input, float expo);
```

## Helicopter Specifics

### Collective Control

```cpp
// Set collective output (helicopter)
void set_throttle_out(float collective, bool apply_swash_limits);
```

### Flybar Control

```cpp
// Virtual flybar for rate damping
void virtual_flybar(float &roll_out, float &pitch_out, float &yaw_out,
                    float pitch_leak, float roll_leak);
```

## Usage Example

```cpp
void MyMode::run() {
    // Get pilot inputs
    float target_roll_rad, target_pitch_rad;
    get_pilot_desired_lean_angles_rad(
        target_roll_rad, target_pitch_rad,
        attitude_control->lean_angle_max_rad(),
        attitude_control->lean_angle_max_rad()
    );

    float target_yaw_rate = get_pilot_desired_yaw_rate_rads();

    // Run attitude controller
    attitude_control->input_euler_angle_roll_pitch_euler_rate_yaw_rad(
        target_roll_rad, target_pitch_rad, target_yaw_rate);

    // Set throttle
    attitude_control->set_throttle_out(throttle, true, g.throttle_filt);
}
```
