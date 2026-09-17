# Specialized Control Libraries

Special-purpose control libraries.

## AC_Sprayer

**Location**: `libraries/AC_Sprayer/AC_Sprayer.h`

**Singleton**: `AC_Sprayer::get_singleton()`

Agricultural crop sprayer control.

### How It Works

1. Pilot enables sprayer via RC switch or auto mode
2. `update()` reads ground speed from AHRS
3. Pump output scales with speed for consistent coverage
4. Spinner maintains constant RPM
5. Below minimum speed, pump stays at minimum (prevents clogging)

### Core Methods

```cpp
// Enable/disable
void run(bool enable);                        // Enable/disable spraying
void update();                                // Call in main loop

// State
bool enabled() const;                         // Is sprayer enabled?
bool running() const;                         // Is pump/spinner running?
bool spraying() const;                        // Above min speed?

// Testing
void test_pump(bool enable);
void test_spinner(bool enable);
```

### Parameters (SPRAY_)

| Parameter | Description |
|-----------|-------------|
| `SPRAY_ENABLE` | Enable sprayer |
| `SPRAY_PUMP_RATE` | Pump rate at cruise speed (%) |
| `SPRAY_PUMP_MIN` | Minimum pump rate (%) |
| `SPRAY_SPINNER` | Spinner PWM value |
| `SPRAY_SPEED_MIN` | Min ground speed to spray (cm/s) |

### Usage

```cpp
void sprayer_update() {
    AC_Sprayer *sprayer = AC_Sprayer::get_singleton();

    // Check RC switch
    if (rc().sprayer_enabled()) {
        sprayer->run(true);
    } else {
        sprayer->run(false);
    }

    // Update pump/spinner based on ground speed
    sprayer->update();

    // Check state for logging
    if (sprayer->spraying()) {
        // Log spray data
    }
}
```

### Servo Setup

```
SPRAY_PUMP_RATE → SERVO channel (k_sprayer_pump)
SPRAY_SPINNER → SERVO channel (k_sprayer_spinner)
```

---

## AC_CustomControl

**Location**: `libraries/AC_CustomControl/AC_CustomControl.h`

User-replaceable attitude controller for research.

### Architecture

```cpp
AC_CustomControl                    // Frontend
├── AC_CustomControl_Backend        // Interface
│   ├── AC_CustomControl_Empty      // Passthrough (does nothing)
│   └── AC_CustomControl_PID        // Example PID implementation
```

### Core Methods

```cpp
// Lifecycle
void init();
void reset();

// Control - returns motor outputs (roll, pitch, yaw)
Vector3f update();

// Enable/disable
void set_custom_controller(bool enable);

// Backend access
AC_CustomControl_Backend* get_backend() const;
```

### Parameters (CC_)

| Parameter | Description |
|-----------|-------------|
| `CC_TYPE` | Controller type (0=None, 1=Empty, 2=PID) |
| `CC_AXIS_MASK` | Axes to control (1=Roll, 2=Pitch, 4=Yaw) |

### Usage

```cpp
// Enable via parameters:
// CC_TYPE = 2
// CC_AXIS_MASK = 7  (all axes)

void custom_control_example() {
    AC_CustomControl custom_ctrl(attitude_control, ahrs);
    custom_ctrl.init();

    // In control loop:
    Vector3f motor_out = custom_ctrl.update();

    // motor_out.x = roll output
    // motor_out.y = pitch output
    // motor_out.z = yaw output
}
```

### Creating Custom Backend

```cpp
// MyController.h
#pragma once

#include "AC_CustomControl_Backend.h"

class AC_CustomControl_MyController : public AC_CustomControl_Backend {
public:
    AC_CustomControl_MyController(AC_CustomControl &frontend,
                                   AP_AHRS &ahrs,
                                   AC_AttitudeControl &att_ctrl);

    // Required interface
    Vector3f update() override;
    void reset() override;

    // Parameters
    static const struct AP_Param::GroupInfo var_info[];

private:
    // Your control law
    float _my_gain;
    AC_PID _roll_pid;
    AC_PID _pitch_pid;
    AC_PID _yaw_pid;
};

// MyController.cpp
Vector3f AC_CustomControl_MyController::update() {
    Vector3f output;

    // Get attitude error
    Quaternion att_error = _att_ctrl.get_att_error_quat();
    Vector3f rate_target = _att_ctrl.get_att_target_ang_vel_rads();

    // Your custom control law here
    output.x = _roll_pid.update_all(rate_target.x, _ahrs.get_gyro().x, dt);
    output.y = _pitch_pid.update_all(rate_target.y, _ahrs.get_gyro().y, dt);
    output.z = _yaw_pid.update_all(rate_target.z, _ahrs.get_gyro().z, dt);

    return output;
}
```

### Registering Custom Backend

In `AC_CustomControl.cpp`:

```cpp
// Add to backend creation
case CustomControlType::MY_CONTROLLER:
    _backend = NEW_NOTHROW AC_CustomControl_MyController(*this, _ahrs, _att_ctrl);
    break;
```

---

## Integration Notes

### Sprayer with Auto Mode

```cpp
void mode_auto_run() {
    // Normal auto navigation...

    // Sprayer auto-control based on mission commands
    AC_Sprayer *sprayer = AC_Sprayer::get_singleton();

    if (mission.get_current_do_cmd().id == MAV_CMD_DO_SPRAYER) {
        sprayer->run(mission.get_current_do_cmd().p1 > 0);
    }

    sprayer->update();
}
```

### Custom Control Research Workflow

1. Set `CC_TYPE = 0` (disabled) for normal flight
2. Implement and test custom backend in SITL
3. Enable with `CC_TYPE = <your_type>` and `CC_AXIS_MASK`
4. Test single axis first (e.g., `CC_AXIS_MASK = 1` for roll only)
5. Gradually enable more axes

### Safety Considerations

**Sprayer**:
- Always test pump/spinner manually first
- Verify SPRAY_SPEED_MIN prevents ground contamination
- Check failsafe disables sprayer

**CustomControl**:
- Always have kill switch
- Test in SITL extensively
- Start with conservative gains
- Enable one axis at a time
