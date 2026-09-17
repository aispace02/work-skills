# ArduCopter Flight Modes

## Mode Overview

| Mode | # | GPS | Manual Throttle | Autopilot | Description |
|------|---|-----|-----------------|-----------|-------------|
| STABILIZE | 0 | No | Yes | No | Attitude stabilized |
| ACRO | 1 | No | Yes | No | Rate-based control |
| ALT_HOLD | 2 | No | No | No | Altitude hold |
| AUTO | 3 | Yes | No | Yes | Mission execution |
| GUIDED | 4 | Yes | No | Yes | GCS-commanded |
| LOITER | 5 | Yes | No | No | Position hold |
| RTL | 6 | Yes | No | Yes | Return to launch |
| CIRCLE | 7 | Yes | No | Yes | Circle around point |
| LAND | 9 | No* | No | Yes | Automatic landing |
| DRIFT | 11 | Yes | No | No | Semi-auto control |
| SPORT | 13 | No | No | No | Earth-frame rates |
| FLIP | 14 | No | No | No | Acrobatic flip |
| AUTOTUNE | 15 | No | No | No | PID auto-tuning |
| POSHOLD | 16 | Yes | No | No | Position + brake |
| BRAKE | 17 | Yes | No | Yes | Emergency stop |
| THROW | 18 | Yes | No | No | Throw to launch |
| GUIDED_NOGPS | 20 | No | No | Yes | Guided without GPS |
| SMART_RTL | 21 | Yes | No | Yes | Retrace path home |
| FLOWHOLD | 22 | No | No | No | Optical flow hold |
| FOLLOW | 23 | Yes | No | Yes | Follow target |
| ZIGZAG | 24 | Yes | No | Yes | Zigzag pattern |
| SYSTEMID | 25 | No | Yes | No | System ID |
| TURTLE | 28 | No | Yes | No | Flip after crash |

*LAND uses GPS if available

## Manual Modes

### STABILIZE (0)

Attitude stabilized with manual throttle.

```cpp
void ModeStabilize::run() {
    // Apply simple mode transform
    update_simple_mode();

    // Convert pilot input to lean angles
    float target_roll_rad, target_pitch_rad;
    get_pilot_desired_lean_angles_rad(target_roll_rad, target_pitch_rad, ...);

    // Get pilot yaw rate
    float target_yaw_rate_rads = get_pilot_desired_yaw_rate_rads();

    // Attitude control
    attitude_control->input_euler_angle_roll_pitch_euler_rate_yaw_rad(
        target_roll_rad, target_pitch_rad, target_yaw_rate_rads);

    // Manual throttle
    float pilot_throttle = get_pilot_desired_throttle();
    attitude_control->set_throttle_out(pilot_throttle, true, g.throttle_filt);
}
```

### ACRO (1)

Rate-based control with manual throttle.

```cpp
void ModeAcro::run() {
    // Get pilot desired rates
    float roll_out_rads, pitch_out_rads, yaw_out_rads;
    get_pilot_desired_rates_rads(roll_out_rads, pitch_out_rads, yaw_out_rads);

    // Rate control
    attitude_control->input_rate_bf_roll_pitch_yaw_rads(
        roll_out_rads, pitch_out_rads, yaw_out_rads);

    // Manual throttle
    attitude_control->set_throttle_out(get_pilot_desired_throttle(), ...);
}
```

Acro trainer modes:
- OFF: Full rate control
- LEVELING: Returns to level when sticks centered
- LIMITED: Limits max angle

## Altitude Hold Modes

### ALT_HOLD (2)

Altitude hold with attitude control.

```cpp
bool ModeAltHold::init(bool ignore_checks) {
    // Initialize vertical position controller
    pos_control->D_init_controller();
    pos_control->D_set_max_speed_accel_m(speed_dn, speed_up, accel_z);
    return true;
}

void ModeAltHold::run() {
    // Get AltHold state (landed, takeoff, flying)
    AltHoldModeState state = get_alt_hold_state_D_ms(target_climb_rate_ms);

    switch (state) {
        case AltHoldModeState::Flying:
            motors->set_desired_spool_state(THROTTLE_UNLIMITED);
            pos_control->D_set_pos_target_from_climb_rate_ms(climb_rate);
            break;
        // ... other states
    }

    // Attitude control
    attitude_control->input_euler_angle_roll_pitch_euler_rate_yaw_rad(...);

    // Vertical control
    pos_control->D_update_controller();
}
```

### SPORT (13)

Earth-frame rate control with altitude hold.

## Position Hold Modes

### LOITER (5)

3D position hold with pilot override.

```cpp
bool ModeLoiter::init(bool ignore_checks) {
    loiter_nav->init_target();
    pos_control->D_init_controller();
    return true;
}

void ModeLoiter::run() {
    // Process pilot roll/pitch input
    loiter_nav->set_pilot_desired_acceleration_rad(roll, pitch);

    // Get pilot climb rate
    target_climb_rate_ms = get_pilot_desired_climb_rate_ms();

    // Run loiter controller
    loiter_nav->update();

    // Attitude control with thrust vector
    attitude_control->input_thrust_vector_rate_heading_rads(
        loiter_nav->get_thrust_vector(), yaw_rate, false);

    // Vertical control
    pos_control->D_update_controller();
}
```

