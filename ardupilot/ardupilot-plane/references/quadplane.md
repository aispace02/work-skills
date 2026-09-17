# QuadPlane (VTOL Support)

## Overview

**Location**: `ArduPlane/quadplane.h`, `ArduPlane/quadplane.cpp`

QuadPlane adds VTOL (Vertical Take-Off and Landing) capability to fixed-wing aircraft using multicopter motors.

## QuadPlane Configurations

### Frame Types (Q_FRAME_TYPE)

| Value | Type | Description |
|-------|------|-------------|
| 0 | Plus | + configuration |
| 1 | X | X configuration |
| 2 | V | V-tail |
| 3 | H | H-frame |
| 4 | V-Tail | V-tail quad |
| 5 | A-Tail | A-tail quad |
| 6 | Tailsitter | Tailsitter |
| 7 | Tilthex | Tilting hexacopter |
| 10 | Y6 | Y6 configuration |
| 11 | Tri | Tricopter |
| 12 | Bicopter | Bicopter tailsitter |

### Motor Classes (Q_FRAME_CLASS)

| Value | Class | Description |
|-------|-------|-------------|
| 1 | Quad | 4 motors |
| 2 | Hexa | 6 motors |
| 3 | Octa | 8 motors |
| 4 | OctaQuad | 8 motors (coax) |
| 5 | Y6 | 6 motors (Y6) |
| 7 | Tri | 3 motors |
| 10 | Tailsitter | Tailsitter |
| 12 | Dodeca-Hexa | 12 motors |

## QuadPlane Class

```cpp
class QuadPlane {
public:
    // Check if QuadPlane enabled
    bool available() const { return enable != 0; }

    // Initialize
    void init();

    // Control
    void control_run();           // Run VTOL control
    void motors_output();         // Output to motors

    // Transition
    void transition_start();
    bool in_transition() const;
    bool in_vtol_mode() const;

    // Position control
    void set_desired_location(const Location &loc);
    void control_loiter();
    void control_land();

    // State
    bool is_flying();
    bool throttle_wait();
};
```

## VTOL Modes

### QSTABILIZE

Manual throttle, attitude stabilized.

```cpp
void ModeQStabilize::update() {
    // Get pilot roll/pitch/yaw input
    float roll_input = plane.channel_roll->norm_input();
    float pitch_input = plane.channel_pitch->norm_input();
    float yaw_input = plane.channel_rudder->norm_input();

    // Apply to attitude controller
    plane.quadplane.attitude_control->input_euler_angle_roll_pitch_euler_rate_yaw(
        roll_input * plane.quadplane.aparm.angle_max,
        pitch_input * plane.quadplane.aparm.angle_max,
        yaw_input * plane.quadplane.yaw_rate_max
    );

    // Pilot controls throttle directly
    plane.quadplane.motors->set_throttle(
        plane.quadplane.get_pilot_throttle()
    );
}
```

### QHOVER

Altitude hold, attitude stabilized.

```cpp
void ModeQHover::update() {
    // Pilot controls climb rate with throttle stick
    float target_climb_rate = plane.quadplane.get_pilot_desired_climb_rate_cms();

    // Run altitude controller
    plane.quadplane.pos_control->set_target_climbrate(target_climb_rate);
    plane.quadplane.pos_control->update_z_controller();
}
```

### QLOITER

Position hold.

```cpp
void ModeQLoiter::update() {
    // Get pilot position inputs
    Vector2f target_vel = plane.quadplane.get_pilot_desired_velocity();

    // Run position controller
    plane.quadplane.loiter_nav->set_pilot_desired_acceleration(target_vel);
    plane.quadplane.loiter_nav->update();

    // Run altitude controller
    plane.quadplane.pos_control->update_z_controller();
}
```

### QLAND

Vertical landing.

```cpp
void ModeQLand::update() {
    // Land at current position
    plane.quadplane.control_land();
}
```

### QRTL

Return to launch, then vertical land.

```cpp
void ModeQRTL::update() {
    switch (submode) {
        case SubMode::RTL:
            // Fly back as plane or VTOL
            plane.quadplane.control_loiter();
            break;
        case SubMode::climb:
            // Climb to safe altitude before transitioning
            break;
    }

    // Check if should transition to QLAND
    if (close_to_home()) {
        plane.set_mode(plane.mode_qland, ModeReason::QRTL_COMPLETE);
    }
}
```

