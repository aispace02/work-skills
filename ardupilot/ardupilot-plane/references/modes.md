# Plane Flight Modes

## Mode Base Class

**Location**: `ArduPlane/mode.h`, `ArduPlane/mode.cpp`

```cpp
class Mode {
public:
    enum Number : uint8_t {
        MANUAL        = 0,
        CIRCLE        = 1,
        STABILIZE     = 2,
        TRAINING      = 3,
        ACRO          = 4,
        FLY_BY_WIRE_A = 5,
        FLY_BY_WIRE_B = 6,
        CRUISE        = 7,
        AUTOTUNE      = 8,
        AUTO          = 10,
        RTL           = 11,
        LOITER        = 12,
        TAKEOFF       = 13,
        AVOID_ADSB    = 14,
        GUIDED        = 15,
        INITIALISING  = 16,
        QSTABILIZE    = 17,
        QHOVER        = 18,
        QLOITER       = 19,
        QLAND         = 20,
        QRTL          = 21,
        QAUTOTUNE     = 22,
        QACRO         = 23,
        THERMAL       = 24,
        LOITER_ALT_QLAND = 25,
        AUTOLAND      = 26,
    };

    // Required overrides
    virtual Number mode_number() const = 0;
    virtual const char *name() const = 0;
    virtual const char *name4() const = 0;
    virtual void update() = 0;

    // Lifecycle
    bool enter();
    void exit();
    virtual void run();

    // Mode properties
    virtual bool is_vtol_mode() const { return false; }
    virtual bool does_auto_navigation() const { return false; }
    virtual bool does_auto_throttle() const { return false; }
    virtual bool allows_throttle_nudging() const { return false; }
    virtual bool is_guided_mode() const { return false; }
    virtual bool is_landing() const { return false; }
    virtual bool is_taking_off() const;

protected:
    virtual bool _enter() { return true; }
    virtual void _exit() {}
};
```

## Mode Categories

### Manual Modes

| Mode | Description |
|------|-------------|
| **MANUAL** | Direct RC passthrough, no stabilization |
| **ACRO** | Rate-based control, aerobatic |
| **TRAINING** | Like manual but won't exceed pitch/roll limits |

### Assisted Modes

| Mode | Description |
|------|-------------|
| **STABILIZE** | Self-leveling, pilot controls throttle |
| **FLY_BY_WIRE_A** | Roll/pitch stabilized, pilot throttle |
| **FLY_BY_WIRE_B** | Altitude hold, pilot controls climb rate |
| **CRUISE** | Heading lock + altitude hold |

### Autonomous Modes

| Mode | Description |
|------|-------------|
| **AUTO** | Execute mission waypoints |
| **GUIDED** | External control (GCS/script) |
| **RTL** | Return to launch |
| **LOITER** | Circle at current location |
| **CIRCLE** | Circle at specified point |
| **TAKEOFF** | Automatic takeoff |
| **AUTOLAND** | Automatic landing |
| **THERMAL** | Thermal soaring |
| **AUTOTUNE** | Auto PID tuning |

### QuadPlane VTOL Modes

| Mode | Description |
|------|-------------|
| **QSTABILIZE** | Multicopter stabilize |
| **QHOVER** | Multicopter altitude hold |
| **QLOITER** | Multicopter position hold |
| **QLAND** | Multicopter landing |
| **QRTL** | VTOL return to launch |
| **QACRO** | Multicopter acro |
| **LOITER_ALT_QLAND** | Loiter then VTOL land |

---

## Key Mode Implementations

### ModeManual

Direct passthrough of RC inputs.

```cpp
void ModeManual::update() {
    // No stabilization - direct passthrough
    SRV_Channels::set_output_scaled(SRV_Channel::k_aileron,
        plane.channel_roll->get_control_in_zero_dz());
    SRV_Channels::set_output_scaled(SRV_Channel::k_elevator,
        plane.channel_pitch->get_control_in_zero_dz());
    SRV_Channels::set_output_scaled(SRV_Channel::k_rudder,
        plane.channel_rudder->get_control_in_zero_dz());
    output_pilot_throttle();
}
```

### ModeFBWA (Fly-By-Wire A)

Roll/pitch stabilized, pilot controls attitude angles.

```cpp
void ModeFBWA::update() {
    // Get pilot desired angles
    plane.nav_roll_cd = plane.channel_roll->norm_input() *
                        plane.roll_limit_cd;
    plane.nav_pitch_cd = plane.channel_pitch->norm_input() *
                         plane.aparm.pitch_limit_max_cd;
}

void ModeFBWA::run() {
    // Stabilize to desired angles
    plane.stabilize_roll();
    plane.stabilize_pitch();
    plane.stabilize_yaw();
    output_pilot_throttle();
}
```

### ModeFBWB (Fly-By-Wire B)

Altitude hold with climb rate control.

