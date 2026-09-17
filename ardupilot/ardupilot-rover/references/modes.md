# Rover Flight Modes

## Mode Base Class

**Location**: `Rover/mode.h`, `Rover/mode.cpp`

```cpp
class Mode {
public:
    // Identification
    virtual Number mode_number() const = 0;
    virtual const char *name4() const = 0;  // 4-char name

    // Lifecycle
    bool enter();                // Call to enter mode
    void exit();                 // Call to exit mode
    virtual void update() = 0;   // Called every loop

    // Mode properties
    virtual bool is_autopilot_mode() const { return false; }
    virtual bool has_manual_input() const { return false; }
    virtual bool attitude_stabilized() const { return true; }
    virtual bool allows_arming() const { return true; }
    virtual bool in_guided_mode() const { return false; }
    virtual bool requires_position() const { return false; }
    virtual bool requires_velocity() const { return false; }

    // Navigation
    virtual float get_distance_to_destination() const { return 0.0f; }
    virtual bool get_desired_location(Location& dest) const;
    virtual bool set_desired_location(const Location& dest);
    virtual bool reached_destination() const { return true; }

protected:
    // Override in subclass
    virtual bool _enter() { return true; }
    virtual void _exit() {}

    // Rover references
    Rover &rover;
    Parameters &g;
    ParametersG2 &g2;

    // Helper methods (available to all modes)
    void get_pilot_desired_steering_and_throttle(float &steer, float &throttle);
    void get_pilot_desired_steering_and_speed(float &steer, float &speed);
    void get_pilot_desired_heading_and_speed(float &heading, float &speed);
    void get_pilot_desired_lateral(float &lateral);
    void calc_throttle(float target_speed, bool avoidance_enabled);
    void calc_steering_to_heading(float desired_heading_cd, float rate_max_degs);
    void calc_steering_from_turn_rate(float turn_rate);
    void calc_steering_from_lateral_acceleration(float lat_accel);
    bool stop_vehicle();
    void navigate_to_waypoint();
    float calc_speed_max(float cruise_speed, float cruise_throttle) const;
};
```

## Mode Categories

### Manual Modes

| Mode | Number | Description |
|------|--------|-------------|
| MANUAL | 0 | Direct RC control, no stabilization |
| ACRO | 1 | Rate-based steering with stabilization |
| STEERING | 3 | Heading + throttle control |
| SIMPLE | 7 | Simplified heading reference |

### Autonomous Modes

| Mode | Number | Description |
|------|--------|-------------|
| AUTO | 10 | Execute mission waypoints |
| GUIDED | 15 | External control (GCS/script) |
| RTL | 11 | Return to launch |
| SMART_RTL | 12 | Return via recorded path |
| LOITER | 5 | Hold position/circle |
| CIRCLE | 9 | Circle a point |
| FOLLOW | 6 | Follow another vehicle |
| DOCK | 8 | Autonomous docking |

### Failsafe Modes

| Mode | Number | Description |
|------|--------|-------------|
| HOLD | 4 | Stop and hold position |

---

## Mode Implementations

### ModeManual

**File**: `mode_manual.cpp`

Direct passthrough of RC inputs to motors.

```cpp
void ModeManual::update() {
    float steering, throttle;
    get_pilot_desired_steering_and_throttle(steering, throttle);

    // Direct output
    g2.motors.set_steering(steering);
    g2.motors.set_throttle(throttle);

    // Lateral for boats
    float lateral;
    get_pilot_desired_lateral(lateral);
    g2.motors.set_lateral(lateral);
}
```

### ModeAuto

**File**: `mode_auto.cpp`

Executes mission commands from AP_Mission.

```cpp
class ModeAuto : public Mode {
    bool is_autopilot_mode() const override { return true; }

    // Mission command handling
    bool start_command(const AP_Mission::Mission_Command& cmd);
    void exit_mission();
    bool verify_command(const AP_Mission::Mission_Command& cmd);

    // Sub-modes
    enum class SubMode {
        WP,              // Navigate to waypoint
        HeadingAndSpeed, // Heading + speed command
        Stop,            // Stopping
        NavScriptTime,   // Scripted navigation
        Loiter           // Loiter in auto
    };
    SubMode _submode;

protected:
    bool _enter() override;
    void update() override;
};

void ModeAuto::update() {
    switch (_submode) {
        case SubMode::WP:
            navigate_to_waypoint();
            if (verify_nav_wp()) {
                rover.mission.advance_current_nav_cmd();
            }
            break;
        case SubMode::HeadingAndSpeed:
            // Navigate at fixed heading and speed
            break;
        case SubMode::Stop:
            stop_vehicle();
            break;
        // ...
    }
}
```

