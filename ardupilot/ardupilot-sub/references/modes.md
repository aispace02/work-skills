# ArduSub Flight Modes

## Mode Overview

| Mode | Number | GPS | Depth | Autopilot | Description |
|------|--------|-----|-------|-----------|-------------|
| MANUAL | 19 | No | No | No | Direct thruster control |
| STABILIZE | 0 | No | No | No | Attitude stabilized |
| ACRO | 1 | No | No | No | Rate-based control |
| ALT_HOLD | 2 | No | Yes | No | Depth hold |
| POSHOLD | 16 | Yes | Yes | Yes | 3D position hold |
| AUTO | 3 | Yes | Yes | Yes | Waypoint missions |
| GUIDED | 4 | Yes | Yes | Yes | GCS-commanded |
| CIRCLE | 7 | Yes | Yes | Yes | Circle around point |
| SURFACE | 9 | No | No* | Yes | Ascend to surface |
| MOTOR_DETECT | 20 | No | No | Yes | Motor detection |
| SURFTRAK | 21 | No | Yes | No | Terrain following |

*SURFACE can work without depth sensor using fixed thrust

## Manual Modes

### MANUAL (19)

Direct pass-through control with no stabilization.

```cpp
void ModeManual::run() {
    if (!motors.armed()) {
        motors.set_desired_spool_state(AP_Motors::DesiredSpoolState::GROUND_IDLE);
        return;
    }
    motors.set_desired_spool_state(AP_Motors::DesiredSpoolState::THROTTLE_UNLIMITED);
}
```

- Roll/pitch/yaw: Direct to thrusters
- Throttle: Direct to vertical thrusters
- Forward/lateral: Direct to horizontal thrusters

### STABILIZE (0)

Attitude-stabilized with manual throttle.

```cpp
void ModeStabilize::run() {
    // Get pilot lean angles
    sub.get_pilot_desired_lean_angles(roll_in, pitch_in, target_roll, target_pitch, angle_max);

    // Get pilot yaw rate
    float target_yaw_rate = sub.get_pilot_desired_yaw_rate(yaw_in);

    // Attitude control
    attitude_control->input_euler_angle_roll_pitch_euler_rate_yaw_cd(
        target_roll, target_pitch, target_yaw_rate);

    // Manual throttle
    attitude_control->set_throttle_out((throttle + 1.0f) / 2.0f, false, g.throttle_filt);

    // Forward/lateral pass-through
    motors.set_forward(channel_forward->norm_input());
    motors.set_lateral(channel_lateral->norm_input());
}
```

### ACRO (1)

Rate-based attitude control.

```cpp
void ModeAcro::run() {
    // Get pilot rate demands
    get_pilot_desired_angle_rates(roll_in, pitch_in, yaw_in,
        roll_rate, pitch_rate, yaw_rate);

    // Rate control
    attitude_control->input_rate_bf_roll_pitch_yaw_cd(
        roll_rate, pitch_rate, yaw_rate);
}
```

## Depth Hold Modes

### ALT_HOLD (2)

Depth hold with attitude stabilization.

```cpp
bool ModeAlthold::init(bool ignore_checks) {
    if (!sub.control_check_barometer()) {
        return false;  // Requires depth sensor
    }

    // Initialize position controller
    position_control->D_set_max_speed_accel_cm(speed_dn, speed_up, accel);
    position_control->D_init_controller();
    return true;
}

void ModeAlthold::run() {
    run_pre();      // Attitude control
    control_depth();  // Depth control
    run_post();     // Forward/lateral
}

void ModeAlthold::control_depth() {
    // Limit throttle near surface
    float distance_to_surface = (g.surface_depth - inertial_nav.get_position_z_up_cm()) * 0.01f;
    motors.set_max_throttle(g.surface_max_throttle + (1.0f - g.surface_max_throttle) * distance_to_surface);

    // Get pilot climb rate
    float target_climb_rate_cms = sub.get_pilot_desired_climb_rate(throttle_in);

    // Handle surface/bottom
    if (fabsf(target_climb_rate_cms) < 0.05f) {
        if (sub.ap.at_surface) {
            position_control->set_pos_desired_U_cm(MIN(pos, g.surface_depth));
        } else if (sub.ap.at_bottom) {
            position_control->set_pos_desired_U_cm(MAX(current_alt + 10, pos));
        }
    }

    // Update position controller
    position_control->D_set_pos_target_from_climb_rate_cms(target_climb_rate_cms);
    position_control->D_update_controller();
}
```

### SURFTRAK (21)

Maintains constant distance above seafloor using rangefinder.

```cpp
bool ModeSurftrak::init(bool ignore_checks) {
    if (!ModeAlthold::init(ignore_checks)) {
        return false;
    }
    reset();  // Clear rangefinder target
    return true;
}

void ModeSurftrak::control_range() {
    float target_climb_rate_cms = sub.get_pilot_desired_climb_rate(throttle_in);

    if (fabsf(target_climb_rate_cms) < 0.05f) {
        // Not piloting - track terrain
        update_surface_offset();
    } else if (!pilot_in_control) {
        // Pilot taking control
        pilot_control_start_z_cm = inertial_nav.get_position_z_up_cm();
        pilot_in_control = true;
    }

    position_control->D_set_pos_target_from_climb_rate_cms(target_climb_rate_cms);
    position_control->D_update_controller();
}
```

## Position Hold Modes

### POSHOLD (16)

3D position hold with pilot override.

