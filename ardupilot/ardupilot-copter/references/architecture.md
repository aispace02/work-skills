# ArduCopter Architecture

## System Overview

ArduCopter is built on the ArduPilot framework, inheriting from `AP_Vehicle` and providing multicopter/helicopter-specific functionality.

## Class Hierarchy

```
AP_Vehicle
    └── Copter
            ├── Mode (base class)
            │   ├── ModeStabilize
            │   ├── ModeAcro
            │   ├── ModeAltHold
            │   ├── ModeLoiter
            │   ├── ModePosHold
            │   ├── ModeAuto
            │   ├── ModeGuided
            │   ├── ModeRTL
            │   ├── ModeSmartRTL
            │   ├── ModeLand
            │   ├── ModeCircle
            │   ├── ModeDrift
            │   ├── ModeSport
            │   ├── ModeFlip
            │   ├── ModeAutoTune
            │   ├── ModeBrake
            │   ├── ModeThrow
            │   ├── ModeFollow
            │   ├── ModeZigZag
            │   ├── ModeFlowHold
            │   ├── ModeSystemId
            │   ├── ModeTurtle
            │   └── ModeAutorotate (heli only)
            │
            ├── AP_MotorsMulticopter or AP_MotorsHeli (motors)
            ├── AC_AttitudeControl_Multi or AC_AttitudeControl_Heli
            ├── AC_PosControl (pos_control)
            ├── AC_WPNav (wp_nav)
            ├── AC_Loiter (loiter_nav)
            └── AC_Circle (circle_nav)
```

## Main Components

### Copter Class (Copter.h)

The main vehicle class containing:

```cpp
class Copter : public AP_Vehicle {
    // Motor output
    MOTOR_CLASS *motors;  // AP_MotorsMulticopter or AP_MotorsHeli

    // Controllers
    AC_AttitudeControl *attitude_control;
    AC_PosControl *pos_control;
    AC_WPNav *wp_nav;
    AC_Loiter *loiter_nav;
    AC_Circle *circle_nav;

    // Current mode
    Mode *flightmode;

    // State flags
    struct {
        bool land_complete;
        bool land_complete_maybe;
        bool throttle_zero;
        bool auto_armed;
        bool motor_interlock_switch;
        // ...
    } ap;

    // Parameters
    Parameters g;
    ParametersG2 g2;
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
        LOITER = 5,
        RTL = 6,
        CIRCLE = 7,
        LAND = 9,
        // ... more modes
    };

    // Virtual methods all modes must implement
    virtual Number mode_number() const = 0;
    virtual bool init(bool ignore_checks) { return true; }
    virtual void exit() {}
    virtual void run() = 0;
    virtual bool requires_GPS() const = 0;
    virtual bool has_manual_throttle() const = 0;
    virtual bool allows_arming(AP_Arming::Method method) const = 0;
    virtual bool is_autopilot() const = 0;

    // Optional overrides
    virtual bool has_user_takeoff(bool must_navigate) const { return false; }
    virtual bool in_guided_mode() const { return false; }
    virtual bool allows_flip() const { return false; }
    virtual bool crash_check_enabled() const { return true; }

protected:
    // Shared resources
    Parameters &g;
    ParametersG2 &g2;
    AC_WPNav *&wp_nav;
    AC_Loiter *&loiter_nav;
    AC_PosControl *&pos_control;
    AP_AHRS &ahrs;
    AC_AttitudeControl *&attitude_control;
    MOTOR_CLASS *&motors;
    RC_Channel *&channel_roll;
    RC_Channel *&channel_pitch;
    RC_Channel *&channel_throttle;
    RC_Channel *&channel_yaw;
};
```

## Scheduler

Fast loop runs at 400Hz (or higher with fast rate loop):

```cpp
const AP_Scheduler::Task Copter::scheduler_tasks[] = {
    // Fast tasks (every loop)
    FAST_TASK_CLASS(AP_InertialSensor, &copter.ins, update),
    FAST_TASK(run_rate_controller_main),
    FAST_TASK(motors_output_main),
    FAST_TASK(read_AHRS),
    FAST_TASK(read_inertia),
    FAST_TASK(check_ekf_reset),
    FAST_TASK(update_flight_mode),
    FAST_TASK(update_home_from_EKF),
    FAST_TASK(update_land_and_crash_detectors),

    // Scheduled tasks
    SCHED_TASK(rc_loop, 100, 130, 3),
    SCHED_TASK(throttle_loop, 50, 75, 6),
    SCHED_TASK(update_GPS, 50, 200, 9),
    SCHED_TASK(update_batt_compass, 10, 120, 12),
    SCHED_TASK(read_rangefinder, 20, 100, 15),
    SCHED_TASK(update_altitude, 10, 100, 18),
    // ...
};
```

## Control Flow

### Main Loop

```
1. INS Update (read sensors)
2. Rate Controller (attitude rates)
3. Motor Output (PWM)
4. AHRS Update (attitude estimation)
5. Inertia Update (position estimation)
6. EKF Reset Check
7. Flight Mode Update (mode-specific logic)
8. Land/Crash Detection
```

### Mode Execution

```cpp
void Copter::update_flight_mode()
{
    flightmode->run();
}
```

Each mode's `run()` method typically:
1. Applies simple mode transform
2. Gets pilot inputs
3. Runs position/attitude control
4. Sets motor outputs

## State Management

### Arming

```cpp
motors->armed()  // Check if armed
arming.arm(method)  // Arm motors
arming.disarm(method)  // Disarm motors
```

### Landing Detection

```cpp
ap.land_complete  // True if definitely landed
ap.land_complete_maybe  // True if probably landed
ap.throttle_zero  // Throttle stick at zero
```

### Failsafe

```cpp
struct {
    uint8_t radio : 1;
    uint8_t gcs : 1;
    uint8_t ekf : 1;
    uint8_t terrain : 1;
    uint8_t adsb : 1;
    uint8_t deadreckon : 1;
} failsafe;
```

## Frame Types

Configured at compile time:

```cpp
#if FRAME_CONFIG == HELI_FRAME
    #define MOTOR_CLASS AP_MotorsHeli
#else
    #define MOTOR_CLASS AP_MotorsMulticopter
#endif
```

## Memory Layout

Parameters stored in two groups:
- `g` (Parameters): Primary parameters
- `g2` (ParametersG2): Extended parameters

```cpp
float angle_max = g.angle_max.get();
float speed = g.pilot_speed_up_cms.get();
```

## File Organization

```
ArduCopter/
├── Copter.h/cpp              # Main class
├── mode.h                    # All mode definitions
├── mode_*.cpp                # Mode implementations
├── Parameters.h/cpp          # Parameter system
├── Attitude.cpp              # Attitude helpers
├── autoyaw.cpp               # Auto yaw control
├── crash_check.cpp           # Crash detection
├── ekf_check.cpp             # EKF failsafe
├── events.cpp                # Failsafe events
├── failsafe.cpp              # Failsafe enable/disable
├── land_detector.cpp         # Landing detection
├── heli.cpp                  # Helicopter support
├── GCS_MAVLink_Copter.cpp    # MAVLink handling
└── defines.h                 # Constants
```
