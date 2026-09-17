# PID Controllers

ArduPilot's PID controller implementations.

## AC_PID

**Location**: `libraries/AC_PID/AC_PID.h`

Standard PID controller with filtering and limits.

### Core Methods

```cpp
// Main update - returns controller output
float update_all(float target, float measurement, float dt, bool limit = false);
float update_error(float error, float dt, bool limit = false);

// Get individual terms
float get_p() const;
float get_i() const;
float get_d() const;
float get_ff() const;                         // Feedforward

// Reset
void reset_I();
void reset_filter();

// Configuration
void set_kP(float kp);
void set_kI(float ki);
void set_kD(float kd);
void set_kFF(float kff);
void set_imax(float imax);
void set_filt_T_hz(float hz);                 // Target filter
void set_filt_E_hz(float hz);                 // Error filter
void set_filt_D_hz(float hz);                 // D-term filter

// State
float get_kP() const;
float get_kI() const;
float get_kD() const;
float get_kFF() const;
float get_imax() const;
float get_error() const;
float get_integrator() const;
```

### Usage

```cpp
AC_PID pid(1.0f, 0.1f, 0.01f, 0.0f, 10.0f);  // kP, kI, kD, kFF, imax

void control_loop() {
    float target = get_desired_value();
    float measurement = get_sensor_value();

    float output = pid.update_all(target, measurement, dt);
    apply_output(output);
}
```

---

## AC_P

**Location**: `libraries/AC_PID/AC_P.h`

Simple proportional controller.

### Core Methods

```cpp
float get_p(float error) const;               // Returns kP * error
void set_kP(float kp);
float get_kP() const;
```

### Usage

```cpp
AC_P p_controller(2.0f);  // kP = 2.0

float output = p_controller.get_p(error);
```

---

## AC_PID_2D

**Location**: `libraries/AC_PID/AC_PID_2D.h`

2D PID for horizontal velocity/position control.

### Core Methods

```cpp
// Main update
Vector2f update_all(const Vector2f& target, const Vector2f& measurement,
                    float dt, const Vector2f& limit);

// Reset
void reset_I();
void reset_filter();

// Configuration
void set_kP(float kp);
void set_kI(float ki);
void set_kD(float kd);
void set_imax(float imax);
void set_filt_E_hz(float hz);
void set_filt_D_hz(float hz);

// State
Vector2f get_p() const;
Vector2f get_i() const;
Vector2f get_d() const;
Vector2f get_integrator() const;
```

### Usage

```cpp
AC_PID_2D vel_pid(1.0f, 0.5f, 0.0f, 100.0f);  // kP, kI, kD, imax

void velocity_control() {
    Vector2f target_vel(1.0f, 0.5f);
    Vector2f current_vel = get_velocity();
    Vector2f limit(100.0f, 100.0f);

    Vector2f output = vel_pid.update_all(target_vel, current_vel, dt, limit);
}
```

---

## AC_P_1D

**Location**: `libraries/AC_PID/AC_P_1D.h`

1D proportional controller with rate limiting.

### Core Methods

```cpp
float update(float error, float error_rate, float dt);
void set_kP(float kp);
void set_limits(float output_min, float output_max, float rate_max);
```

---

## AC_P_2D

**Location**: `libraries/AC_PID/AC_P_2D.h`

2D proportional controller with magnitude limiting.

### Core Methods

```cpp
Vector2f update(const Vector2f& error, float dt);
void set_kP(float kp);
void set_limits(float output_max, float rate_max);
```

---

## AC_PI_2D

**Location**: `libraries/AC_PID/AC_PI_2D.h`

2D PI controller (no derivative term).

### Core Methods

```cpp
Vector2f update(const Vector2f& error, float dt);
void set_kP(float kp);
void set_kI(float ki);
void set_imax(float imax);
void reset_I();
```

---

## Tuning Patterns

### Runtime Gain Adjustment

```cpp
void adjust_gains_for_gentle_mode() {
    AC_AttitudeControl *att = AC_AttitudeControl::get_singleton();
    AC_PID& roll_pid = att->get_rate_roll_pid();

    // Save original
    float orig_kp = roll_pid.get_kP();

    // Reduce for gentle mode
    roll_pid.set_kP(orig_kp * 0.5f);
    roll_pid.reset_I();  // Always reset I after gain changes
}
```

### I-Term Management

```cpp
// Reset integrators when changing modes
void on_mode_change() {
    AC_AttitudeControl *att = AC_AttitudeControl::get_singleton();
    att->reset_rate_controller_I_terms();
}

// Smooth reset (ramp down)
void on_landing() {
    att->reset_rate_controller_I_terms_smoothly();
}

// Relax velocity I-terms
void on_position_mode_exit() {
    AC_PosControl *pos = AC_PosControl::get_singleton();
    pos->relax_velocity_controller_xy();
    pos->relax_velocity_controller_z();
}
```

### Filter Configuration

```cpp
void configure_pid_filters() {
    AC_PID pid;

    // Target filter - smooths setpoint changes
    pid.set_filt_T_hz(20.0f);

    // Error filter - smooths error signal
    pid.set_filt_E_hz(10.0f);

    // D-term filter - critical for noise rejection
    pid.set_filt_D_hz(5.0f);
}
```

## Controller Hierarchy in ArduPilot

```
Position P (AC_P_2D)
    ↓ velocity target
Velocity PID (AC_PID_2D)
    ↓ acceleration target → roll/pitch
Angle P (AC_P)
    ↓ rate target
Rate PID (AC_PID)
    ↓ motor output
```

Each level cascades into the next. Outer loops run slower than inner loops.
