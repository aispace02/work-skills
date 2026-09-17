# ArduSub Architecture

## System Overview

ArduSub is built on the ArduPilot framework, inheriting from `AP_Vehicle` and providing ROV/submarine-specific functionality.

## Class Hierarchy

```
AP_Vehicle
    └── Sub
            ├── Mode (base class)
            │   ├── ModeManual
            │   ├── ModeStabilize
            │   ├── ModeAcro
            │   ├── ModeAlthold
            │   │   ├── ModeSurftrak
            │   │   └── ModePoshold
            │   ├── ModeGuided
            │   │   └── ModeAuto
            │   ├── ModeCircle
            │   ├── ModeSurface
            │   └── ModeMotordetect
            │
            ├── AP_Motors6DOF (motors)
            ├── AC_AttitudeControl_Sub (attitude_control)
            ├── AC_PosControl (pos_control)
            ├── AC_WPNav (wp_nav)
            ├── AC_Loiter (loiter_nav)
            ├── AC_Circle (circle_nav)
            └── AP_InertialNav (inertial_nav)
```

## Main Components

### Sub Class (Sub.h)

The main vehicle class containing:
- Mode instances
- Motor controller
- Navigation controllers
- Sensor interfaces
- State flags

```cpp
class Sub : public AP_Vehicle {
    // Motors
    AP_Motors6DOF motors;

    // Controllers
    AC_AttitudeControl_Sub attitude_control;
    AC_PosControl pos_control;
    AC_WPNav wp_nav;
    AC_Loiter loiter_nav;
    AC_Circle circle_nav;

    // Navigation
    AP_InertialNav inertial_nav;

    // Current mode
    Mode *flightmode;
    Mode::Number control_mode;

    // State
    struct {
        uint8_t at_bottom : 1;
        uint8_t at_surface : 1;
        uint8_t depth_sensor_present : 1;
        // ...
    } ap;
};
```

### Mode Base Class (mode.h)

All modes inherit from `Mode`:

```cpp
class Mode {
public:
    enum class Number : uint8_t {
        STABILIZE = 0,
        ACRO = 1,
        ALT_HOLD = 2,
        AUTO = 3,
        GUIDED = 4,
        CIRCLE = 7,
        SURFACE = 9,
        POSHOLD = 16,
        MANUAL = 19,
        MOTOR_DETECT = 20,
        SURFTRAK = 21
    };

    // Virtual methods
    virtual bool init(bool ignore_checks) { return true; }
    virtual void run() = 0;
    virtual bool requires_GPS() const = 0;
    virtual bool requires_altitude() const = 0;
    virtual bool allows_arming(bool from_gcs) const = 0;
    virtual const char *name() const = 0;
    virtual Number number() const = 0;

protected:
    // Access to vehicle systems
    Parameters &g;
    AP_Motors6DOF &motors;
    AC_PosControl *position_control;
    AC_AttitudeControl_Sub *attitude_control;
    RC_Channel *&channel_roll;
    RC_Channel *&channel_pitch;
    RC_Channel *&channel_throttle;
    RC_Channel *&channel_yaw;
    RC_Channel *&channel_forward;
    RC_Channel *&channel_lateral;
};
```

## Scheduler

Main loop runs at configurable rate (default 400Hz for Navigator, 200Hz otherwise):

```cpp
const AP_Scheduler::Task Sub::scheduler_tasks[] = {
    // Fast tasks (every loop)
    FAST_TASK(run_rate_controller),
    FAST_TASK(motors_output),
    FAST_TASK(read_AHRS),
    FAST_TASK(read_inertia),
    FAST_TASK(update_flight_mode),
    FAST_TASK(update_surface_and_bottom_detector),

    // Scheduled tasks
    SCHED_TASK(fifty_hz_loop, 50, 75, 3),
    SCHED_TASK(update_batt_compass, 10, 120, 12),
    SCHED_TASK(read_rangefinder, 20, 100, 15),
    SCHED_TASK(update_altitude, 10, 100, 18),
    SCHED_TASK(three_hz_loop, 3, 75, 21),
    SCHED_TASK(one_hz_loop, 1, 100, 33),
    // ...
};
```

## Control Flow

### Main Loop

```
1. INS Update (read sensors)
2. Rate Controller (attitude rates)
3. Motors Output (PWM)
4. AHRS Update (attitude estimation)
5. Inertia Update (position estimation)
6. Flight Mode Update (mode-specific logic)
7. Surface/Bottom Detection
```

### Mode Execution

```cpp
void Sub::update_flight_mode()
{
    flightmode->run();
}
```

Each mode's `run()` method:
1. Checks armed state
2. Reads pilot inputs
3. Runs attitude control
4. Sets motor outputs

## Input Channels

ArduSub uses 6 RC channels for full 6DOF control:

```cpp
RC_Channel *channel_roll;      // Roll attitude
RC_Channel *channel_pitch;     // Pitch attitude
RC_Channel *channel_throttle;  // Vertical (heave)
RC_Channel *channel_yaw;       // Yaw rate
RC_Channel *channel_forward;   // Forward/backward (surge)
RC_Channel *channel_lateral;   // Left/right (sway)
```

## State Management

### Arming State

```cpp
motors.armed()  // Check if armed
arming.arm(method)  // Arm motors
arming.disarm(method)  // Disarm motors
```

### Position State

```cpp
ap.at_surface  // True when at/above surface
ap.at_bottom   // True when at bottom
ap.depth_sensor_present  // True if depth sensor detected
```

### Failsafe State

```cpp
failsafe.leak      // Leak detected
failsafe.ekf       // EKF unhealthy
failsafe.gcs       // GCS heartbeat lost
failsafe.pilot_input  // Pilot input lost
failsafe.sensor_health  // Sensor error
```

## Memory Layout

Parameters are stored in two groups:
- `g` (Parameters): Primary parameters
- `g2` (ParametersG2): Extended parameters

```cpp
// Access parameters
float gain = g.gain_default.get();
float depth = g.surface_depth.get();
```

## File Organization

```
ArduSub/
├── Sub.h/cpp              # Main class
├── mode.h                 # Mode definitions
├── mode_*.cpp             # Mode implementations
├── Parameters.h/cpp       # Parameter system
├── motors.cpp             # Motor output
├── joystick.cpp           # Joystick input
├── failsafe.cpp           # Failsafe handling
├── GCS_MAVLink_Sub.cpp    # MAVLink handling
├── commands_logic.cpp     # Mission commands
├── surface_bottom_detector.cpp  # Detection
└── defines.h              # Constants
```
