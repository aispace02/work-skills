# Rover Architecture

## Class Hierarchy

```
AP_Vehicle (base)
    └── Rover (main vehicle class)
            ├── control_mode (Mode* - current active mode)
            ├── Parameters g (vehicle parameters)
            ├── ParametersG2 g2 (extended parameters + subsystems)
            │       ├── AP_MotorsUGV motors
            │       ├── AR_AttitudeControl attitude_control
            │       ├── AR_WPNav_OA wp_nav
            │       ├── AR_PosControl pos_control
            │       ├── AP_SmartRTL smart_rtl
            │       ├── Sailboat sailboat
            │       └── RC_Channels_Rover rc_channels
            └── Mode instances (mode_manual, mode_auto, etc.)
```

## Main Files

| File | Purpose |
|------|---------|
| `Rover.h` | Main class declaration, scheduler tasks |
| `Rover.cpp` | Scheduler task table, core methods |
| `system.cpp` | Initialization, mode switching, AHRS updates |
| `defines.h` | Constants, enums, limits |

## Rover Class Key Members

```cpp
class Rover : public AP_Vehicle {
public:
    // Singleton access
    static Rover *get_singleton() { return _singleton; }

    // Core state
    Mode *control_mode;              // Current active mode
    Parameters g;                     // Group 1 parameters
    ParametersG2 g2;                  // Group 2 (extended)

    // Timing
    float G_Dt;                       // Main loop delta time

    // Status
    struct {
        bool initialised;
        bool active;
        bool triggered;
        uint32_t triggered_timer;
    } failsafe;

    // Position
    Location current_loc;             // Current position
    Location home;                    // Home position

    // Mode instances
    ModeInitializing mode_initializing;
    ModeManual mode_manual;
    ModeAuto mode_auto;
    ModeGuided mode_guided;
    ModeRTL mode_rtl;
    ModeSmartRTL mode_smart_rtl;
    // ... all other modes

    // Key methods
    bool set_mode(Mode::Number mode, ModeReason reason);
    void update_current_mode();
    void set_servos();
};
```

## Initialization Sequence

```cpp
// 1. HAL startup (hardware abstraction layer)
AP_HAL::Scheduler::system_initialized();

// 2. Parameter load
AP_Param::setup();
AP_Param::load_all();

// 3. init_ardupilot() - Main initialization
void Rover::init_ardupilot() {
    // Board-specific init
    BoardConfig.init();

    // Sensors
    ins.init(scheduler.get_loop_rate_hz());
    compass.init();
    barometer.init();
    gps.init();

    // RC channels
    g2.rc_channels.init();

    // Motors (based on FRAME_TYPE)
    g2.motors.init(get_frame_type());

    // Navigation
    g2.wp_nav.init();

    // Sailboat (if boat)
    g2.sailboat.init();

    // Set initial mode
    set_mode(Mode::Number::INITIALISING, ModeReason::INITIALISED);
}

// 4. startup_INS() - Calibration
void Rover::startup_INS() {
    ahrs.init();
    ahrs.set_vehicle_class(AHRS_VEHICLE_GROUND);
    ins.wait_for_startup();
}

// 5. Mode transition to operational mode
set_mode((Mode::Number)g.initial_mode.get(), ModeReason::INITIALISED);
```

## Main Loop (400Hz)

