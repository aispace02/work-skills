# Motor Configuration

## AP_Motors Classes

**Files**:
- `libraries/AP_Motors/AP_Motors.h` - Base class
- `libraries/AP_Motors/AP_MotorsMulticopter.h` - Multicopter base
- `libraries/AP_Motors/AP_MotorsMatrix.h` - Standard multicopter
- `libraries/AP_Motors/AP_MotorsHeli.h` - Helicopter base

## Frame Types

### Multicopter Frames

| Frame Class | Description |
|-------------|-------------|
| QUAD | 4 motors |
| HEXA | 6 motors |
| OCTA | 8 motors |
| OCTAQUAD | 8 motors (coaxial) |
| Y6 | 6 motors (Y6) |
| TRI | 3 motors + servo |
| COAX | 2 motors (coaxial) |
| SINGLE | 1 motor + 4 servos |

### Frame Types (within class)

| Type | Description |
|------|-------------|
| PLUS | + configuration |
| X | X configuration |
| V | V configuration |
| H | H configuration |
| VTAIL | V-tail |
| ATAIL | A-tail |
| BETAFLIGHTX | BetaFlight X |
| DJIASSISTANCE | DJI compatible |
| CWXFRONT | CW X with front motor |

## Motor Mixing

### Matrix Motors

```cpp
void AP_MotorsMatrix::add_motor_raw(
    int8_t motor_num,
    float roll_fac,   // Roll factor
    float pitch_fac,  // Pitch factor
    float yaw_fac,    // Yaw factor
    uint8_t testing_order
);
```

### Example: Quad X

```cpp
// Motors numbered 1-4 starting front-right, going clockwise
add_motor(AP_MOTORS_MOT_1,  45, AP_MOTORS_MATRIX_YAW_FACTOR_CCW, 1);  // Front right
add_motor(AP_MOTORS_MOT_2, -135, AP_MOTORS_MATRIX_YAW_FACTOR_CCW, 3); // Back left
add_motor(AP_MOTORS_MOT_3, -45, AP_MOTORS_MATRIX_YAW_FACTOR_CW, 4);   // Front left
add_motor(AP_MOTORS_MOT_4, 135, AP_MOTORS_MATRIX_YAW_FACTOR_CW, 2);   // Back right
```

## Motor Output

### Setting Outputs

```cpp
// Set roll/pitch/yaw/throttle demands
void set_roll(float roll_in);      // -1 to +1
void set_pitch(float pitch_in);    // -1 to +1
void set_yaw(float yaw_in);        // -1 to +1
void set_throttle(float throttle); // 0 to 1
```

### Output Process

```cpp
void AP_MotorsMulticopter::output() {
    // Check if armed
    if (!armed()) {
        output_min();
        return;
    }

    // Calculate outputs
    output_armed_stabilizing();

    // Limit and output
    output_to_motors();
}
```

## Spool States

```cpp
enum class SpoolState {
    SHUT_DOWN,        // Motors stopped
    GROUND_IDLE,      // Low speed spin (landed)
    SPOOLING_UP,      // Transitioning to unlimited
    THROTTLE_UNLIMITED, // Normal flight
    SPOOLING_DOWN     // Transitioning to idle
};

// Get current state
SpoolState get_spool_state() const;

// Set desired state
void set_desired_spool_state(DesiredSpoolState spool);
```

## Throttle Management

### Throttle Limits

```cpp
// Check throttle limits
struct {
    bool roll;           // Roll limit reached
    bool pitch;          // Pitch limit reached
    bool yaw;            // Yaw limit reached
    bool throttle_lower; // At min throttle
    bool throttle_upper; // At max throttle
} limit;
```

### Throttle Slew

```cpp
// Set throttle slew rate
void set_throttle_slew_rate(float slew_rate);
```

## ESC Calibration

### Calibration Modes

```cpp
enum ESCCalibrationModes {
    ESCCAL_NONE = 0,
    ESCCAL_PASSTHROUGH_IF_THROTTLE_HIGH = 1,
    ESCCAL_PASSTHROUGH_ALWAYS = 2,
    ESCCAL_AUTO = 3,
    ESCCAL_DISABLED = 9,
};
```

### Calibration Process

```cpp
void Copter::esc_calibration_startup_check();
void Copter::esc_calibration_passthrough();
void Copter::esc_calibration_auto();
```

## Motor Test

```cpp
// Test single motor
bool output_test_num(uint8_t motor, float throttle);

// Test sequence
MAV_RESULT mavlink_motor_test_start(
    const GCS_MAVLINK &gcs_chan,
    uint8_t motor_seq,
    uint8_t throttle_type,
    float throttle_value,
    float timeout_sec,
    uint8_t motor_count
);
```

## Parameters

### Motor Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `MOT_SPIN_ARM` | Spin when armed (0-1) | 0.1 |
| `MOT_SPIN_MIN` | Minimum spin (0-1) | 0.15 |
| `MOT_SPIN_MAX` | Maximum spin (0-1) | 0.95 |
| `MOT_PWM_TYPE` | PWM output type | 0 |
| `MOT_PWM_MIN` | Minimum PWM | 1000 |
| `MOT_PWM_MAX` | Maximum PWM | 2000 |
| `MOT_THST_EXPO` | Thrust curve expo | 0.65 |
| `MOT_THST_HOVER` | Throttle for hover | 0.35 |
| `MOT_BAT_VOLT_MAX` | Max battery voltage | 0 |
| `MOT_BAT_VOLT_MIN` | Min battery voltage | 0 |
| `MOT_YAW_HEADROOM` | Yaw headroom | 200 |

### Frame Parameters

| Parameter | Description |
|-----------|-------------|
| `FRAME_CLASS` | Frame class (Quad, Hexa, etc) |
| `FRAME_TYPE` | Frame type (X, +, etc) |

## PWM Output Types

```cpp
enum pwm_output_type {
    PWM_TYPE_NORMAL = 0,
    PWM_TYPE_ONESHOT = 1,
    PWM_TYPE_ONESHOT125 = 2,
    PWM_TYPE_BRUSHED = 3,
    PWM_TYPE_DSHOT150 = 4,
    PWM_TYPE_DSHOT300 = 5,
    PWM_TYPE_DSHOT600 = 6,
    PWM_TYPE_DSHOT1200 = 7,
    PWM_TYPE_PWM_RANGE = 8,
};
```

## Thrust Linearization

### Battery Compensation

```cpp
// Compensate for battery voltage
void update_battery_resistance();
float get_resistance_compensation(float throttle);
```

### Thrust Curve

```cpp
// Apply thrust curve (expo)
float thrust_to_actuator(float thrust);
float actuator_to_thrust(float actuator);
```

## Helicopter Specifics

### Collective Control

```cpp
// Set collective pitch
void set_collective(float collective);

// RSC (Rotor Speed Control)
void set_desired_rotor_speed(float speed);
float get_desired_rotor_speed() const;
```

### Swashplate

```cpp
// Swashplate types
enum SwashType {
    SWASH_H3 = 0,
    SWASH_H1 = 1,
    SWASH_H3_140 = 2,
    SWASH_H3_120 = 3,
    SWASH_H4_90 = 4,
    SWASH_H4_45 = 5,
};
```

## Usage Example

```cpp
void Copter::motors_output(bool full_push) {
    // Check motor interlock
    if (ap.motor_interlock_switch) {
        motors->set_interlock(true);
    }

    // Call motor output
    motors->output(full_push);
}
```
