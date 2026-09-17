# Joystick/Gamepad Control

## Overview

ArduSub is primarily controlled via joystick/gamepad using MAVLink MANUAL_CONTROL messages, rather than traditional RC radio.

**File**: `ArduSub/joystick.cpp`

## Input Mapping

### MANUAL_CONTROL Message

```cpp
void Sub::transform_manual_control_to_rc_override(
    int16_t x,        // Forward/backward (-1000 to 1000)
    int16_t y,        // Left/right (-1000 to 1000)
    int16_t z,        // Up/down (0 to 1000)
    int16_t r,        // Yaw (-1000 to 1000)
    uint16_t buttons, // Button bitmask (16 buttons)
    uint16_t buttons2,// Extended buttons (16 more)
    uint8_t extensions,
    int16_t s,        // Pitch trim
    int16_t t,        // Roll trim
    int16_t aux1-aux6 // Auxiliary axes
)
```

### Axis Mapping

| Axis | Function | Range | Notes |
|------|----------|-------|-------|
| x | Forward/Lateral | -1000 to +1000 | See roll_pitch_flag |
| y | Lateral/Roll | -1000 to +1000 | See roll_pitch_flag |
| z | Throttle (vertical) | 0 to 1000 | 500 = neutral |
| r | Yaw | -1000 to +1000 | Rotation rate |
| s | Pitch trim | -1000 to +1000 | Fine adjustment |
| t | Roll trim | -1000 to +1000 | Fine adjustment |

### Control Modes

**Movement Mode** (roll_pitch_flag = 0):
- X axis: Forward/backward
- Y axis: Left/right (strafe)

**Attitude Mode** (roll_pitch_flag = 1):
- X axis: Pitch trim
- Y axis: Roll trim

```cpp
if (roll_pitch_flag == 1) {
    pitchTrim = -x * rpyScale;
    rollTrim = y * rpyScale;
}
```

## Gain System

### Gain Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `JS_GAIN_DEFAULT` | Default gain | 0.5 |
| `JS_GAIN_MIN` | Minimum gain | 0.25 |
| `JS_GAIN_MAX` | Maximum gain | 1.0 |
| `JS_GAIN_STEPS` | Number of gain steps | 4 |

### Gain Calculation

```cpp
float rpyScale = 0.4 * gain;  // Roll/pitch/yaw scaling
float throttleScale = 0.8 * gain * g.throttle_gain;  // Throttle scaling

// Apply to channels
channel_throttle->set_override(constrain_int16(
    (zTot) * throttleScale + throttleBase, 1100, 1900), tnow);
channel_yaw->set_override(constrain_int16(
    r * rpyScale + rpyCenter, 1100, 1900), tnow);
```

## Button Functions

### JSButton Class

Defined in `libraries/AP_JSButton/AP_JSButton.h`:

```cpp
class JSButton {
public:
    enum button_function_t {
        k_none = 0,
        k_shift = 1,
        k_arm_toggle = 2,
        k_arm = 3,
        k_disarm = 4,
        k_mode_manual = 5,
        k_mode_stabilize = 6,
        k_mode_depth_hold = 7,
        k_mode_poshold = 8,
        k_mode_auto = 9,
        k_mode_circle = 10,
        k_mode_guided = 11,
        k_mode_acro = 12,
        // ... camera, lights, servos, relays ...
    };
};
```

### Common Button Functions

| Function | ID | Description |
|----------|-----|-------------|
| `k_none` | 0 | No action |
| `k_shift` | 1 | Shift modifier |
| `k_arm_toggle` | 2 | Toggle arm/disarm |
| `k_arm` | 3 | Arm motors |
| `k_disarm` | 4 | Disarm motors |
| `k_mode_manual` | 5 | Switch to Manual |
| `k_mode_stabilize` | 6 | Switch to Stabilize |
| `k_mode_depth_hold` | 7 | Switch to ALT_HOLD |
| `k_mode_poshold` | 8 | Switch to POSHOLD |
| `k_mode_auto` | 9 | Switch to Auto |
| `k_mount_center` | 15 | Center camera gimbal |
| `k_mount_tilt_up` | 16 | Tilt camera up |
| `k_mount_tilt_down` | 17 | Tilt camera down |
| `k_lights1_cycle` | 20 | Cycle lights 1 |
| `k_lights1_brighter` | 21 | Increase lights 1 |
| `k_lights1_dimmer` | 22 | Decrease lights 1 |
| `k_gain_toggle` | 23 | Toggle high/low gain |
| `k_gain_inc` | 24 | Increase gain |
| `k_gain_dec` | 25 | Decrease gain |
| `k_input_hold_set` | 34 | Set input hold |
| `k_roll_pitch_toggle` | 35 | Toggle movement/attitude mode |

### Button Parameters

32 buttons supported (BTN0-BTN31):

