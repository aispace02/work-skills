# Extending Rover

Guide to adding new functionality to ArduPilot Rover.

## Adding a New Flight Mode

### Step 1: Define Mode Class

Add to `Rover/mode.h`:

```cpp
class ModeCustom : public Mode {
public:
    // Required overrides
    Number mode_number() const override { return Number::CUSTOM; }
    const char *name4() const override { return "CUST"; }
    void update() override;

    // Mode attributes
    bool is_autopilot_mode() const override { return true; }
    bool requires_position() const override { return true; }
    bool allows_arming() const override { return true; }

    // Optional: Navigation interface
    bool set_desired_location(const Location &loc) override;
    bool reached_destination() const override;
    float get_distance_to_destination() const override;

protected:
    bool _enter() override;
    void _exit() override;

private:
    // Mode-specific state
    Location _destination;
    bool _destination_valid;
};
```

### Step 2: Add Mode Number

In `Rover/mode.h` enum:

```cpp
enum class Number : uint8_t {
    // ... existing modes
    CUSTOM = 17,  // Pick unused number
};
```

### Step 3: Implement Mode

Create `Rover/mode_custom.cpp`:

```cpp
#include "Rover.h"

bool ModeCustom::_enter() {
    // Initialize mode state
    _destination_valid = false;

    // Check preconditions
    if (!rover.ahrs.get_position(_destination)) {
        return false;  // Can't enter without position
    }

    return true;
}

void ModeCustom::_exit() {
    // Cleanup
    _destination_valid = false;
}

void ModeCustom::update() {
    if (!_destination_valid) {
        stop_vehicle();
        return;
    }

    // Navigate to destination
    navigate_to_waypoint();

    // Check for completion
    if (reached_destination()) {
        // Do something when arrived
    }
}

bool ModeCustom::set_desired_location(const Location &loc) {
    _destination = loc;
    _destination_valid = true;

    // Initialize navigation
    g2.wp_nav.set_desired_location(loc);
    return true;
}

bool ModeCustom::reached_destination() const {
    if (!_destination_valid) {
        return true;
    }
    return g2.wp_nav.reached_destination();
}

float ModeCustom::get_distance_to_destination() const {
    if (!_destination_valid) {
        return 0;
    }
    return g2.wp_nav.get_distance_to_destination();
}
```

### Step 4: Register Mode

In `Rover.h`, add instance:

```cpp
class Rover : public AP_Vehicle {
    // ... existing modes
    ModeCustom mode_custom;
};
```

In `Rover/system.cpp`, add to `mode_from_mode_num()`:

```cpp
Mode* Rover::mode_from_mode_num(Mode::Number mode) {
    switch (mode) {
        // ... existing cases
        case Mode::Number::CUSTOM:
            return &mode_custom;
    }
}
```

### Step 5: Add to Build

In `Rover/wscript` or just ensure file is in Rover directory (automatically included).

---

## Adding a New Parameter

### Simple Vehicle Parameter

In `Rover/Parameters.h`:

```cpp
class Parameters {
    // ... existing
    AP_Float my_speed_limit;
};
```

In `Rover/Parameters.cpp`:

```cpp
const AP_Param::Info Parameters::var_info[] = {
    // ... existing

    // @Param: MY_SPEED_LIM
    // @DisplayName: My Speed Limit
    // @Description: Custom speed limit for my feature
    // @Units: m/s
    // @Range: 0 50
    // @User: Standard
    GSCALAR(my_speed_limit, "MY_SPEED_LIM", 10.0f),

    // ...
};
```

Usage:

```cpp
float limit = g.my_speed_limit.get();
```

### Group 2 Parameter

In `Rover/Parameters.h`:

```cpp
class ParametersG2 {
    // ... existing
    AP_Int8 my_enable;
};
```

In `Rover/Parameters.cpp`:

```cpp
const AP_Param::GroupInfo ParametersG2::var_info[] = {
    // ... existing

    // @Param: MY_ENABLE
    // @DisplayName: My Feature Enable
    // @Description: Enable my custom feature
    // @Values: 0:Disabled,1:Enabled
    // @User: Standard
    AP_GROUPINFO("MY_ENABLE", XX, ParametersG2, my_enable, 0),

    // ...
};
```

Usage:

```cpp
if (g2.my_enable.get() > 0) {
    // Feature enabled
}
```

---

## Adding a New Scheduler Task

In `Rover/Rover.cpp`:

```cpp
// Add task function declaration
void Rover::my_custom_task();

// Add to scheduler table
const AP_Scheduler::Task Rover::scheduler_tasks[] = {
    // ... existing tasks

    // Function, Rate(Hz), MaxTime(us), Priority
    SCHED_TASK(my_custom_task, 10, 200, 150),

    // ...
};
```

Implement in `Rover/Rover.cpp` or separate file:

```cpp
void Rover::my_custom_task() {
    // Called at 10Hz
    // Keep execution time under 200us typically
}
```

---

## Adding a Mission Command

### Navigation Command

In `Rover/mode_auto.cpp`, add to `start_command()`:

