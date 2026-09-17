# Extending ArduPlane

Guide to adding new functionality to ArduPilot Plane.

## Adding a New Flight Mode

### Step 1: Define Mode Class

Add to `ArduPlane/mode.h`:

```cpp
class ModeCustom : public Mode {
public:
    Number mode_number() const override { return Number::CUSTOM; }
    const char *name() const override { return "CUSTOM"; }
    const char *name4() const override { return "CUST"; }

    // Control methods
    void update() override;
    void run() override;

    // Mode properties
    bool does_auto_navigation() const override { return false; }
    bool does_auto_throttle() const override { return false; }
    bool allows_throttle_nudging() const override { return false; }

protected:
    bool _enter() override;
    void _exit() override;

private:
    // Mode-specific state
    uint32_t enter_time_ms;
};
```

### Step 2: Add Mode Number

In `mode.h` enum (if new number needed):

```cpp
enum Number : uint8_t {
    // ... existing modes
    CUSTOM = 27,  // Pick unused number
};
```

### Step 3: Implement Mode

Create `ArduPlane/mode_custom.cpp`:

```cpp
#include "Plane.h"

bool ModeCustom::_enter() {
    // Initialize mode state
    enter_time_ms = AP_HAL::millis();

    // Setup controllers
    plane.TECS_controller.reset_controller();

    return true;
}

void ModeCustom::_exit() {
    // Cleanup if needed
}

void ModeCustom::update() {
    // Mode-specific logic runs here
    // This is called before attitude stabilization

    // Example: hold current heading and altitude
    plane.nav_roll_cd = 0;  // Wings level
    plane.nav_pitch_cd = plane.TECS_controller.get_pitch_demand();
}

void ModeCustom::run() {
    // Attitude stabilization runs here
    // This is called after update()

    plane.stabilize_roll();
    plane.stabilize_pitch();
    plane.stabilize_yaw();

    // Handle throttle
    if (does_auto_throttle()) {
        // TECS handles throttle
    } else {
        output_pilot_throttle();
    }
}
```

### Step 4: Add Mode Instance

In `Plane.h`:

```cpp
class Plane : public AP_Vehicle {
    // ... existing members
    ModeCustom mode_custom;
};
```

### Step 5: Register Mode

In `ArduPlane/control_modes.cpp`:

```cpp
Mode *Plane::mode_from_mode_num(Mode::Number mode) {
    switch (mode) {
        // ... existing cases
        case Mode::Number::CUSTOM:
            return &mode_custom;
    }
}
```

---

## Adding a New Parameter

### Simple Parameter

```cpp
// 1. In Parameters.h
class Parameters {
    AP_Float my_custom_gain;
};

// 2. In Parameters.cpp
const AP_Param::Info Parameters::var_info[] = {
    // ... existing

    // @Param: MY_GAIN
    // @DisplayName: My Custom Gain
    // @Description: Gain for my custom feature
    // @Range: 0 10
    // @User: Advanced
    GSCALAR(my_custom_gain, "MY_GAIN", 1.0f),

    // ...
};

// 3. Usage
float gain = g.my_custom_gain.get();
```

### Mode-Specific Parameters

```cpp
// In mode.h class definition
class ModeTakeoff : public Mode {
    // Mode parameters embedded in mode
    static const struct AP_Param::GroupInfo var_info[];

    AP_Int16 target_alt;
    AP_Float ground_pitch;
};

// In mode_takeoff.cpp
const AP_Param::GroupInfo ModeTakeoff::var_info[] = {
    // @Param: TKOFF_ALT
    // @DisplayName: Takeoff altitude
    // @Description: Target altitude for takeoff mode
    // @Units: m
    // @Range: 10 1000
    AP_GROUPINFO("ALT", 1, ModeTakeoff, target_alt, 50),

    // @Param: TKOFF_GND_PITCH
    // @DisplayName: Ground pitch
    // @Description: Pitch angle on ground during takeoff
    // @Units: deg
    // @Range: -10 30
    AP_GROUPINFO("GND_PITCH", 2, ModeTakeoff, ground_pitch, 5.0f),

    AP_GROUPEND
};
```

---

## Adding a Mission Command

### Navigation Command

In `ArduPlane/commands_logic.cpp`:

```cpp
// 1. Add to start_command()
bool Plane::start_command(const AP_Mission::Mission_Command& cmd) {
    switch (cmd.id) {
        // ... existing cases

        case MAV_CMD_NAV_CUSTOM:
            return do_nav_custom(cmd);
    }
}

// 2. Implement handler
bool Plane::do_nav_custom(const AP_Mission::Mission_Command& cmd) {
    // Extract parameters
    Location target = cmd.content.location;
    float param1 = cmd.p1;

    // Setup navigation
    prev_WP_loc = current_loc;
    next_WP_loc = target;

    return true;
}

// 3. Add verify function
bool Plane::verify_nav_custom(const AP_Mission::Mission_Command& cmd) {
    // Check completion
    return nav_controller->reached_waypoint();
}

// 4. Add to verify_command()
bool Plane::verify_command(const AP_Mission::Mission_Command& cmd) {
    switch (cmd.id) {
        case MAV_CMD_NAV_CUSTOM:
            return verify_nav_custom(cmd);
    }
}
```

### DO Command

```cpp
bool Plane::start_command(const AP_Mission::Mission_Command& cmd) {
    switch (cmd.id) {
        case MAV_CMD_DO_CUSTOM:
            return do_custom_action(cmd);
    }
}

bool Plane::do_custom_action(const AP_Mission::Mission_Command& cmd) {
    // Execute immediate action
    // DO commands complete immediately
    return true;
}
```

---

## Adding a Scheduler Task

In `ArduPlane/Plane.cpp`:

```cpp
// 1. Add task declaration (if new function)
void Plane::my_custom_task();

// 2. Add to scheduler table
const AP_Scheduler::Task Plane::scheduler_tasks[] = {
    // ... existing tasks

    // Function, Rate(Hz), MaxTime(us), Priority
    SCHED_TASK(my_custom_task, 10, 100, 200),
};

// 3. Implement
void Plane::my_custom_task() {
    // Runs at 10Hz
    // Keep execution under 100us typically
}
```

---

## Adding MAVLink Handler

In `ArduPlane/GCS_MAVLink_Plane.cpp`:

```cpp
void GCS_MAVLINK_Plane::handle_message(const mavlink_message_t &msg) {
    switch (msg.msgid) {
        // ... existing handlers

        case MAVLINK_MSG_ID_CUSTOM:
            handle_custom_message(msg);
            break;
    }

    // Call parent
    GCS_MAVLINK::handle_message(msg);
}

void GCS_MAVLINK_Plane::handle_custom_message(const mavlink_message_t &msg) {
    mavlink_custom_t packet;
    mavlink_msg_custom_decode(&msg, &packet);

    // Process
    plane.handle_custom_data(packet.field1, packet.field2);
}
```

---

## Adding a Log Message

In `ArduPlane/Log.cpp`:

```cpp
// 1. Define structure
struct PACKED log_Custom {
    LOG_PACKET_HEADER;
    uint64_t time_us;
    float value1;
    float value2;
    int16_t state;
};

// 2. Add to log formats
{ LOG_CUSTOM_MSG, sizeof(log_Custom),
    "CUST", "Qffh", "TimeUS,V1,V2,Sta", "s---", "F---" },

// 3. Write function
void Plane::Log_Write_Custom() {
    struct log_Custom pkt = {
        LOG_PACKET_HEADER_INIT(LOG_CUSTOM_MSG),
        time_us : AP_HAL::micros64(),
        value1  : custom_value1,
        value2  : custom_value2,
        state   : custom_state
    };
    logger.WriteBlock(&pkt, sizeof(pkt));
}
```

---

## Testing in SITL

```bash
# Build for SITL
./waf configure --board sitl
./waf plane

# Run simulation
cd Tools/autotest
./sim_vehicle.py -v ArduPlane -f plane --console --map

# Fly missions
./sim_vehicle.py -v ArduPlane --map --console -L CMAC
```

---

## Best Practices

1. **Mode design**: Keep `update()` for navigation, `run()` for attitude
2. **Parameter naming**: Use consistent prefixes
3. **Logging**: Log enough data for post-flight analysis
4. **Safety**: Always consider failsafe implications
5. **Testing**: Test in SITL before real hardware
6. **Code style**: Follow ArduPilot coding standards
