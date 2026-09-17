# Attitude & Position Control

Core control libraries for multicopter attitude and position control.

## AC_AttitudeControl

**Location**: `libraries/AC_AttitudeControl/AC_AttitudeControl.h`

**Singleton**: `AC_AttitudeControl::get_singleton()`

### Variants
- `AC_AttitudeControl_Multi` - Multicopter
- `AC_AttitudeControl_Heli` - Helicopter
- `AC_AttitudeControl_Multi_6DoF` - 6DoF vehicles

### Core Methods

```cpp
// Timestep
void set_dt_s(float dt_s);
float get_dt_s() const;

// Angle inputs (centidegrees)
void input_euler_angle_roll_pitch_yaw(float roll_cd, float pitch_cd, float yaw_cd, bool slew_yaw);
void input_euler_angle_roll_pitch_euler_rate_yaw(float roll_cd, float pitch_cd, float yaw_rate_cds);

// Rate inputs (centidegrees/sec)
void input_rate_bf_roll_pitch_yaw(float roll_rate_cds, float pitch_rate_cds, float yaw_rate_cds);

// Thrust vector inputs
void input_thrust_vector_rate_heading(const Vector3f& thrust_vec, float heading_rate_cds);
void input_thrust_vector_heading(const Vector3f& thrust_vec, float heading_cd, float heading_rate_cds);

// Controller execution
void attitude_controller_run_quat();     // Run angle → rate
virtual void rate_controller_run();      // Run rate → motor output

// Throttle
void set_throttle_out(float throttle_in, bool apply_angle_boost, float filt_cutoff);
float get_throttle_boosted(float throttle_in);

// Resets
void reset_yaw_target_and_rate(bool reset_rate = true);
void reset_rate_controller_I_terms();
void reset_rate_controller_I_terms_smoothly();

// State queries
Quaternion get_attitude_target_quat() const;
Vector3f get_attitude_target_euler_cd() const;
float lean_angle_max_cd() const;
```

### Parameters (ATC_)

| Parameter | Description |
|-----------|-------------|
| `ATC_ANG_RLL_P` | Roll angle P gain |
| `ATC_ANG_PIT_P` | Pitch angle P gain |
| `ATC_ANG_YAW_P` | Yaw angle P gain |
| `ATC_RAT_RLL_P/I/D` | Roll rate PID |
| `ATC_RAT_PIT_P/I/D` | Pitch rate PID |
| `ATC_RAT_YAW_P/I/D` | Yaw rate PID |
| `ATC_ACCEL_R_MAX` | Max roll accel (cdeg/s²) |
| `ATC_ACCEL_P_MAX` | Max pitch accel |
| `ATC_ACCEL_Y_MAX` | Max yaw accel |
| `ATC_RATE_R_MAX` | Max roll rate (deg/s) |
| `ATC_RATE_P_MAX` | Max pitch rate |
| `ATC_RATE_Y_MAX` | Max yaw rate |
| `ATC_INPUT_TC` | Input time constant |

---

## AC_PosControl

**Location**: `libraries/AC_AttitudeControl/AC_PosControl.h`

**Singleton**: `AC_PosControl::get_singleton()`

### Core Methods