```cpp
bool ModeAuto::start_command(const AP_Mission::Mission_Command& cmd) {
    switch (cmd.id) {
        // ... existing cases

        case MAV_CMD_NAV_MY_CUSTOM:
            return do_nav_my_custom(cmd);
    }
}
```

Implement handler:

```cpp
bool ModeAuto::do_nav_my_custom(const AP_Mission::Mission_Command& cmd) {
    // Extract parameters
    float param1 = cmd.content.location.lat;  // Use appropriate field

    // Setup navigation
    Location target = cmd.content.location;
    if (!set_desired_location(target)) {
        return false;
    }

    // Set submode
    _submode = SubMode::WP;
    return true;
}
```

Add to `verify_command()`:

```cpp
bool ModeAuto::verify_command(const AP_Mission::Mission_Command& cmd) {
    switch (cmd.id) {
        // ... existing cases

        case MAV_CMD_NAV_MY_CUSTOM:
            return verify_nav_my_custom();
    }
}

bool ModeAuto::verify_nav_my_custom() {
    return reached_destination();
}
```

---

## Adding a MAVLink Handler

In `Rover/GCS_MAVLink_Rover.cpp`:

```cpp
void GCS_MAVLINK_Rover::handle_message(const mavlink_message_t &msg) {
    switch (msg.msgid) {
        // ... existing cases

        case MAVLINK_MSG_ID_MY_CUSTOM_MSG:
            handle_my_custom_msg(msg);
            break;
    }

    // Call parent
    GCS_MAVLINK::handle_message(msg);
}

void GCS_MAVLINK_Rover::handle_my_custom_msg(const mavlink_message_t &msg) {
    mavlink_my_custom_msg_t packet;
    mavlink_msg_my_custom_msg_decode(&msg, &packet);

    // Process
    if (rover.control_mode == &rover.mode_guided) {
        rover.mode_guided.handle_custom(packet.field1, packet.field2);
    }
}
```

---

## Adding a Sensor

### Create Sensor Library (if new)

In `libraries/AP_MySensor/`:

```cpp
// AP_MySensor.h
class AP_MySensor {
public:
    void init();
    void update();
    float get_value() const { return _value; }

    static AP_MySensor *get_singleton() { return _singleton; }

private:
    static AP_MySensor *_singleton;
    float _value;
};
```

### Integrate with Rover

In `Rover/Parameters.h`:

```cpp
class ParametersG2 {
    AP_MySensor my_sensor;
};
```

In `Rover/Parameters.cpp`:

```cpp
// @Group: MYSNS_
// @Path: ../libraries/AP_MySensor/AP_MySensor.cpp
AP_SUBGROUPINFO(my_sensor, "MYSNS_", XX, ParametersG2, AP_MySensor),
```

In `Rover/system.cpp`:

```cpp
void Rover::init_ardupilot() {
    // ... existing init
    g2.my_sensor.init();
}
```

In `Rover/Rover.cpp`:

```cpp
// Add scheduler task
SCHED_TASK_CLASS(AP_MySensor, &g2.my_sensor, update, 50, 200, XX),
```

---

## Adding a Log Message

In `Rover/Log.cpp`:

```cpp
// Define structure
struct PACKED log_MyData {
    LOG_PACKET_HEADER;
    uint64_t time_us;
    float value1;
    float value2;
    int16_t status;
};

// Add to log formats
{LOG_MY_DATA_MSG, sizeof(log_MyData),
    "MYDT", "QffB", "TimeUS,Val1,Val2,Stat", "s---", "F---"},

// Write function
void Rover::Log_Write_MyData() {
    struct log_MyData pkt = {
        LOG_PACKET_HEADER_INIT(LOG_MY_DATA_MSG),
        time_us : AP_HAL::micros64(),
        value1  : my_value1,
        value2  : my_value2,
        status  : my_status
    };
    logger.WriteBlock(&pkt, sizeof(pkt));
}
```

Call from scheduler or mode:

```cpp
if (should_log(MASK_MY_LOG)) {
    Log_Write_MyData();
}
```

---

## Testing New Features

### SITL Testing

```bash
# Build for SITL
./waf configure --board sitl
./waf rover

# Run simulation
cd Tools/autotest
./sim_vehicle.py -v Rover -f rover --console --map
```

### Unit Testing

Add tests in `libraries/AP_MySensor/tests/`:

```cpp
// test_my_sensor.cpp
#include <AP_MySensor/AP_MySensor.h>
#include <gtest/gtest.h>

TEST(MySensor, Init) {
    AP_MySensor sensor;
    sensor.init();
    EXPECT_EQ(sensor.get_value(), 0.0f);
}
```

---

## Code Style Guidelines

1. **Naming**: Use `snake_case` for functions/variables, `CamelCase` for classes
2. **Indentation**: 4 spaces, no tabs
3. **Braces**: Same line for control structures
4. **Parameters**: Use `AP_Param` for user-configurable values
5. **Singletons**: Use `get_singleton()` pattern for shared objects
6. **Comments**: Doxygen style for public APIs