```cpp
// Parameters: BTN0_FUNCTION through BTN31_FUNCTION
// Each button can have primary and shift functions
JSButton jbtn_0;  // g.jbtn_0
JSButton jbtn_1;  // g.jbtn_1
// ...
JSButton jbtn_31; // g.jbtn_31
```

## Input Hold

Maintain current forward/lateral/throttle without continuous input:

```cpp
case JSButton::button_function_t::k_input_hold_set:
    if (!motors.armed()) break;
    if (!held) {
        zTrim = abs(z_last - 500) > 50 ? z_last - 500 : 0;
        xTrim = abs(x_last) > 50 ? x_last : 0;
        yTrim = abs(y_last) > 50 ? y_last : 0;
        input_hold_engaged = zTrim || xTrim || yTrim;
        if (input_hold_engaged) {
            gcs().send_text(MAV_SEVERITY_INFO, "#Input Hold Set");
        }
    }
    break;
```

## Button Press Handling

```cpp
void Sub::handle_jsbutton_press(uint8_t _button, bool shift, bool held) {
    switch (get_button(_button)->function(shift)) {
        case JSButton::button_function_t::k_arm_toggle:
            if (motors.armed()) {
                arming.disarm(AP_Arming::Method::MAVLINK);
            } else {
                arming.arm(AP_Arming::Method::MAVLINK);
            }
            break;

        case JSButton::button_function_t::k_mode_depth_hold:
            set_mode(Mode::Number::ALT_HOLD, ModeReason::RC_COMMAND);
            break;

        case JSButton::button_function_t::k_gain_inc:
            gain = constrain_float(gain + gain_step, g.minGain, g.maxGain);
            gcs().send_text(MAV_SEVERITY_INFO, "#Gain is %2.0f%%", gain * 100);
            break;
        // ...
    }
}
```

## Camera Control

### Gimbal Tilt/Pan

```cpp
case JSButton::button_function_t::k_mount_tilt_up:
    cam_tilt = 1900;  // Max speed up
    break;

case JSButton::button_function_t::k_mount_tilt_down:
    cam_tilt = 1100;  // Max speed down
    break;

case JSButton::button_function_t::k_mount_center:
    camera_mount.set_angle_target(0, 0, 0, false);
    camera_mount.set_mode(MAV_MOUNT_MODE_RC_TARGETING);
    break;
```

### Lights Control

```cpp
case JSButton::button_function_t::k_lights1_brighter:
    if (!held) {
        uint16_t step = 1000.0 / g.lights_steps;
        lights1 = constrain_float(lights1 + step, 0.0, 1000.0);
        SRV_Channels::set_output_scaled(SRV_Channel::k_lights1, lights1);
    }
    break;
```

## Relay and Servo Control

### Relay Functions

```cpp
case JSButton::button_function_t::k_relay_1_toggle:
    if (!held) {
        relay.toggle(0);
    }
    break;

case JSButton::button_function_t::k_relay_1_momentary:
    if (!held) {
        relay.on(0);  // On when pressed
    }
    break;
// On release:
case JSButton::button_function_t::k_relay_1_momentary:
    relay.off(0);  // Off when released
    break;
```

### Servo Functions

```cpp
case JSButton::button_function_t::k_servo_1_inc:
    sub.g2.actuators.increase_actuator(0);
    break;

case JSButton::button_function_t::k_servo_1_center:
    sub.g2.actuators.center_actuator(0);
    break;
```

## Default Button Mapping

```cpp
JSButton::button_function_t defaults[16][2] = {
    {k_none,            k_none},           // 0
    {k_mode_manual,     k_none},           // 1
    {k_mode_depth_hold, k_none},           // 2
    {k_mode_stabilize,  k_none},           // 3
    {k_disarm,          k_none},           // 4
    {k_shift,           k_none},           // 5
    {k_arm,             k_none},           // 6
    {k_mount_center,    k_none},           // 7
    {k_input_hold_set,  k_none},           // 8
    {k_mount_tilt_down, k_mount_pan_left}, // 9
    {k_mount_tilt_up,   k_mount_pan_right},// 10
    {k_gain_inc,        k_trim_pitch_dec}, // 11
    {k_gain_dec,        k_trim_pitch_inc}, // 12
    {k_lights1_dimmer,  k_trim_roll_dec},  // 13
    {k_lights1_brighter,k_trim_roll_inc},  // 14
    {k_none,            k_none},           // 15
};
```

## Scripting Buttons

For Lua scripting:

```cpp
case JSButton::button_function_t::k_script_1:
    sub.script_buttons[0].press();
    break;

// Check from Lua:
bool Sub::is_button_pressed(uint8_t index) {
    return script_buttons[index - 1].is_pressed();
}

uint8_t Sub::get_and_clear_button_count(uint8_t index) {
    return script_buttons[index - 1].get_and_clear_count();
}
```
