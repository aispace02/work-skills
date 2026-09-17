# Attitude Controllers

## Overview

**Location**: `libraries/APM_Control/`

Plane uses separate PID controllers for roll, pitch, and yaw.

## Controller Classes

| Controller | File | Purpose |
|------------|------|---------|
| AP_RollController | AP_RollController.h | Roll rate + angle |
| AP_PitchController | AP_PitchController.h | Pitch rate + angle |
| AP_YawController | AP_YawController.h | Yaw damping |
| AP_SteerController | AP_SteerController.h | Ground steering |

## AP_RollController

```cpp
class AP_RollController {
public:
    // Get servo output for roll stabilization
    // Returns -4500 to +4500
    int32_t get_servo_out(
        int32_t angle_err,       // Angle error in centidegrees
        float scaler,            // Speed scaling factor
        bool disable_integrator  // Disable I term
    );

    // Get rate-only output
    float get_rate_out(
        float desired_rate,      // Desired roll rate (deg/s)
        float scaler
    );

    // Reset integrator
    void reset_I();
};
```

### Usage

```cpp
void Plane::stabilize_roll() {
    // Calculate angle error
    int32_t angle_err = nav_roll_cd - ahrs.roll_sensor;

    // Get servo output
    float scaler = get_speed_scaler();
    int32_t out = rollController.get_servo_out(
        angle_err,
        scaler,
        false
    );

    // Apply to servo
    SRV_Channels::set_output_scaled(SRV_Channel::k_aileron, out);
}
```

### Parameters (RLL_)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `RLL2SRV_P` | Proportional gain | 1.0 |
| `RLL2SRV_I` | Integral gain | 0.3 |
| `RLL2SRV_D` | Derivative gain | 0.08 |
| `RLL2SRV_FF` | Feed forward | 0.4 |
| `RLL2SRV_RMAX` | Max roll rate (deg/s) | 75 |
| `RLL2SRV_IMAX` | Max integrator | 3000 |

## AP_PitchController

```cpp
class AP_PitchController {
public:
    // Get servo output for pitch stabilization
    int32_t get_servo_out(
        int32_t angle_err,       // Angle error in centidegrees
        float scaler,
        bool disable_integrator
    );

    // Get rate-only output
    float get_rate_out(
        float desired_rate,      // Desired pitch rate (deg/s)
        float scaler
    );
};
```

### Parameters (PTCH_)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `PTCH2SRV_P` | Proportional gain | 1.0 |
| `PTCH2SRV_I` | Integral gain | 0.3 |
| `PTCH2SRV_D` | Derivative gain | 0.08 |
| `PTCH2SRV_FF` | Feed forward | 0.4 |
| `PTCH2SRV_RMAX_UP` | Max pitch up rate (deg/s) | 75 |
| `PTCH2SRV_RMAX_DN` | Max pitch down rate (deg/s) | 75 |
| `PTCH2SRV_IMAX` | Max integrator | 3000 |

## AP_YawController

Yaw damper to reduce Dutch roll oscillation.

```cpp
class AP_YawController {
public:
    // Get rudder output for yaw damping
    int32_t get_servo_out(
        float scaler,
        bool disable_integrator
    );

    // Turn coordination output
    float get_coordination_out(
        float bank_angle         // Current bank angle (rad)
    );
};
```

### Parameters (YAW_)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `YAW2SRV_SLIP` | Sideslip gain | 0 |
| `YAW2SRV_INT` | Integrator gain | 0 |
| `YAW2SRV_DAMP` | Damping gain | 0 |
| `YAW2SRV_RLL` | Roll coordination gain | 1.0 |
| `YAW2SRV_IMAX` | Max integrator | 1500 |

## Speed Scaling

Controllers scale their output based on airspeed:

```cpp
float Plane::get_speed_scaler() {
    float aspeed;
    if (!ahrs.airspeed_estimate(&aspeed)) {
        aspeed = aparm.airspeed_cruise_cm * 0.01f;
    }

    // Scale factor = reference_speed / actual_speed
    float scaler = g.scaling_speed / aspeed;
    return constrain_float(scaler, 0.5f, 2.0f);
}
```

**Lower speed** → larger control deflections needed
**Higher speed** → smaller control deflections needed

## AutoTune

**Mode**: `AUTOTUNE` (mode 8)

Automatically tunes roll and pitch PID gains.

```cpp
// AutoTune adjusts these parameters:
RLL2SRV_P, RLL2SRV_I, RLL2SRV_D
PTCH2SRV_P, PTCH2SRV_I, PTCH2SRV_D
```

### How AutoTune Works

1. Enter AUTOTUNE mode
2. Fly level, then make a sharp roll command
3. AutoTune injects test inputs and measures response
4. Iteratively adjusts gains for optimal response
5. Repeat for pitch axis
6. Land and save parameters

## Attitude Control Flow

```
Desired Angles (nav_roll_cd, nav_pitch_cd)
        │
        ▼
Angle Error = desired - actual
        │
        ▼
    Controller
   ┌─────────────────┐
   │ P × angle_err   │
   │ + I × ∫error dt │
   │ + D × rate      │
   │ + FF × rate_dem │
   └─────────────────┘
        │
        ▼
   Speed Scaling
        │
        ▼
   Servo Output
   (-4500 to +4500)
```

## Common Tuning Issues

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Oscillation | P too high | Reduce P, increase D |
| Slow response | P too low | Increase P |
| Drift in wind | I too low | Increase I |
| Windup/overshoot | I too high | Reduce I or IMAX |
| Jerky response | D too high | Reduce D |
| Can't reach attitude | RMAX too low | Increase RMAX |

## Ground Steering

For taxiing and takeoff roll:

```cpp
class AP_SteerController {
public:
    int32_t get_steering_out(
        float heading_error,     // Heading error (deg)
        bool locked_course       // Lock to course vs heading
    );
};
```

### Parameters (STEER_)

| Parameter | Description |
|-----------|-------------|
| `STEER2SRV_P` | Heading error gain |
| `STEER2SRV_I` | Integrator gain |
| `STEER2SRV_D` | Rate damping |
| `STEER2SRV_TCONST` | Time constant |
