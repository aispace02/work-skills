# Thruster Configuration

## AP_Motors6DOF

ArduSub uses `AP_Motors6DOF` for 6 degree-of-freedom thruster control.

**Files**: `libraries/AP_Motors/AP_Motors6DOF.h`, `libraries/AP_Motors/AP_Motors6DOF.cpp`

## Frame Types

| Value | Name | Motors | Description |
|-------|------|--------|-------------|
| 0 | SUB_FRAME_BLUEROV1 | 6 | Original BlueROV design |
| 1 | SUB_FRAME_VECTORED | 6 | BlueROV2 (default) |
| 2 | SUB_FRAME_VECTORED_6DOF | 8 | Full 6DOF with 8 thrusters |
| 3 | SUB_FRAME_VECTORED_6DOF_90DEG | 8 | 6DOF 90-degree orientation |
| 4 | SUB_FRAME_SIMPLEROV_3 | 3 | Simple 3-motor ROV |
| 5 | SUB_FRAME_SIMPLEROV_4 | 4 | Simple 4-motor ROV |
| 6 | SUB_FRAME_SIMPLEROV_5 | 5 | Simple 5-motor ROV |
| 7 | SUB_FRAME_CUSTOM | - | User-defined configuration |

## Motor Factor Matrix

Each motor has factors for 6 axes:

```cpp
// add_motor_raw_6dof(motor_num, roll_fac, pitch_fac, yaw_fac, throttle_fac, forward_fac, lateral_fac, test_order)
```

### BlueROV2 Vectored (Frame 1)

```
Motor 1: Roll=0,    Pitch=0,    Yaw=+1,   Throttle=0,    Forward=-1, Lateral=+1
Motor 2: Roll=0,    Pitch=0,    Yaw=-1,   Throttle=0,    Forward=-1, Lateral=-1
Motor 3: Roll=0,    Pitch=0,    Yaw=-1,   Throttle=0,    Forward=+1, Lateral=+1
Motor 4: Roll=0,    Pitch=0,    Yaw=+1,   Throttle=0,    Forward=+1, Lateral=-1
Motor 5: Roll=+1,   Pitch=0,    Yaw=0,    Throttle=-1,   Forward=0,  Lateral=0
Motor 6: Roll=-1,   Pitch=0,    Yaw=0,    Throttle=-1,   Forward=0,  Lateral=0
```

### Vectored 6DOF (Frame 2)

Full 6DOF control with 8 thrusters:

```cpp
case SUB_FRAME_VECTORED_6DOF:
    add_motor_raw_6dof(MOT_1, 0, 0, 1.0f, 0, -1.0f, 1.0f, 1);
    add_motor_raw_6dof(MOT_2, 0, 0, -1.0f, 0, -1.0f, -1.0f, 2);
    add_motor_raw_6dof(MOT_3, 0, 0, -1.0f, 0, 1.0f, 1.0f, 3);
    add_motor_raw_6dof(MOT_4, 0, 0, 1.0f, 0, 1.0f, -1.0f, 4);
    add_motor_raw_6dof(MOT_5, 1.0f, -1.0f, 0, -1.0f, 0, 0, 5);
    add_motor_raw_6dof(MOT_6, -1.0f, -1.0f, 0, -1.0f, 0, 0, 6);
    add_motor_raw_6dof(MOT_7, 1.0f, 1.0f, 0, -1.0f, 0, 0, 7);
    add_motor_raw_6dof(MOT_8, -1.0f, 1.0f, 0, -1.0f, 0, 0, 8);
    break;
```

## Motor Direction

Each motor can be reversed without changing wiring:

```cpp
// Parameters MOT_1_DIRECTION through MOT_12_DIRECTION
// Values: 1 = normal, -1 = reverse
AP_GROUPINFO("1_DIRECTION", 1, AP_Motors6DOF, _motor_reverse[0], 1),
```

## Output Mixing

### Stabilization Output