**Mission Commands Supported**:
- `MAV_CMD_NAV_WAYPOINT` - Go to waypoint
- `MAV_CMD_NAV_RETURN_TO_LAUNCH` - RTL
- `MAV_CMD_NAV_LOITER_UNLIM` - Loiter forever
- `MAV_CMD_NAV_LOITER_TIME` - Loiter for time
- `MAV_CMD_NAV_SET_YAW_SPEED` - Heading + speed
- `MAV_CMD_DO_SET_REVERSE` - Set reverse direction
- `MAV_CMD_DO_CHANGE_SPEED` - Change speed
- Plus conditional and DO commands

### ModeGuided

**File**: `mode_guided.cpp`

External control via MAVLink or scripts.

```cpp
class ModeGuided : public Mode {
    bool is_autopilot_mode() const override { return true; }
    bool in_guided_mode() const override { return true; }

    // Control inputs
    bool set_desired_speed_and_heading(float speed, float heading);
    bool set_desired_location(const Location &loc) override;
    bool set_desired_loiter_heading_and_speed(float heading, float speed);
    bool set_desired_attitude(float heading, float body_rate);

    enum class SubMode {
        WP,
        HeadingAndSpeed,
        TurnRateAndSpeed,
        Loiter,
        Stop
    };
    SubMode _guided_mode;
};

void ModeGuided::update() {
    switch (_guided_mode) {
        case SubMode::WP:
            navigate_to_waypoint();
            break;
        case SubMode::HeadingAndSpeed:
            calc_steering_to_heading(_desired_heading, g2.wp_nav.get_turn_max_rads());
            calc_throttle(_desired_speed, true);
            break;
        case SubMode::TurnRateAndSpeed:
            calc_steering_from_turn_rate(_desired_turn_rate);
            calc_throttle(_desired_speed, true);
            break;
        // ...
    }
}
```

### ModeRTL

**File**: `mode_rtl.cpp`

Returns directly to home position.

```cpp
void ModeRTL::update() {
    navigate_to_waypoint();
}

bool ModeRTL::_enter() {
    // Set destination to home
    if (!set_desired_location(rover.home)) {
        return false;
    }
    g2.wp_nav.set_speed(g.rtl_speed);
    return true;
}
```

### ModeSmartRTL

**File**: `mode_smartrtl.cpp`

Returns along the recorded path.

```cpp
void ModeSmartRTL::update() {
    switch (_state) {
        case STATE_ACTIVE:
            // Get next point from SmartRTL path
            if (g2.smart_rtl.get_next_point(_next_point)) {
                set_desired_location(_next_point);
            }
            navigate_to_waypoint();
            break;
        case STATE_HOME:
            // Final approach to home
            navigate_to_waypoint();
            break;
    }
}
```

### ModeLoiter

**File**: `mode_loiter.cpp`

Hold position with optional loitering.

```cpp
void ModeLoiter::update() {
    // Get distance and bearing to loiter point
    float dist = current_loc.get_distance(_destination);
    float bearing = current_loc.get_bearing_to(_destination);

    if (dist <= g2.loit_radius) {
        // Inside loiter radius - stop or circle
        if (g2.loit_type == LOITER_TYPE_STOP) {
            stop_vehicle();
        } else {
            // Circle at loiter point
            calc_steering_to_heading(bearing + 90, ...);
        }
    } else {
        // Navigate to loiter point
        navigate_to_waypoint();
    }
}
```

### ModeCircle

**File**: `mode_circle.cpp`

Circle around a center point.