```cpp
// Scheduler task table (Rover.cpp)
const AP_Scheduler::Task Rover::scheduler_tasks[] = {
    // Function                 Rate(Hz)  MaxTime  Priority
    SCHED_TASK(read_radio,           50,    200,      3),
    SCHED_TASK(ahrs_update,         400,    400,      6),
    SCHED_TASK(read_rangefinders,    50,    200,      9),
    SCHED_TASK(update_current_mode, 400,    200,     12),
    SCHED_TASK(set_servos,          400,    200,     15),
    SCHED_TASK_CLASS(AP_GPS, &gps, update, 50, 300, 18),
    SCHED_TASK_CLASS(AP_Baro, &barometer, update, 10, 200, 21),
    // ... more tasks
    SCHED_TASK(one_second_loop,       1,   1500,     96),
};

// Main update flow
void Rover::loop() {
    // Called by AP_Scheduler at 400Hz

    // 1. Read sensors
    read_radio();          // RC input
    ahrs_update();         // Position/heading

    // 2. Run current mode
    update_current_mode(); // Calls control_mode->update()

    // 3. Output to motors
    set_servos();          // Motor commands

    // 4. Monitoring (lower rate)
    failsafe_check();
    ekf_check();
}
```

## Mode Switching

```cpp
bool Rover::set_mode(Mode::Number mode, ModeReason reason) {
    // Get mode pointer
    Mode *new_mode = mode_from_mode_num(mode);
    if (new_mode == nullptr) {
        return false;
    }

    // Check if mode can be entered
    if (!new_mode->enter()) {
        return false;
    }

    // Exit old mode
    if (control_mode != nullptr) {
        control_mode->exit();
    }

    // Switch
    control_mode = new_mode;

    // Log and notify
    logger.Write_Mode(mode, reason);
    notify_mode(control_mode);

    return true;
}

Mode* Rover::mode_from_mode_num(Mode::Number mode) {
    switch (mode) {
        case Mode::Number::MANUAL: return &mode_manual;
        case Mode::Number::AUTO: return &mode_auto;
        case Mode::Number::GUIDED: return &mode_guided;
        case Mode::Number::RTL: return &mode_rtl;
        case Mode::Number::SMART_RTL: return &mode_smart_rtl;
        case Mode::Number::HOLD: return &mode_hold;
        case Mode::Number::LOITER: return &mode_loiter;
        case Mode::Number::STEERING: return &mode_steering;
        case Mode::Number::ACRO: return &mode_acro;
        case Mode::Number::CIRCLE: return &mode_circle;
        case Mode::Number::FOLLOW: return &mode_follow;
        case Mode::Number::SIMPLE: return &mode_simple;
        case Mode::Number::DOCK: return &mode_dock;
        case Mode::Number::INITIALISING: return &mode_initializing;
        default: return nullptr;
    }
}
```

## Global Access Patterns

```cpp
// Singleton access
Rover &rover = AP::rover();      // From anywhere
Rover *rover = Rover::get_singleton();

// From Mode classes (already have reference)
void ModeAuto::update() {
    rover.current_loc;           // Current position
    rover.home;                  // Home location
    rover.G_Dt;                  // Delta time
    g;                           // Parameters (shorthand)
    g2;                          // Extended parameters
    g2.motors;                   // Motor control
    g2.wp_nav;                   // Navigation
}

// Parameters
rover.g.speed_cruise;            // Cruise speed
rover.g2.turn_radius;            // Turn radius
rover.g.fs_action;               // Failsafe action
```

## Timing

```cpp
// Main loop timing
rover.G_Dt;                      // Delta time (seconds)
rover.scheduler.get_loop_rate_hz();  // Loop rate (400Hz)

// Timestamps
AP_HAL::millis();                // Milliseconds since boot
AP_HAL::micros();                // Microseconds since boot

// Timeouts (common pattern)
uint32_t last_update_ms;
if (AP_HAL::millis() - last_update_ms > TIMEOUT_MS) {
    // Timeout occurred
}
```

## Friend Classes

The Rover class declares many friends for access to private members:

```cpp
class Rover {
    friend class GCS_MAVLINK_Rover;
    friend class GCS_Rover;
    friend class Mode;
    friend class ModeAuto;
    friend class ModeGuided;
    // ... all mode classes
    friend class AP_Arming_Rover;
    friend class RC_Channel_Rover;
    friend class RC_Channels_Rover;
    friend class Sailboat;
};
```