```cpp
void ModeFBWB::update() {
    // Roll control same as FBWA
    plane.nav_roll_cd = plane.channel_roll->norm_input() *
                        plane.roll_limit_cd;

    // Pitch stick controls climb rate (via TECS)
    float climb_rate = plane.channel_pitch->norm_input() *
                       plane.TECS_controller.get_max_climbrate();
    plane.TECS_controller.set_target_climbrate(climb_rate);
}
```

### ModeCruise

Heading and altitude hold.

```cpp
void ModeCruise::update() {
    // Lock heading when stick centered
    if (fabsf(plane.channel_roll->norm_input()) < 0.05f) {
        if (!locked_heading) {
            locked_heading = true;
            locked_heading_cd = plane.ahrs.yaw_sensor;
        }
        plane.nav_roll_cd = plane.nav_controller->lateral_acceleration_demand() *
                            plane.roll_limit_cd;
    } else {
        locked_heading = false;
        plane.nav_roll_cd = plane.channel_roll->norm_input() *
                            plane.roll_limit_cd;
    }
    // Altitude same as FBWB
}

void ModeCruise::navigate() {
    if (locked_heading) {
        plane.nav_controller->update_heading(locked_heading_cd);
    }
}
```

### ModeAuto

Execute mission commands.

```cpp
void ModeAuto::update() {
    // Run mission
    plane.mission.update();
}

void ModeAuto::navigate() {
    // Navigate to current waypoint
    plane.nav_controller->update_waypoint(
        plane.prev_WP_loc,
        plane.next_WP_loc
    );
    plane.calc_nav_roll();
    plane.calc_nav_pitch();
}

bool ModeAuto::does_auto_navigation() const { return true; }
bool ModeAuto::does_auto_throttle() const { return true; }
```

### ModeRTL

Return to launch.

```cpp
bool ModeRTL::_enter() {
    // Set target to home or rally point
    plane.prev_WP_loc = plane.current_loc;
    plane.next_WP_loc = plane.calc_best_rally_or_home_location(
        plane.current_loc,
        plane.get_RTL_altitude_cm()
    );
    return true;
}

void ModeRTL::navigate() {
    // Navigate to home/rally
    plane.nav_controller->update_waypoint(
        plane.prev_WP_loc,
        plane.next_WP_loc
    );

    // Check for QRTL transition (QuadPlane)
    if (plane.quadplane.available()) {
        switch_QRTL();
    }
}
```

### ModeLoiter

Circle at current location.

```cpp
bool ModeLoiter::_enter() {
    // Set loiter center to current location
    plane.next_WP_loc = plane.current_loc;
    return true;
}

void ModeLoiter::navigate() {
    // Circle around loiter point
    plane.nav_controller->update_loiter(
        plane.next_WP_loc,
        plane.aparm.loiter_radius,
        plane.loiter.direction
    );
}
```

### ModeTakeoff

Automatic takeoff.

```cpp
void ModeTakeoff::update() {
    // Set takeoff pitch
    if (!plane.takeoff_state.complete) {
        plane.nav_pitch_cd = target_pitch_cd();
    }
}

void ModeTakeoff::navigate() {
    // Fly toward takeoff waypoint
    plane.nav_controller->update_waypoint(start_loc, takeoff_loc);

    // Check completion
    if (plane.current_loc.alt > (start_loc.alt + target_alt * 100)) {
        plane.takeoff_state.complete = true;
    }
}
```

---

## Mode Properties Summary

| Mode | Auto Nav | Auto Throttle | VTOL | Throttle Nudge |
|------|----------|---------------|------|----------------|
| MANUAL | No | No | No | No |
| STABILIZE | No | No | No | No |
| FBWA | No | No | No | No |
| FBWB | No | Yes | No | No |
| CRUISE | No | Yes | No | No |
| AUTO | Yes | Yes | No | Yes |
| GUIDED | Yes | Yes | No | Yes |
| RTL | Yes | Yes | No | Yes |
| LOITER | Yes | Yes | No | Yes |
| CIRCLE | Yes | Yes | No | No |
| QSTABILIZE | No | No | Yes | No |
| QHOVER | No | No | Yes | No |
| QLOITER | No | No | Yes | No |

---

## Adding a New Mode

1. **Define mode class** in `mode.h`:
```cpp
class ModeCustom : public Mode {
public:
    Number mode_number() const override { return Number::CUSTOM; }
    const char *name() const override { return "CUSTOM"; }
    const char *name4() const override { return "CUST"; }

    void update() override;
    void run() override;
    bool does_auto_throttle() const override { return true; }

protected:
    bool _enter() override;
};
```

2. **Implement** in `mode_custom.cpp`:
```cpp
bool ModeCustom::_enter() {
    // Initialize mode state
    return true;
}

void ModeCustom::update() {
    // Mode-specific control logic
}

void ModeCustom::run() {
    // Attitude stabilization
    plane.stabilize_roll();
    plane.stabilize_pitch();
    plane.stabilize_yaw();
}
```

3. **Add instance** to `Plane.h`:
```cpp
ModeCustom mode_custom;
```

4. **Register** in `control_modes.cpp`:
```cpp
case Mode::Number::CUSTOM:
    return &mode_custom;
```