```cpp
void ModeCircle::update() {
    // Calculate target point on circle
    float angle = _start_angle + _direction * _angle_total;
    Location target;
    target.offset_bearing(_center, angle, _radius);

    set_desired_location(target);
    navigate_to_waypoint();

    // Update angle progress
    _angle_total += rover.G_Dt * _rate_rad;
}
```

### ModeFollow

**File**: `mode_follow.cpp`

Follow another vehicle (FOLLOW_SYSID).

```cpp
void ModeFollow::update() {
    // Get target vehicle position from AP_Follow
    Location target_loc;
    Vector3f target_vel;

    if (!g2.follow.get_target_location_and_velocity(target_loc, target_vel)) {
        return;  // No valid target
    }

    // Offset from target
    target_loc.offset_bearing(g2.follow.get_offset_bearing(),
                               g2.follow.get_offset_distance());

    set_desired_location(target_loc);
    navigate_to_waypoint();
}
```

### ModeDock

**File**: `mode_dock.cpp`

Autonomous docking to a target.

```cpp
void ModeDock::update() {
    switch (_state) {
        case STATE_APPROACH:
            // Approach dock target
            navigate_to_waypoint();
            if (reached_destination()) {
                _state = STATE_FINAL;
            }
            break;
        case STATE_FINAL:
            // Final docking with precision
            // Uses dock sensor if available
            break;
        case STATE_DOCKED:
            stop_vehicle();
            break;
    }
}
```

---

## Common Mode Patterns

### Navigation Pattern

```cpp
void ModeXxx::update() {
    // Update waypoint navigation
    g2.wp_nav.update(rover.G_Dt);

    // Get steering from turn rate
    float turn_rate = g2.wp_nav.get_turn_rate_rads();
    calc_steering_from_turn_rate(turn_rate);

    // Get throttle from target speed
    float target_speed = g2.wp_nav.get_speed();
    calc_throttle(target_speed, true);  // true = avoidance enabled
}
```

### Heading + Speed Pattern

```cpp
void ModeXxx::update() {
    float desired_heading = radians(90.0f);  // East
    float desired_speed = 2.0f;              // m/s

    calc_steering_to_heading(degrees(desired_heading) * 100,
                             g2.wp_nav.get_turn_max_rads());
    calc_throttle(desired_speed, true);
}
```

### Manual Input Pattern

```cpp
void ModeXxx::update() {
    float steering, throttle;
    get_pilot_desired_steering_and_throttle(steering, throttle);

    // Mix with autopilot or use directly
    g2.motors.set_steering(steering);
    g2.motors.set_throttle(throttle);
}
```

### Stop Pattern

```cpp
void ModeXxx::update() {
    if (stop_vehicle()) {
        // Vehicle has stopped
        // Transition to next state
    }
}
```

---

## Mode Entry Requirements

| Mode | Position Required | Velocity Required | Notes |
|------|------------------|-------------------|-------|
| Manual | No | No | Always available |
| Acro | No | No | Always available |
| Steering | No | No | Always available |
| Hold | No | No | Always available |
| Auto | Yes | No | Needs valid position |
| Guided | Yes | No | Needs valid position |
| RTL | Yes | No | Needs home + position |
| SmartRTL | Yes | No | Needs recorded path |
| Loiter | Yes | No | Needs valid position |
| Circle | Yes | No | Needs valid position |
| Follow | Yes | Yes | Needs target + position |

---

## Adding a New Mode

1. **Create header section** in `mode.h`:
```cpp
class ModeCustom : public Mode {
public:
    Number mode_number() const override { return Number::CUSTOM; }
    const char *name4() const override { return "CUST"; }
    bool is_autopilot_mode() const override { return true; }

    void update() override;

protected:
    bool _enter() override;
    void _exit() override;
};
```

2. **Create implementation** `mode_custom.cpp`:
```cpp
bool ModeCustom::_enter() {
    // Initialize mode
    return true;
}

void ModeCustom::update() {
    // Your control logic
}

void ModeCustom::_exit() {
    // Cleanup
}
```

3. **Add to Rover class** in `Rover.h`:
```cpp
ModeCustom mode_custom;
```

4. **Register in mode_from_mode_num()** in `system.cpp`:
```cpp
case Mode::Number::CUSTOM:
    return &mode_custom;
```

5. **Add mode number** to enum if needed in `mode.h`