```cpp
bool ModePoshold::init(bool ignore_checks) {
    if (!sub.position_ok()) {
        return false;  // Requires GPS
    }

    // Initialize XY and Z controllers
    position_control->NE_set_max_speed_accel_cm(pilot_speed, accel);
    position_control->NE_init_controller_stopping_point();
    position_control->D_init_controller();
    return true;
}

void ModePoshold::run() {
    // Attitude control
    attitude_control->input_euler_angle_roll_pitch_euler_rate_yaw_cd(...);

    // Depth control (inherited from ALT_HOLD)
    control_depth();

    // Horizontal position control
    control_horizontal();
}

void ModePoshold::control_horizontal() {
    // Get pilot velocity input
    Vector2f body_rates_cms = {
        sub.get_pilot_desired_horizontal_rate(channel_forward),
        sub.get_pilot_desired_horizontal_rate(channel_lateral)
    };

    // Convert to earth frame
    auto earth_rates_cms = ahrs.body_to_earth2D(body_rates_cms);
    position_control->input_vel_accel_NE_cm(earth_rates_cms, {0, 0});

    // Get motor outputs
    sub.translate_pos_control_rp(lateral_out, forward_out);
    position_control->NE_update_controller();

    motors.set_forward(forward_out);
    motors.set_lateral(lateral_out);
}
```

## Autonomous Modes

### AUTO (3)

Executes waypoint missions.

```cpp
void ModeAuto::run() {
    switch (sub.auto_mode) {
        case Auto_WP:
            auto_wp_run();
            break;
        case Auto_Circle:
            auto_circle_run();
            break;
        case Auto_Loiter:
            auto_loiter_run();
            break;
        case Auto_NavGuided:
            auto_nav_guided_run();
            break;
    }
}

void ModeAuto::auto_wp_run() {
    // Run waypoint navigation
    sub.wp_nav.update_wpnav();

    // Get roll/pitch from nav controller
    sub.translate_wpnav_rp(lateral_out, forward_out);

    // Attitude control
    attitude_control->input_euler_angle_roll_pitch_yaw_cd(0, 0, get_auto_heading(), true);

    motors.set_forward(forward_out);
    motors.set_lateral(lateral_out);
}
```

### GUIDED (4)

GCS-commanded position/velocity control.

```cpp
void ModeGuided::run() {
    switch (sub.guided_mode) {
        case Guided_WP:
            guided_pos_control_run();
            break;
        case Guided_Velocity:
            guided_vel_control_run();
            break;
        case Guided_PosVel:
            guided_posvel_control_run();
            break;
        case Guided_Angle:
            guided_angle_control_run();
            break;
    }
}

bool ModeGuided::guided_set_destination(const Vector3f& destination) {
    sub.wp_nav.set_wp_destination(destination, false);
    sub.guided_mode = Guided_WP;
    return true;
}

void ModeGuided::guided_set_velocity(const Vector3f& velocity) {
    position_control->input_vel_accel_NE_cm({velocity.x, velocity.y}, {0, 0});
    position_control->D_set_pos_target_from_climb_rate_cms(velocity.z);
    sub.guided_mode = Guided_Velocity;
}
```

### CIRCLE (7)

Circles around a point.

```cpp
bool ModeCircle::init(bool ignore_checks) {
    if (!sub.position_ok()) {
        return false;
    }

    sub.circle_nav.init_center();
    return true;
}

void ModeCircle::run() {
    // Update circle navigation
    sub.circle_nav.update();

    // Get motor outputs
    sub.translate_circle_nav_rp(lateral_out, forward_out);

    // Yaw control (face center or direction of travel)
    float target_yaw_rate = sub.get_pilot_desired_yaw_rate(yaw_in);
    if (sub.circle_pilot_yaw_override) {
        attitude_control->input_euler_angle_roll_pitch_euler_rate_yaw_cd(0, 0, target_yaw_rate);
    } else {
        attitude_control->input_euler_angle_roll_pitch_yaw_cd(0, 0, sub.circle_nav.get_yaw_cd(), true);
    }

    motors.set_forward(forward_out);
    motors.set_lateral(lateral_out);
}
```

## Special Modes

### SURFACE (9)

Ascend to surface.

```cpp
void ModeSurface::run() {
    if (!motors.armed()) {
        motors.output_min();
        return;
    }

    if (nobaro_mode) {
        // No depth sensor - use fixed thrust
        float thrust = 0.5f + g2.surface_nobaro_thrust * 0.005f;
        attitude_control->set_throttle_out(thrust, true, g.throttle_filt);
    } else {
        // Already surfaced?
        if (sub.ap.at_surface) {
            set_mode(Mode::Number::ALT_HOLD, ModeReason::SURFACE_COMPLETE);
            return;
        }

        // Attitude control
        attitude_control->input_euler_angle_roll_pitch_euler_rate_yaw_cd(...);

        // Climb at max rate
        float climb_rate = constrain_float(fabsf(wp_nav.get_default_speed_up_cms()), 1, max_speed);
        position_control->D_set_pos_target_from_climb_rate_cms(climb_rate);
        position_control->D_update_controller();
    }

    // Pilot can still control horizontal
    motors.set_forward(channel_forward->norm_input());
    motors.set_lateral(channel_lateral->norm_input());
}
```

### MOTOR_DETECT (20)

Automatic motor direction detection.

```cpp
void ModeMotordetect::run() {
    // Motors are controlled directly via MAVLink
    // See motors.cpp handle_do_motor_test()
}
```

## Mode Transitions

```cpp
bool Sub::set_mode(Mode::Number mode, ModeReason reason) {
    Mode *new_flightmode = mode_from_mode_num(mode);
    if (new_flightmode == nullptr) {
        return false;
    }

    // Try to initialize new mode
    if (!new_flightmode->init(false)) {
        return false;
    }

    // Exit current mode
    exit_mode(flightmode, new_flightmode);

    // Set new mode
    prev_control_mode = control_mode;
    control_mode = mode;
    flightmode = new_flightmode;

    return true;
}
```
