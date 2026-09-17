# Servo Control System

## Overview

The AntennaTracker controls two servos:
- **Pan (Yaw)**: Horizontal rotation (azimuth)
- **Tilt (Pitch)**: Vertical angle (elevation)

**File**: `servos.cpp`

## Servo Types

Three servo types are supported, configurable via parameters:

| Type | Value | Description |
|------|-------|-------------|
| POSITION | 0 | Standard position servo with PID |
| ONOFF | 1 | Simple on/off relay control |
| CR | 2 | Continuous rotation servo |

```cpp
enum ServoType {
    SERVO_TYPE_ONOFF = 0,
    SERVO_TYPE_CR = 1,
    SERVO_TYPE_POSITION = 2,
};
```

**Parameters**:
- `SERVO_YAW_TYPE` - Yaw servo type
- `SERVO_PITCH_TYPE` - Pitch servo type

## Servo Initialization

```cpp
void Tracker::init_servos() {
    // Enable auxiliary servos
    AP::srv().enable_aux_servos();

    // Assign default functions
    SRV_Channels::set_default_function(CH_YAW, SRV_Channel::k_tracker_yaw);
    SRV_Channels::set_default_function(CH_PITCH, SRV_Channel::k_tracker_pitch);

    // Set angle ranges
    // Yaw: +/- (YAW_RANGE/2) in centidegrees
    SRV_Channels::set_angle(SRV_Channel::k_tracker_yaw, g.yaw_range * 100/2);

    // Pitch: +/- (PITCH_MAX - PITCH_MIN)/2 in centidegrees
    SRV_Channels::set_angle(SRV_Channel::k_tracker_pitch,
                            (-g.pitch_min + g.pitch_max) * 100/2);

    // Initialize output filters
    yaw_servo_out_filt.set_cutoff_frequency(SERVO_OUT_FILT_HZ);
    pitch_servo_out_filt.set_cutoff_frequency(SERVO_OUT_FILT_HZ);
}
```

## Position Servo Control

### Pitch Position Servo

```cpp
void Tracker::update_pitch_position_servo() {
    int32_t pitch_min_cd = g.pitch_min * 100;
    int32_t pitch_max_cd = g.pitch_max * 100;

    // Calculate new servo position using PID
    float new_servo_out = SRV_Channels::get_output_scaled(SRV_Channel::k_tracker_pitch)
                        + g.pidPitch2Srv.update_error(nav_status.angle_error_pitch, G_Dt);

    // Apply position limits
    if (new_servo_out <= pitch_min_cd) {
        new_servo_out = pitch_min_cd;
        g.pidPitch2Srv.reset_I();  // Prevent integrator windup
    }
    if (new_servo_out >= pitch_max_cd) {
        new_servo_out = pitch_max_cd;
        g.pidPitch2Srv.reset_I();
    }

    SRV_Channels::set_output_scaled(SRV_Channel::k_tracker_pitch, new_servo_out);

    // Update filter for direction calculations
    pitch_servo_out_filt.apply(new_servo_out, G_Dt);
}
```

### Yaw Position Servo

```cpp
void Tracker::update_yaw_position_servo() {
    int32_t yaw_limit_cd = g.yaw_range * 100 / 2;

    // PID-based servo change
    float servo_change = g.pidYaw2Srv.update_error(nav_status.angle_error_yaw, G_Dt);
    servo_change = constrain_float(servo_change, -18000, 18000);

    float new_servo_out = constrain_float(
        SRV_Channels::get_output_scaled(SRV_Channel::k_tracker_yaw) + servo_change,
        -18000, 18000);

    // Apply position limits
    if (new_servo_out <= -yaw_limit_cd) {
        new_servo_out = -yaw_limit_cd;
        g.pidYaw2Srv.reset_I();
    }
    if (new_servo_out >= yaw_limit_cd) {
        new_servo_out = yaw_limit_cd;
        g.pidYaw2Srv.reset_I();
    }

    SRV_Channels::set_output_scaled(SRV_Channel::k_tracker_yaw, new_servo_out);
    yaw_servo_out_filt.apply(new_servo_out, G_Dt);
}
```

## On/Off Servo Control

For relay-based servo systems with simple on/off control.

### Pitch On/Off Servo

```cpp
void Tracker::update_pitch_onoff_servo(float pitch) const {
    // Calculate acceptable error based on rate and minimum time
    float acceptable_error = g.onoff_pitch_rate * g.onoff_pitch_mintime;

    if (fabsf(nav_status.angle_error_pitch) < acceptable_error) {
        // Within deadband - stop movement
        SRV_Channels::set_output_scaled(SRV_Channel::k_tracker_pitch, 0);
    } else if ((nav_status.angle_error_pitch > 0) && (pitch*100 > pitch_min_cd)) {
        // Pointing too low - push servo up
        SRV_Channels::set_output_scaled(SRV_Channel::k_tracker_pitch, -9000);
    } else if (pitch*100 < pitch_max_cd) {
        // Pointing too high - push servo down
        SRV_Channels::set_output_scaled(SRV_Channel::k_tracker_pitch, 9000);
    }
}
```

### Yaw On/Off Servo

