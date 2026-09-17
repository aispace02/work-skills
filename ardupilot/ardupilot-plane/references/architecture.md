# Plane Architecture

## Class Hierarchy

```
AP_Vehicle (base)
    └── Plane (main vehicle class)
            ├── control_mode (Mode* - current active mode)
            ├── Parameters g (vehicle parameters)
            ├── ParametersG2 g2 (extended parameters)
            ├── TECS_controller (altitude/speed control)
            ├── L1_controller (lateral navigation)
            ├── rollController, pitchController, yawController
            ├── QuadPlane quadplane (VTOL support)
            └── Mode instances (mode_manual, mode_auto, etc.)
```

## Main Files

| File | Purpose |
|------|---------|
| `Plane.h` | Main class declaration |
| `Plane.cpp` | Scheduler tasks, main methods |
| `Attitude.cpp` | Attitude stabilization |
| `altitude.cpp` | Altitude/speed control via TECS |
| `commands_logic.cpp` | Mission command handlers |
| `control_modes.cpp` | Mode switching |
| `defines.h` | Constants, enums |

## Plane Class Key Members

```cpp
class Plane : public AP_Vehicle {
public:
    static Plane *get_singleton() { return _singleton; }

private:
    // Parameters
    Parameters g;
    ParametersG2 g2;

    // Controllers
    AP_TECS TECS_controller;           // Speed/height
    AP_L1_Control L1_controller;       // Navigation
    AP_RollController rollController;
    AP_PitchController pitchController;
    AP_YawController yawController;

    // Current mode
    Mode *control_mode;
    Mode *previous_mode;

    // Mode instances
    ModeManual mode_manual;
    ModeFBWA mode_fbwa;
    ModeFBWB mode_fbwb;
    ModeCruise mode_cruise;
    ModeAuto mode_auto;
    ModeRTL mode_rtl;
    ModeLoiter mode_loiter;
    ModeGuided mode_guided;
    // ... all other modes

    // QuadPlane support
    QuadPlane quadplane;

    // Navigation
    AP_Navigation *nav_controller;     // Points to L1_controller

    // State
    Location current_loc;
    Location home;
    Location prev_WP_loc, next_WP_loc;

    // Airspeed
    float target_airspeed_cm;
    float airspeed_error;

    // Altitude
    float target_altitude_amsl_cm;
    float altitude_error_cm;
};
```

## Initialization Sequence

```cpp
// 1. HAL startup
AP_HAL::Scheduler::system_initialized();

// 2. Parameter load
AP_Param::setup();
AP_Param::load_all();

// 3. init_ardupilot() - Main initialization
void Plane::init_ardupilot() {
    // Sensors
    ins.init(scheduler.get_loop_rate_hz());
    ahrs.init();
    compass.init();
    barometer.init();
    gps.init();

    // Airspeed
    airspeed.init();

    // RC channels
    g2.rc_channels.init();

    // Navigation
    nav_controller = &L1_controller;

    // TECS
    TECS_controller.init();

    // QuadPlane (if enabled)
    quadplane.init();

    // Set initial mode
    set_mode(mode_initializing, ModeReason::INITIALISED);
}
```

## Main Loop (400Hz)

```cpp
// From Plane.cpp scheduler_tasks[]
const AP_Scheduler::Task Plane::scheduler_tasks[] = {
    // Task                           Rate   MaxTime  Priority
    SCHED_TASK(read_radio,             50,    100,     6),
    SCHED_TASK(update_speed_height,    50,    200,    12),
    SCHED_TASK(update_GPS_50Hz,        50,    300,    30),
    SCHED_TASK(navigate,               10,    150,    36),
    SCHED_TASK(update_compass,         10,    200,    39),
    SCHED_TASK(calc_airspeed_errors,   10,    100,    42),
    SCHED_TASK(update_alt,             10,    200,    45),
    SCHED_TASK(one_second_loop,         1,    400,    90),
    // ... more tasks
};

// Main flight loop in Plane::update_flight_mode()
void Plane::update_flight_mode() {
    // Run current mode's update
    control_mode->update();

    // Run current mode's run (attitude control)
    control_mode->run();
}
```

## Control Flow

```
Main Loop (400Hz)
    │
    ├─► read_radio() - Get RC input
    │
    ├─► update_speed_height() - Run TECS
    │       └─► TECS_controller.update_pitch_throttle()
    │
    ├─► navigate() - Run L1 navigation
    │       └─► control_mode->navigate()
    │           └─► nav_controller->update_waypoint()
    │
    └─► update_flight_mode()
            ├─► control_mode->update() - Mode-specific logic
            └─► control_mode->run() - Attitude stabilization
                    ├─► stabilize_roll()
                    ├─► stabilize_pitch()
                    └─► stabilize_yaw()
```

## Mode Switching

```cpp
bool Plane::set_mode(Mode &new_mode, ModeReason reason) {
    // Check if mode can be entered
    if (!new_mode.enter()) {
        return false;
    }

    // Exit current mode
    if (control_mode != nullptr) {
        control_mode->exit();
    }

    // Switch
    previous_mode = control_mode;
    control_mode = &new_mode;
    last_mode_change_ms = AP_HAL::millis();

    // Log and notify
    logger.Write_Mode(control_mode->mode_number(), reason);
    gcs().send_message(MSG_HEARTBEAT);

    return true;
}
```

## Key State Variables

```cpp
// Navigation
struct {
    uint32_t last_valid_rc_ms;
    bool rc_failsafe;
    int16_t state;          // FAILSAFE_NONE, FAILSAFE_SHORT, FAILSAFE_LONG
} failsafe;

// Flight state
struct {
    float commanded_roll;
    float commanded_pitch;
    float commanded_throttle;
} nav_scripting;

// Takeoff state
struct {
    bool complete;
    uint32_t start_time_ms;
    float target_ground_speed;
} takeoff_state;

// Landing state
bool landing_complete;
float auto_state.land_sink_rate;
```

## Servo Functions

| Function | Channel | Description |
|----------|---------|-------------|
| k_aileron | 4 | Roll control |
| k_elevator | 19 | Pitch control |
| k_throttle | 70 | Throttle |
| k_rudder | 21 | Yaw control |
| k_flap | 2 | Flaps |
| k_aileron_with_input | 18 | Aileron + RC |
| k_flaperon_left | 24 | Left flaperon |
| k_flaperon_right | 25 | Right flaperon |
