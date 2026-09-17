# AntennaTracker Modes

## Mode System

**Files**: `mode.h`, `mode.cpp`, `mode_*.cpp`

## Mode Numbers

```cpp
enum class Number {
    MANUAL       = 0,   // RC pass-through
    STOP         = 1,   // Servos stopped
    SCAN         = 2,   // Automatic scanning
    SERVOTEST    = 3,   // Servo testing
    GUIDED       = 4,   // GCS-commanded
    AUTO         = 10,  // Vehicle tracking
    INITIALISING = 16,  // Startup
};
```

## Mode Base Class

```cpp
class Mode {
public:
    virtual void update() = 0;
    virtual bool requires_armed_servos() const { return false; }
    virtual const char *name() const = 0;
    virtual Number number() const = 0;

protected:
    void update_auto();      // Track vehicle
    void update_scan();      // Scan pattern

    void calc_angle_error(float pitch, float yaw, bool direction_reversed);
    void convert_ef_to_bf(float pitch, float yaw, float& bf_pitch, float& bf_yaw);
    bool convert_bf_to_ef(float pitch, float yaw, float& ef_pitch, float& ef_yaw);
    bool get_ef_yaw_direction();
};
```

## Mode Details

### MANUAL (0)

Direct RC pass-through to servos.

**File**: `mode_manual.cpp`

```cpp
void ModeManual::update() {
    // Copy RC input directly to servo output
    SRV_Channels::set_output_pwm(SRV_Channel::k_tracker_yaw,
                                  RC_Channels::rc_channel(CH_YAW)->get_radio_in());
    SRV_Channels::set_output_pwm(SRV_Channel::k_tracker_pitch,
                                  RC_Channels::rc_channel(CH_PITCH)->get_radio_in());
}
```

**Characteristics**:
- No PID control
- Direct PWM pass-through
- Full manual control

### STOP (1)

Servos held at current position or zeroed.

```cpp
void ModeStop::update() {
    // Output controlled by SAFE_DISARM_PWM parameter
    // 0 = zero PWM, 1 = trim PWM
}
```

**Characteristics**:
- Safe mode for transport
- Controlled by `SAFE_DISARM_PWM`

### SCAN (2)

Continuous automatic scanning pattern.

**File**: `mode_scan.cpp`

```cpp
void ModeScan::update() {
    update_scan();  // Inherited scanning logic
}
```

**Algorithm** (in `mode.cpp`):
```cpp
void Mode::update_scan() {
    // Yaw scanning
    if (!nav_status.manual_control_yaw) {
        float yaw_delta = g.scan_speed_yaw * 0.02f;
        nav_status.bearing += yaw_delta * (scan_reverse_yaw ? -1 : 1);

        // Reverse at limits
        if (nav_status.bearing < 0) scan_reverse_yaw = false;
        if (nav_status.bearing > 360) scan_reverse_yaw = true;
    }

    // Pitch scanning
    if (!nav_status.manual_control_pitch) {
        float pitch_delta = g.scan_speed_pitch * 0.02f;
        // Oscillate between pitch_min and pitch_max
    }

    update_auto();  // Apply to servos
}
```

**Parameters**:
- `SCAN_SPEED_YAW` - Yaw scan rate (deg/s)
- `SCAN_SPEED_PIT` - Pitch scan rate (deg/s)

### SERVOTEST (3)

Servo diagnostic mode for testing movement.

**File**: `mode_servotest.cpp`

```cpp
void ModeServoTest::update() {
    // Servos controlled via MAVLink commands
    // Used for testing servo range and response
}
```

### GUIDED (4)

GCS-commanded pointing direction.

**File**: `mode_guided.cpp`

```cpp
void ModeGuided::update() {
    if (tracker.guided_target.valid) {
        // Point to GCS-specified location
        tracker.update_bearing_and_distance();
        update_auto();
    }
}
```

**MAVLink Commands**:
- `SET_ATTITUDE_TARGET` - Set yaw/pitch directly
- `SET_POSITION_TARGET_GLOBAL_INT` - Point to location

### AUTO (10)