```cpp
void Tracker::update_yaw_onoff_servo(float yaw) const {
    float acceptable_error = g.onoff_yaw_rate * g.onoff_yaw_mintime;

    if (fabsf(nav_status.angle_error_yaw * 0.01f) < acceptable_error) {
        // Within deadband - stop movement
        SRV_Channels::set_output_scaled(SRV_Channel::k_tracker_yaw, 0);
    } else if (nav_status.angle_error_yaw * 0.01f > 0) {
        // Counter-clockwise of target - move clockwise
        SRV_Channels::set_output_scaled(SRV_Channel::k_tracker_yaw, 18000);
    } else {
        // Clockwise of target - move counter-clockwise
        SRV_Channels::set_output_scaled(SRV_Channel::k_tracker_yaw, -18000);
    }
}
```

## Continuous Rotation Servo Control

For servos that rotate continuously without position feedback.

### Pitch CR Servo

```cpp
void Tracker::update_pitch_cr_servo(float pitch) {
    float pitch_out = constrain_float(
        g.pidPitch2Srv.update_error(nav_status.angle_error_pitch, G_Dt),
        -(-g.pitch_min + g.pitch_max) * 100/2,
        (-g.pitch_min + g.pitch_max) * 100/2);
    SRV_Channels::set_output_scaled(SRV_Channel::k_tracker_pitch, pitch_out);
}
```

### Yaw CR Servo

```cpp
void Tracker::update_yaw_cr_servo(float yaw) {
    float yaw_out = constrain_float(
        -g.pidYaw2Srv.update_error(nav_status.angle_error_yaw, G_Dt),
        -g.yaw_range * 100/2,
        g.yaw_range * 100/2);
    SRV_Channels::set_output_scaled(SRV_Channel::k_tracker_yaw, yaw_out);
}
```

## PID Controllers

### Configuration

```cpp
// In Parameters.h
AC_PID pidPitch2Srv;
AC_PID pidYaw2Srv;

// Default values (P, I, D, FF, IMAX, FLTT, FLTE, FLTD, SMAX)
pidPitch2Srv(0.2, 0.0f, 0.05f, 0.02f, 4000.0f, 0.0f, 0.0f, 0.0f, 0.1f);
pidYaw2Srv  (0.2, 0.0f, 0.05f, 0.02f, 4000.0f, 0.0f, 0.0f, 0.0f, 0.1f);
```

### PID Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `PITCH2SRV_P` | Pitch P gain | 0.2 |
| `PITCH2SRV_I` | Pitch I gain | 0.0 |
| `PITCH2SRV_D` | Pitch D gain | 0.05 |
| `PITCH2SRV_IMAX` | Pitch I max | 4000 |
| `YAW2SRV_P` | Yaw P gain | 0.2 |
| `YAW2SRV_I` | Yaw I gain | 0.0 |
| `YAW2SRV_D` | Yaw D gain | 0.05 |
| `YAW2SRV_IMAX` | Yaw I max | 4000 |

## Servo Output Filtering

Low-pass filters smooth servo output for calculating direction:

```cpp
LowPassFilterFloat yaw_servo_out_filt;
LowPassFilterFloat pitch_servo_out_filt;

// Cutoff frequency
#define SERVO_OUT_FILT_HZ 2
```

## Slew Rate Limiting

The `YAW_SLEW_TIME` and `PITCH_SLEW_TIME` parameters limit servo movement rate:

```cpp
// Time for full range sweep (seconds)
// 0 = unlimited speed
AP_Float yaw_slew_time;   // Default: 2
AP_Float pitch_slew_time; // Default: 2
```

## Hardware Configuration

### Default Servo Channels
- Channel 5: Yaw (k_tracker_yaw)
- Channel 6: Pitch (k_tracker_pitch)

### Servo Range Setup
```
# Yaw servo (example for HS-645MG with 2:1 gearing)
SERVO5_MIN = 680
SERVO5_MAX = 2380
SERVO5_REVERSED = 1  (if needed)

# Pitch servo (example)
SERVO6_MIN = 640
SERVO6_MAX = 2540
SERVO6_REVERSED = 1  (if needed)
```

## Servo Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `SERVO_YAW_TYPE` | Yaw servo type (0=Pos, 1=OnOff, 2=CR) | 0 |
| `SERVO_PITCH_TYPE` | Pitch servo type | 0 |
| `YAW_RANGE` | Total yaw movement (deg) | 360 |
| `PITCH_MIN` | Minimum pitch angle (deg) | -90 |
| `PITCH_MAX` | Maximum pitch angle (deg) | 90 |
| `YAW_SLEW_TIME` | Time for full yaw sweep (s) | 2 |
| `PITCH_SLEW_TIME` | Time for full pitch sweep (s) | 2 |
| `ONOFF_YAW_RATE` | On/off yaw rate (deg/s) | 9 |
| `ONOFF_PITCH_RATE` | On/off pitch rate (deg/s) | 1 |
| `ONOFF_YAW_MINT` | On/off yaw min time (s) | 0.1 |
| `ONOFF_PITCH_MINT` | On/off pitch min time (s) | 0.1 |
| `YAW_TRIM` | Yaw offset (deg) | 0 |
| `PITCH_TRIM` | Pitch offset (deg) | 0 |

## Disarm/Stop Behavior

Controlled by `SAFE_DISARM_PWM`:
- `0`: Output zero PWM
- `1`: Output trim PWM