```cpp
void AP_Motors6DOF::output_armed_stabilizing() {
    // Get control inputs
    float roll_thrust = _roll_in;
    float pitch_thrust = _pitch_in;
    float yaw_thrust = _yaw_in;
    float throttle_thrust = get_throttle();
    float forward_thrust = _forward_in;
    float lateral_thrust = _lateral_in;

    // Mix to motors
    for (int i = 0; i < AP_MOTORS_MAX_NUM_MOTORS; i++) {
        if (motor_enabled[i]) {
            _thrust_rpyt_out[i] = roll_thrust * _roll_factor[i]
                                + pitch_thrust * _pitch_factor[i]
                                + yaw_thrust * _yaw_factor[i]
                                + throttle_thrust * _throttle_factor[i]
                                + forward_thrust * _forward_factor[i]
                                + lateral_thrust * _lateral_factor[i];
        }
    }

    // Limit and output
    limit_output();
    output_to_motors();
}
```

### Forward/Vertical Coupling

Compensates for pitch changes during forward thrust:

```cpp
// @Param: FV_CPLNG_K
// @Description: Used to decouple pitch from forward/vertical motion
// @Range: 0.0 1.5
AP_GROUPINFO("FV_CPLNG_K", 9, AP_Motors6DOF, _forwardVerticalCouplingFactor, 1.0),
```

## Motor Test

Test individual motors via MAVLink:

```cpp
bool Sub::handle_do_motor_test(mavlink_command_int_t command) {
    float motor_number = command.param1;
    float throttle_type = command.param2;
    float throttle = command.param3;

    if (throttle_type == MOTOR_TEST_THROTTLE_PWM) {
        return motors.output_test_num(motor_number, throttle);
    }

    if (throttle_type == MOTOR_TEST_THROTTLE_PERCENT) {
        throttle = constrain_float(throttle, 0.0f, 100.0f);
        throttle = rc_min + throttle * 0.01f * (rc_max - rc_min);
        return motors.output_test_num(motor_number, throttle);
    }

    return false;
}
```

## Motor Detection Mode

Automatically detects motor directions:

```cpp
// MOTOR_DETECT mode (20)
// Motors controlled directly via MAVLink DO_MOTOR_TEST commands
// User interface guides through detection process
```

## PWM Output

### Thrust to PWM Conversion

```cpp
int16_t AP_Motors6DOF::calc_thrust_to_pwm(float thrust_in) const {
    // thrust_in: -1 to +1
    // Returns: PWM value (typically 1100-1900)

    thrust_in = constrain_float(thrust_in, -1.0f, 1.0f);

    // Apply motor direction
    // Apply deadzone
    // Scale to PWM range

    return pwm_out;
}
```

### Output Limits

```cpp
// Throttle limiting near surface
void set_max_throttle(float max_throttle) {
    _max_throttle = max_throttle;
}

// Current limiting
float get_current_limit_max_throttle() {
    // Reduce thrust if current exceeds limit
    return _output_limited;
}
```

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `FRAME_CONFIG` | Frame type | 1 |
| `MOT_PWM_MIN` | Minimum PWM output | 1100 |
| `MOT_PWM_MAX` | Maximum PWM output | 1900 |
| `MOT_1_DIRECTION` | Motor 1 direction | 1 |
| `MOT_FV_CPLNG_K` | Forward/vertical coupling | 1.0 |

## Adding a Custom Frame

```cpp
case SUB_FRAME_CUSTOM:
    _frame_class_string = "CUSTOM";
    // Define motor factors
    //                    Motor#  Roll   Pitch  Yaw    Throt  Fwd    Lat    Order
    add_motor_raw_6dof(MOT_1, 0.0f, 0.0f, 1.0f, 0.0f, -1.0f, 1.0f, 1);
    add_motor_raw_6dof(MOT_2, 0.0f, 0.0f, -1.0f, 0.0f, -1.0f, -1.0f, 2);
    // ... add more motors
    break;
```

## Servo Functions

Thrusters use servo functions 33-44:

```cpp
SERVO1_FUNCTION = 33  // Motor 1
SERVO2_FUNCTION = 34  // Motor 2
SERVO3_FUNCTION = 35  // Motor 3
// ... etc
```

## Input Channels

Motors receive commands through these channels:

```cpp
motors.set_forward(channel_forward->norm_input());   // -1 to +1
motors.set_lateral(channel_lateral->norm_input());   // -1 to +1
// Throttle via attitude_control->set_throttle_out()
// Roll/pitch/yaw via attitude_control
```