Automatic vehicle tracking.

**File**: `mode_auto.cpp`

```cpp
void ModeAuto::update() {
    if (tracker.vehicle.location_valid) {
        update_auto();  // Track vehicle
    } else if (tracker.target_set || (g.auto_opts.get() & (1 << 0))) {
        update_scan();  // Scan for unknown target
    }
}
```

**Features**:
- Tracks vehicle via MAVLink position
- Falls back to scan if no target
- Controlled by `AUTO_OPTIONS` bitmask

### INITIALISING (16)

Startup mode during initialization.

**Characteristics**:
- Active during boot
- Transitions to `INITIAL_MODE` when ready

## Mode Switching

### Set Mode Function
```cpp
bool Tracker::set_mode(Mode &newmode, ModeReason reason) {
    if (!newmode.init()) {
        return false;
    }
    mode = &newmode;
    gcs().send_message(MSG_HEARTBEAT);
    return true;
}
```

### Mode Selection
```cpp
Mode* Tracker::mode_from_mode_num(Mode::Number num) {
    switch (num) {
        case Mode::Number::MANUAL: return &mode_manual;
        case Mode::Number::STOP: return &mode_stop;
        case Mode::Number::SCAN: return &mode_scan;
        case Mode::Number::SERVOTEST: return &mode_servotest;
        case Mode::Number::GUIDED: return &mode_guided;
        case Mode::Number::AUTO: return &mode_auto;
        case Mode::Number::INITIALISING: return &mode_initialising;
    }
    return nullptr;
}
```

## Common Mode Utilities

### update_auto()

Core tracking algorithm used by AUTO, SCAN, GUIDED:

```cpp
void Mode::update_auto() {
    // Get target angles with trim
    float yaw_deg = wrap_180(nav_status.bearing + g.yaw_trim);
    float pitch_deg = constrain_float(nav_status.pitch + g.pitch_trim,
                                       g.pitch_min, g.pitch_max);

    // Convert to centidegrees
    float yaw = yaw_deg * 100;
    float pitch = pitch_deg * 100;

    // Check if we need reversed yaw direction
    bool direction_reversed = get_ef_yaw_direction();

    // Calculate angle error
    calc_angle_error(pitch, yaw, direction_reversed);

    // Convert earth frame to body frame
    float bf_pitch, bf_yaw;
    convert_ef_to_bf(pitch, yaw, bf_pitch, bf_yaw);

    // Update servos (if target far enough)
    if ((g.distance_min <= 0) ||
        (nav_status.distance >= g.distance_min) ||
        !tracker.vehicle.location_valid) {
        tracker.update_pitch_servo(bf_pitch);
        tracker.update_yaw_servo(bf_yaw);
    }
}
```

### calc_angle_error()

Calculate error between target and actual angles:

```cpp
void Mode::calc_angle_error(float pitch, float yaw, bool direction_reversed) {
    // Pitch error = target - actual
    float ahrs_pitch = ahrs.pitch_sensor;
    int32_t ef_pitch_angle_error = pitch - ahrs_pitch;

    // Yaw error with wrapping
    int32_t ahrs_yaw_cd = wrap_180_cd(ahrs.yaw_sensor);
    int32_t ef_yaw_angle_error = wrap_180_cd(yaw - ahrs_yaw_cd);

    // Handle reversed direction (for limited yaw range)
    if (direction_reversed) {
        // Take the long way around
    }

    // Store errors for PID
    nav_status.angle_error_pitch = bf_pitch_err;
    nav_status.angle_error_yaw = bf_yaw_err;
}
```

## Mode Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `INITIAL_MODE` | Startup mode | 10 (AUTO) |
| `SCAN_SPEED_YAW` | Yaw scan speed (deg/s) | 2 |
| `SCAN_SPEED_PIT` | Pitch scan speed (deg/s) | 5 |
| `AUTO_OPTIONS` | Auto mode options bitmask | 0 |

## AUTO_OPTIONS Bitmask

| Bit | Value | Description |
|-----|-------|-------------|
| 0 | 1 | Scan for unknown target |
