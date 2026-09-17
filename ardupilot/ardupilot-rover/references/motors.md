# Rover Motor Control

## AP_MotorsUGV

**Location**: `libraries/AP_Motors/AP_MotorsUGV.h`

Motor mixing and output for Unmanned Ground Vehicles.

## Frame Types

```cpp
// FRAME_CLASS parameter
enum frame_class {
    FRAME_UNDEFINED = 0,
    FRAME_ROVER = 1,      // Standard land rover
    FRAME_BOAT = 2,       // Watercraft
    FRAME_BALANCEBOT = 3  // Self-balancing
};

// FRAME_TYPE parameter - motor mixing
enum frame_type {
    FRAME_TYPE_UNDEFINED = 0,
    FRAME_TYPE_OMNI3 = 1,      // Omnidirectional 3-motor
    FRAME_TYPE_OMNIX = 2,      // Omni X configuration
    FRAME_TYPE_OMNIPLUS = 3,   // Omni + configuration
};
```

## Core API

### Setting Outputs

```cpp
// Primary outputs
void set_throttle(float throttle);    // -100 to +100
void set_steering(float steering);    // -4500 to +4500 (centidegrees)
void set_lateral(float lateral);      // -100 to +100 (boats/omni)

// Walking robots
void set_roll(float roll);
void set_pitch(float pitch);
void set_walking_height(float height);

// Sailboat
void set_mainsail(float mainsail);    // 0 to 100
void set_wingsail(float wingsail);    // -100 to +100
void set_mast_rotation(float rotation);
```

### Motor State Queries

```cpp
// Limits (for integrator windup prevention)
struct {
    bool steer_left;      // Left steering at limit
    bool steer_right;     // Right steering at limit
    bool throttle_lower;  // Min throttle limit
    bool throttle_upper;  // Max throttle limit
} limit;

// Frame info
bool have_skid_steering() const;
bool have_vectored_thrust() const;
bool boat_vectored_thrust_is_zero() const;

// Output state
float get_throttle() const;
float get_steering() const;
float get_lateral() const;
bool pre_arm_check(char *failure_msg, uint8_t failure_msg_len) const;
```

### Special Methods

```cpp
// Failsafe
void set_throttle_limits_bypass(bool bypass);
void lock_servos();

// Arming
void armed(bool arm);
bool armed() const;

// Motor test
bool motor_test(AP_MotorsUGV::motor_test_order motor, uint8_t type, float value, float timeout);
```

## Motor Output Channels

| Function | Servo Function | Description |
|----------|---------------|-------------|
| Throttle | MOTOR1 (70) | Main throttle |
| ThrottleLeft | MOTOR2 (71) | Left motor (skid steer) |
| ThrottleRight | MOTOR3 (72) | Right motor (skid steer) |
| Steering | GROUNDSTEER (26) | Steering servo |
| Lateral | MOTOR4 (73) | Lateral thrust |
| MainSail | MAINSAIL (89) | Sailboat mainsail |
| WingSail | WINGSAIL (90) | Sailboat wingsail |

## Mixing Modes

### Skid Steering (Differential Drive)

```cpp
// Two motors, steering by speed difference
// ThrottleLeft and ThrottleRight
left_output  = throttle + steering
right_output = throttle - steering
```

### Steering + Throttle (Car-like)

```cpp
// Separate steering servo and throttle motor
// Steering servo, Throttle motor
steering_servo = steering_input
throttle_motor = throttle_input
```

### Omnidirectional

```cpp
// 3 or 4 motors for holonomic motion
// Combines throttle, steering, and lateral
motor_n = f(throttle, steering, lateral, motor_angle)
```

## Usage Patterns

### Basic Motor Control

```cpp
void ModeManual::update() {
    float steering, throttle;
    get_pilot_desired_steering_and_throttle(steering, throttle);

    g2.motors.set_steering(steering);
    g2.motors.set_throttle(throttle);
}
```

### With Limits Check

```cpp
void calculate_steering() {
    float steering = g2.attitude_control.get_steering_out_rate(
        desired_rate,
        g2.motors.limit.steer_left,   // Pass limits
        g2.motors.limit.steer_right,
        rover.G_Dt
    );
    g2.motors.set_steering(steering);
}
```

### Boat with Lateral

```cpp
void ModeManual::update() {
    float steering, throttle;
    get_pilot_desired_steering_and_throttle(steering, throttle);

    float lateral;
    get_pilot_desired_lateral(lateral);

    g2.motors.set_steering(steering);
    g2.motors.set_throttle(throttle);
    g2.motors.set_lateral(lateral);
}
```

### Sailboat

```cpp
void Sailboat::update() {
    // Calculate sail positions
    float mainsail = calc_mainsail();
    float wingsail = calc_wingsail();

    g2.motors.set_mainsail(mainsail);
    g2.motors.set_wingsail(wingsail);

    // Motor assist for slow speeds/tacking
    if (motor_assist_needed()) {
        g2.motors.set_throttle(throttle);
    }
}
```

## Parameters (MOT_)

| Parameter | Description | Range |
|-----------|-------------|-------|
| `MOT_PWM_TYPE` | PWM output type | 0=Normal, 1=OneShot, ... |
| `MOT_SAFE_DISARM` | Disarm behavior | 0=No PWM, 1=Zero PWM |
| `MOT_SLEWRATE` | Throttle slew rate | % per second |
| `MOT_THST_EXPO` | Thrust curve expo | 0 to 1 |
| `MOT_SPD_SCA_BASE` | Speed scaling base | m/s |
| `MOT_VEC_THR_BASE` | Vector thrust base | % |
| `MOT_THST_ASYM` | Asymmetric thrust | 0=Symmetric, 1=Asym |

## Initialization

```cpp
// Called during Rover::init_ardupilot()
void AP_MotorsUGV::init(uint8_t frame_type) {
    // Setup servo functions based on frame type
    add_motor(AP_MOTORS_MOT_1, ...);
    add_motor(AP_MOTORS_MOT_2, ...);
    // etc.

    // Set PWM ranges
    SRV_Channels::set_output_min_max(SRV_Channel::k_throttle, ...);
}
```

## Output Update Flow

```cpp
// Called at 400Hz from Rover::set_servos()
void Rover::set_servos() {
    // Output motor commands
    g2.motors.output(arming.is_armed());

    // Also update sailboat if applicable
    g2.sailboat.output_mainsail();
}

void AP_MotorsUGV::output(bool armed) {
    // Apply mixing
    output_throttle_and_steering(throttle, steering, lateral);

    // Output to servos
    SRV_Channels::set_output_scaled(...);
}
```

## Safety Features

### Throttle Limits

```cpp
// Throttle is limited based on:
// - Parameter limits (MOT_THR_MIN, MOT_THR_MAX)
// - Failsafe state
// - Arming state
```

### Pre-arm Checks

```cpp
bool AP_MotorsUGV::pre_arm_check(char *failure_msg, uint8_t len) const {
    // Check motor outputs are configured
    // Check ESC calibration
    // Check throttle limits
}
```

### Motor Test

```cpp
// For testing individual motors
g2.motors.motor_test(
    AP_MotorsUGV::motor_test_order::MOTOR_TEST_THROTTLE,
    1,     // type (1=percent)
    50.0f, // value (50%)
    2.0f   // timeout (2 seconds)
);
```