```cpp
// Timestep & estimates
void set_dt_s(float dt_s);
void update_estimates();

// Position inputs (NED frame, meters)
void input_pos_NED_m(const Vector3f& pos_m, float pos_offset_z_cm, float pos_offset_z_buffer_cm);
void input_pos_NE_m(const Vector2f& pos_m);
void input_pos_D_m(float pos_m, float vel_max_m, float accel_max_m);

// Velocity inputs (m/s)
void input_vel_NE_m(const Vector2f& vel_m);
void input_vel_D_m(float vel_m);

// Controller updates
void NE_update_controller();              // Horizontal
void D_update_controller();               // Vertical

// Initialization
void NE_init_controller();
void D_init_controller();
void relax_velocity_controller_xy();
void relax_velocity_controller_z();

// Speed/accel limits
void NE_set_max_speed_accel_m(float speed_m, float accel_m);
void D_set_max_speed_accel_m(float speed_up_m, float speed_down_m, float accel_m);

// Outputs (for attitude controller)
float get_roll_cd() const;
float get_pitch_cd() const;
float get_roll_rad() const;
float get_pitch_rad() const;

// State queries
Vector3f get_pos_target_m() const;
Vector3f get_vel_target_m() const;
Vector3f get_pos_error_m() const;

// Stopping
void set_pos_target_to_stopping_point();
void get_stopping_point_xy_m(Vector2f& stopping_point) const;
void get_stopping_point_z_m(float& stopping_point) const;
```

### Parameters (PSC_)

| Parameter | Description |
|-----------|-------------|
| `PSC_POSXY_P` | Horizontal position P |
| `PSC_POSZ_P` | Vertical position P |
| `PSC_VELXY_P/I/D` | Horizontal velocity PID |
| `PSC_VELZ_P/I/D` | Vertical velocity PID |
| `PSC_ACCXY_FILT` | XY accel filter (Hz) |
| `PSC_ACCZ_FILT` | Z accel filter (Hz) |

---

## Usage Patterns

### Basic Attitude Control (Stabilize)

```cpp
void mode_stabilize_run() {
    AC_AttitudeControl *att = AC_AttitudeControl::get_singleton();
    att->set_dt_s(dt);

    // Get pilot input
    float roll_cd = channel_roll->get_control_in() * angle_max;
    float pitch_cd = channel_pitch->get_control_in() * angle_max;
    float yaw_rate_cds = channel_yaw->get_control_in() * yaw_rate_max;

    // Set target and run
    att->input_euler_angle_roll_pitch_euler_rate_yaw(roll_cd, pitch_cd, yaw_rate_cds);
    att->attitude_controller_run_quat();
    att->set_throttle_out(throttle, true, POSCONTROL_THROTTLE_CUTOFF_FREQ);
    att->rate_controller_run();
}
```

### Position Hold

```cpp
void mode_poshold_run() {
    AC_PosControl *pos = AC_PosControl::get_singleton();
    AC_AttitudeControl *att = AC_AttitudeControl::get_singleton();

    // Initialize once
    if (!initialized) {
        pos->NE_init_controller();
        pos->D_init_controller();
        initialized = true;
    }

    // Hold current position
    pos->input_pos_NED_m(target_pos, 0, 0);

    // Update controllers
    pos->update_estimates();
    pos->NE_update_controller();
    pos->D_update_controller();

    // Feed to attitude
    att->input_euler_angle_roll_pitch_yaw(
        pos->get_roll_cd(), pos->get_pitch_cd(), yaw_cd, true);
    att->attitude_controller_run_quat();
    att->rate_controller_run();
}
```

### Velocity Control

```cpp
void velocity_mode_run() {
    AC_PosControl *pos = AC_PosControl::get_singleton();

    // Set desired velocity (NED, m/s)
    Vector2f vel_NE(1.0f, 0.5f);  // 1 m/s North, 0.5 m/s East
    float vel_D = -0.3f;          // 0.3 m/s up (negative = up in NED)

    pos->input_vel_NE_m(vel_NE);
    pos->input_vel_D_m(vel_D);

    pos->NE_update_controller();
    pos->D_update_controller();
}
```

## Thread Safety

Rate controller runs at 400Hz, potentially on separate thread. Key pattern:
- Calculations complete first
- `_ang_vel_body_rads` written atomically at end
- No explicit locks needed for rate targets

```cpp
// Safe: single atomic write at end
void input_euler_angle_roll_pitch_yaw(...) {
    Vector3f ang_vel = calculate_rate_target();  // All calcs first
    _ang_vel_body_rads = ang_vel;                // Atomic write
}
```