### POSHOLD (16)

Position hold with brake-to-loiter transition.

States:
- PILOT_OVERRIDE: Direct pilot control
- BRAKE: Braking to stop
- BRAKE_READY_TO_LOITER: Ready to transition
- BRAKE_TO_LOITER: Transitioning
- LOITER: Full position hold
- CONTROLLER_TO_PILOT_OVERRIDE: Returning to pilot

## Autonomous Modes

### AUTO (3)

Executes waypoint missions.

```cpp
void ModeAuto::run() {
    switch (_mode) {
        case SubMode::TAKEOFF:
            takeoff_run();
            break;
        case SubMode::WP:
            wp_run();
            break;
        case SubMode::LAND:
            land_run();
            break;
        case SubMode::RTL:
            rtl_run();
            break;
        case SubMode::CIRCLE:
            circle_run();
            break;
        case SubMode::LOITER:
            loiter_run();
            break;
    }
}

void ModeAuto::wp_run() {
    // Update waypoint navigation
    wp_nav->update_wpnav();

    // Auto yaw
    auto_yaw.get_heading();

    // Attitude control
    attitude_control->input_thrust_vector_heading_rads(
        wp_nav->get_thrust_vector(), auto_yaw.yaw_rad());

    // Vertical control
    pos_control->D_update_controller();
}
```

### GUIDED (4)

GCS or script commanded position/velocity/acceleration.

SubModes:
- TakeOff: Guided takeoff
- WP: Waypoint navigation
- Pos: Position control
- PosVelAccel: Full PVA control
- VelAccel: Velocity + acceleration
- Accel: Acceleration only
- Angle: Attitude control

```cpp
// Set position target
bool ModeGuided::set_destination(const Location& dest_loc, ...);

// Set velocity target
void ModeGuided::set_vel_NED_ms(const Vector3f& vel_ned_ms, ...);

// Set acceleration target
void ModeGuided::set_accel_NED_mss(const Vector3f& accel_ned_mss, ...);

// Set attitude target
void ModeGuided::set_angle(const Quaternion& attitude_quat, ...);
```

### RTL (6)

Return to launch.

States:
- STARTING: Initial state
- INITIAL_CLIMB: Climb to RTL altitude
- RETURN_HOME: Fly toward home
- LOITER_AT_HOME: Loiter at home
- FINAL_DESCENT: Descend to land
- LAND: Landing

```cpp
void ModeRTL::run(bool disarm_on_land) {
    switch (_state) {
        case SubMode::INITIAL_CLIMB:
        case SubMode::RETURN_HOME:
            climb_return_run();
            break;
        case SubMode::LOITER_AT_HOME:
            loiterathome_run();
            break;
        case SubMode::FINAL_DESCENT:
            descent_run();
            break;
        case SubMode::LAND:
            land_run(disarm_on_land);
            break;
    }
}
```

### SMART_RTL (21)

Returns home by retracing its flight path.

```cpp
void ModeSmartRTL::run() {
    switch (smart_rtl_state) {
        case SubMode::WAIT_FOR_PATH_CLEANUP:
            wait_cleanup_run();
            break;
        case SubMode::PATH_FOLLOW:
            path_follow_run();
            break;
        case SubMode::PRELAND_POSITION:
            pre_land_position_run();
            break;
        case SubMode::LAND:
            land();
            break;
    }
}
```

### LAND (9)

Automatic landing.

```cpp
void ModeLand::run() {
    if (control_position) {
        gps_run();  // Land with GPS position control
    } else {
        nogps_run();  // Land without position control
    }
}

void ModeLand::gps_run() {
    land_run_horizontal_control();
    land_run_vertical_control();
}
```

## Special Modes

### FLIP (14)

Acrobatic flip maneuver.

States:
- Start: Initialize
- Roll: Rolling phase
- Pitch_A/B: Pitching phases
- Recover: Recovery
- Abandon: Abort flip

### THROW (18)

Launch by throwing.

States:
- Disarmed: Waiting for arm
- Detecting: Waiting for throw
- Wait_Throttle_Unlimited: Spool motors
- Uprighting: Level vehicle
- HgtStabilise: Stabilize altitude
- PosHold: Final position hold

### TURTLE (28)

Flip over after crash using motor reversing.

### AUTOTUNE (15)

Automatic PID tuning using chirp inputs.

### SYSTEMID (25)

System identification with chirp signals.

## Mode Transitions

```cpp
bool Copter::set_mode(Mode::Number mode, ModeReason reason) {
    Mode *new_flightmode = mode_from_mode_num(mode);
    if (new_flightmode == nullptr) {
        return false;
    }

    if (!new_flightmode->init(false)) {
        mode_change_failed(new_flightmode, "init failed");
        return false;
    }

    exit_mode(flightmode, new_flightmode);
    flightmode = new_flightmode;

    return true;
}
```
