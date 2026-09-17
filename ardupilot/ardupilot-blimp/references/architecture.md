# Blimp Architecture

## System Overview

Blimp is built on the ArduPilot framework, inheriting from `AP_Vehicle` and providing lighter-than-air vehicle-specific functionality with oscillating fin control.

## Class Hierarchy

```
AP_Vehicle
    └── Blimp
            ├── Mode (base class)
            │   ├── ModeLand
            │   ├── ModeManual
            │   ├── ModeVelocity
            │   ├── ModeLoiter
            │   └── ModeRTL
            │
            ├── Fins (motors)
            ├── Loiter (position/velocity controller)
            ├── AC_PID_2D (pid_vel_xy, pid_pos_xy)
            ├── AC_PID_Basic (pid_vel_z, pid_vel_yaw, pid_pos_z)
            └── AC_PID (pid_pos_yaw)
```

## Main Components

### Blimp Class (Blimp.h)

The main vehicle class:

```cpp
class Blimp : public AP_Vehicle {
    // Motor Output (oscillating fins)
    Fins *motors;
    Loiter *loiter;

    // Primary input channels
    RC_Channel *channel_right;
    RC_Channel *channel_front;
    RC_Channel *channel_up;
    RC_Channel *channel_yaw;

    // Velocity & Position PIDs
    AC_PID_2D pid_vel_xy;
    AC_PID_Basic pid_vel_z;
    AC_PID_Basic pid_vel_yaw;
    AC_PID_2D pid_pos_xy;
    AC_PID_Basic pid_pos_z;
    AC_PID pid_pos_yaw;

    // State
    Vector3f vel_ned;
    Vector3f vel_ned_filtd;
    Vector3f pos_ned;
    float vel_yaw;
    float vel_yaw_filtd;

    // Current mode
    Mode *flightmode;
    Mode::Number control_mode;

    // State flags
    ap_t ap;  // land_complete, throttle_zero, etc.

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
        LAND = 0,
        MANUAL = 1,
        VELOCITY = 2,
        LOITER = 3,
        RTL = 4,
    };

    virtual bool init(bool ignore_checks) { return true; }
    virtual void run() = 0;
    virtual bool requires_GPS() const = 0;
    virtual bool has_manual_throttle() const = 0;
    virtual bool allows_arming(bool from_gcs) const = 0;
    virtual bool is_autopilot() const { return false; }

protected:
    // Shared resources
    Parameters &g;
    ParametersG2 &g2;
    AP_InertialNav &inertial_nav;
    AP_AHRS &ahrs;
    Fins *&motors;
    Loiter *&loiter;
    RC_Channel *&channel_right;
    RC_Channel *&channel_front;
    RC_Channel *&channel_up;
    RC_Channel *&channel_yaw;
    float &G_Dt;
};
```

## Scheduler

Main loop runs at variable rate with these tasks:

```cpp
const AP_Scheduler::Task Blimp::scheduler_tasks[] = {
    // Fast tasks (every loop)
    FAST_TASK_CLASS(AP_InertialSensor, &blimp.ins, update),
    FAST_TASK(motors_output),
    FAST_TASK(read_AHRS),
    FAST_TASK(read_inertia),
    FAST_TASK(check_ekf_reset),
    FAST_TASK(update_flight_mode),
    FAST_TASK(update_home_from_EKF),

    // Scheduled tasks
    SCHED_TASK(rc_loop, 100, 130, 3),
    SCHED_TASK(throttle_loop, 50, 75, 6),
    SCHED_TASK_CLASS(AP_GPS, &blimp.gps, update, 50, 200, 9),
    SCHED_TASK(update_batt_compass, 10, 120, 12),
    SCHED_TASK(update_altitude, 10, 100, 21),
    SCHED_TASK(three_hz_loop, 3, 75, 24),
    SCHED_TASK(one_hz_loop, 1, 100, 39),
    SCHED_TASK(ekf_check, 10, 75, 42),
    // ...
};
```

## Control Flow

### Main Loop

```
1. INS Update (read sensors)
2. Motors Output (fin PWM)
3. AHRS Update (attitude estimation)
4. Inertia Update (position/velocity)
5. EKF Reset Check
6. Flight Mode Update (mode-specific logic)
7. Home Update
```

### Mode Execution

```cpp
void Blimp::update_flight_mode() {
    flightmode->run();
}
```

Each mode's `run()` method:
1. Gets pilot input
2. Transforms input (simple mode)
3. Updates position/velocity targets
4. Calls loiter controller
5. Fin outputs are set by loiter

## State Management

### Arming

```cpp
motors->armed()  // Check if armed
motors->armed(true)  // Arm fins
motors->armed(false) // Disarm fins
```

### State Flags (ap_t)

```cpp
struct {
    uint8_t pre_arm_rc_check : 1;
    uint8_t pre_arm_check : 1;
    uint8_t auto_armed : 1;
    uint8_t logging_started : 1;
    uint8_t land_complete : 1;
    uint8_t new_radio_frame : 1;
    uint8_t compass_mot : 1;
    uint8_t motor_test : 1;
    uint8_t initialised : 1;
    uint8_t land_complete_maybe : 1;
    uint8_t throttle_zero : 1;
    uint8_t gps_glitching : 1;
    uint8_t in_arming_delay : 1;
    uint8_t initialised_params : 1;
} ap;
```

### Failsafe

```cpp
struct {
    int8_t radio_counter;
    uint8_t radio : 1;
    uint8_t gcs : 1;
    uint8_t ekf : 1;
} failsafe;
```

## Navigation State

### Position/Velocity

```cpp
Vector3f pos_ned;       // Position in NED frame (m)
Vector3f vel_ned;       // Velocity in NED frame (m/s)
Vector3f vel_ned_filtd; // Filtered velocity
float vel_yaw;          // Yaw rate (rad/s)
float vel_yaw_filtd;    // Filtered yaw rate
```

### Coordinate Transform

```cpp
// Rotate from North-East to Body-Frame
void rotate_NE_to_BF(Vector2f &vec);

// Rotate from Body-Frame to North-East
void rotate_BF_to_NE(Vector2f &vec);
```

## File Organization

```
Blimp/
├── Blimp.h/cpp           # Main class
├── mode.h                # All mode definitions
├── mode_*.cpp            # Mode implementations
├── Fins.h/cpp            # Fin oscillation control
├── Loiter.h/cpp          # Position/velocity control
├── Parameters.h/cpp      # Parameter system
├── events.cpp            # Failsafe events
├── failsafe.cpp          # Failsafe enable/disable
├── ekf_check.cpp         # EKF checking
├── radio.cpp             # RC input
├── GCS_MAVLink_Blimp.cpp # MAVLink handling
└── defines.h             # Constants
```