## Transitions

### Forward Transition (VTOL → Fixed-Wing)

```cpp
// Triggered when:
// - Airspeed > Q_ASSIST_SPEED
// - Or mode changes to fixed-wing mode

void QuadPlane::transition_start() {
    transition_state = TRANSITION_AIRSPEED_WAIT;
    transition_start_ms = AP_HAL::millis();
}

// Transition completes when:
// - Airspeed > ARSPD_FBW_MIN
// - And time > Q_TRANSITION_MS
```

### Back Transition (Fixed-Wing → VTOL)

```cpp
// Triggered when:
// - Mode changes to Q mode
// - Or RTL reaches home

void QuadPlane::transition_to_vtol() {
    // Slow down
    TECS_controller.set_target_airspeed(0);

    // Activate VTOL motors
    motors_output(true);
}
```

## Q_ASSIST

VTOL motors assist fixed-wing flight when needed.

### Q_ASSIST Triggers

| Trigger | Description |
|---------|-------------|
| Airspeed low | Below `Q_ASSIST_SPEED` |
| Angle high | Roll/pitch exceed `Q_ASSIST_ANGLE` |
| Altitude low | Below `Q_ASSIST_ALT` |

```cpp
bool QuadPlane::assistance_needed() {
    if (airspeed < Q_ASSIST_SPEED) return true;
    if (abs(roll) > Q_ASSIST_ANGLE) return true;
    if (abs(pitch) > Q_ASSIST_ANGLE) return true;
    if (alt_agl < Q_ASSIST_ALT) return true;
    return false;
}
```

## Parameters (Q_)

### General

| Parameter | Description | Default |
|-----------|-------------|---------|
| `Q_ENABLE` | Enable QuadPlane | 0 |
| `Q_FRAME_CLASS` | Motor class | 1 |
| `Q_FRAME_TYPE` | Frame type | 0 |
| `Q_THR_MIN_PWM` | Min motor PWM | 1000 |
| `Q_THR_MAX_PWM` | Max motor PWM | 2000 |

### Transition

| Parameter | Description | Default |
|-----------|-------------|---------|
| `Q_TRANSITION_MS` | Transition time (ms) | 5000 |
| `Q_ASSIST_SPEED` | Speed for VTOL assist (m/s) | 0 |
| `Q_ASSIST_ANGLE` | Angle for VTOL assist (deg) | 30 |
| `Q_ASSIST_ALT` | Altitude for VTOL assist (m) | 0 |

### Attitude

| Parameter | Description |
|-----------|-------------|
| `Q_A_*` | Attitude control (like AC_AttitudeControl) |
| `Q_P_*` | Position control (like AC_PosControl) |
| `Q_WP_*` | Waypoint navigation |

### Tiltrotor

| Parameter | Description |
|-----------|-------------|
| `Q_TILT_ENABLE` | Enable tiltrotor |
| `Q_TILT_TYPE` | Tilt type |
| `Q_TILT_RATE` | Tilt rate |

### Tailsitter

| Parameter | Description |
|-----------|-------------|
| `Q_TAILSIT_ENABLE` | Enable tailsitter |
| `Q_TAILSIT_ANGLE` | Transition angle |
| `Q_TAILSIT_INPUT` | Input type |

## Special Configurations

### Tiltrotor

Motors tilt between vertical and horizontal.

```cpp
// Tiltrotor types
Q_TILT_TYPE = 0  // Continuous tilt
Q_TILT_TYPE = 1  // Binary tilt
Q_TILT_TYPE = 2  // Vectored thrust
```

### Tailsitter

Aircraft rotates 90° between hover and forward flight.

```cpp
// Tailsitter transitions by rotating the whole aircraft
// rather than using separate hover motors
```

### Bicopter

Two motors with thrust vectoring for yaw/pitch.

## Motor Mapping

```cpp
// QuadPlane uses SERVO5-8 for quad motors by default
// Additional motors on SERVO9-12 for hexa/octa

// Set motor functions:
SERVO5_FUNCTION = 33  // Motor 1
SERVO6_FUNCTION = 34  // Motor 2
SERVO7_FUNCTION = 35  // Motor 3
SERVO8_FUNCTION = 36  // Motor 4
```

## Logging

QuadPlane logs to `QTUN` message for VTOL flight data.
