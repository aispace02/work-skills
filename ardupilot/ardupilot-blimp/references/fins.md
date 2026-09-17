# Fin Control System

## Overview

Blimp uses oscillating fins rather than traditional spinning propellers. The `Fins` class converts movement commands into sinusoidal servo positions.

**Files**: `Blimp/Fins.h`, `Blimp/Fins.cpp`

## Fin Configuration

### Default Setup (Airfish)

```cpp
void Fins::setup_fins() {
    //fin   #   r   f   d     y,    r   f     d     y
    //          amplitude factors    offset factors
    add_fin(0,  0,  1, 0.5,   0,    0,  0,  0.5,    0); // Back
    add_fin(1,  0, -1, 0.5,   0,    0,  0,  0.5,    0); // Front
    add_fin(2, -1,  0,   0, 0.5,    0,  0,    0,  0.5); // Right
    add_fin(3,  1,  0,   0, 0.5,    0,  0,    0, -0.5); // Left
}
```

### Fin Factors

Each fin has 8 factors controlling how it responds to commands:

**Amplitude Factors** (how much the fin flaps):
- `_right_amp_factor`: Response to right/left command
- `_front_amp_factor`: Response to front/back command
- `_down_amp_factor`: Response to up/down command
- `_yaw_amp_factor`: Response to yaw command

**Offset Factors** (average fin position):
- `_right_off_factor`: Offset from right/left command
- `_front_off_factor`: Offset from front/back command
- `_down_off_factor`: Offset from up/down command
- `_yaw_off_factor`: Offset from yaw command

## Output Mixing

### Input Commands

```cpp
float right_out;  // Lateral movement (-1 to +1)
float front_out;  // Forward/backward (-1 to +1)
float down_out;   // Vertical (-1 to +1)
float yaw_out;    // Rotation (-1 to +1)
```

### Mixing Algorithm

```cpp
void Fins::output() {
    if (!_armed) {
        right_out = front_out = down_out = yaw_out = 0;
    }

    // Constrain inputs
    right_out = constrain_float(right_out, -1, 1);
    front_out = constrain_float(front_out, -1, 1);
    down_out = constrain_float(down_out, -1, 1);
    yaw_out = constrain_float(yaw_out, -1, 1);

    _time = AP_HAL::micros() * 1.0e-6;

    for (int8_t i = 0; i < NUM_FINS; i++) {
        // Calculate amplitude (always positive)
        _amp[i] = fmaxf(0, _right_amp_factor[i] * right_out)
                + fmaxf(0, _front_amp_factor[i] * front_out)
                + fabsf(_down_amp_factor[i] * down_out)
                + fabsf(_yaw_amp_factor[i] * yaw_out);

        // Calculate offset (signed)
        _off[i] = _right_off_factor[i] * right_out
                + _front_off_factor[i] * front_out
                + _down_off_factor[i] * down_out
                + _yaw_off_factor[i] * yaw_out;

        // Average offsets when multiple inputs active
        _num_added = count_active_inputs(i);
        if (_num_added > 0) {
            _off[i] = _off[i] / _num_added;
        }

        // Ensure amplitude + offset doesn't exceed 1
        if ((_amp[i] + fabsf(_off[i])) > 1) {
            _amp[i] = 1 - fabsf(_off[i]);
        }

        // Frequency multiplier
        _freq[i] = 1;

        // Turbo mode: double frequency for high offset, low amplitude
        if (turbo_mode && _amp[i] <= 0.6 && fabsf(_off[i]) >= 0.4) {
            _freq[i] = 2;
        }

        // Generate sine wave position
        _pos[i] = _amp[i] * cosf(freq_hz * _freq[i] * _time * 2 * M_PI) + _off[i];

        // Output to servo
        SRV_Channels::set_output_scaled(
            SRV_Channels::get_motor_function(i),
            _pos[i] * FIN_SCALE_MAX
        );
    }
}
```

## Sine Wave Generation

The core output formula:

```cpp
_pos[i] = _amp[i] * cos(freq_hz * _freq[i] * _time * 2π) + _off[i]
```

Where:
- `_pos[i]`: Servo position (-1 to +1)
- `_amp[i]`: Oscillation amplitude (0 to 1)
- `freq_hz`: Base frequency (default 3 Hz)
- `_freq[i]`: Frequency multiplier (1 or 2)
- `_time`: Current time in seconds
- `_off[i]`: DC offset (-1 to +1)

### Amplitude vs Offset

| Amplitude | Offset | Effect |
|-----------|--------|--------|
| High | 0 | Symmetric flapping, no net thrust |
| 0 | High | Steady deflection, constant thrust |
| High | High | Asymmetric flapping, net thrust |

## Turbo Mode

When enabled (`FINS_TURBO_MODE = 1`), fins oscillate at double frequency when:
- Amplitude ≤ 0.6
- |Offset| ≥ 0.4

This provides faster response for positional corrections.

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `FINS_FREQ_HZ` | Base oscillation frequency | 3 Hz |
| `FINS_TURBO_MODE` | Enable frequency doubling | 0 |

## Servo Mapping

Fins map to motor servo channels:

```cpp
SRV_Channels::set_angle(SRV_Channel::k_motor1, FIN_SCALE_MAX); // Fin 0
SRV_Channels::set_angle(SRV_Channel::k_motor2, FIN_SCALE_MAX); // Fin 1
SRV_Channels::set_angle(SRV_Channel::k_motor3, FIN_SCALE_MAX); // Fin 2
SRV_Channels::set_angle(SRV_Channel::k_motor4, FIN_SCALE_MAX); // Fin 3
```

## Armed State

```cpp
void Fins::armed(bool arm) {
    _armed = arm;
    AP_Notify::flags.armed = arm;
}

bool Fins::armed() const {
    return _armed;
}
```

When disarmed, all outputs are zeroed:

```cpp
if (!_armed) {
    right_out = front_out = down_out = yaw_out = 0;
}
```

## Throttle Indicator

For MAVLink display purposes:

```cpp
float Fins::get_throttle() {
    // Returns max of all outputs as throttle indicator
    return fmaxf(
        fmaxf(fabsf(down_out), fabsf(front_out)),
        fmaxf(fabsf(right_out), fabsf(yaw_out))
    );
}
```

## Adding Custom Fin Configuration

```cpp
void add_fin(
    int8_t fin_num,
    float right_amp_fac,
    float front_amp_fac,
    float down_amp_fac,
    float yaw_amp_fac,
    float right_off_fac,
    float front_off_fac,
    float down_off_fac,
    float yaw_off_fac
);
```

Example for different fin arrangement:

```cpp
// Custom arrangement
add_fin(0, 0.5, 0.5, 0, 0, 0, 0, 0, 0);  // Front-right
add_fin(1, -0.5, 0.5, 0, 0, 0, 0, 0, 0); // Front-left
// ... etc
```
