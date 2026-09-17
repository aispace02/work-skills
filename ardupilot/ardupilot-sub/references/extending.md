# Extending ArduSub

Guide to adding new functionality to ArduPilot Sub.

## Adding a New Flight Mode

### Step 1: Define Mode Number

Add to `mode.h` enum:

```cpp
enum class Number : uint8_t {
    STABILIZE = 0,
    // ... existing modes
    MY_NEW_MODE = 22,  // Pick unused number
};
```

### Step 2: Create Mode Class

Add to `mode.h`:

```cpp
class ModeMyNew : public Mode {
public:
    using Mode::Mode;

    virtual void run() override;
    bool init(bool ignore_checks) override;

    bool requires_GPS() const override { return false; }
    bool requires_altitude() const override { return true; }
    bool allows_arming(bool from_gcs) const override { return true; }
    bool is_autopilot() const override { return false; }

protected:
    const char *name() const override { return "MY_NEW"; }
    const char *name4() const override { return "MNEW"; }
    Mode::Number number() const override { return Mode::Number::MY_NEW_MODE; }

private:
    uint32_t enter_time_ms;
};
```

### Step 3: Implement Mode

Create `mode_mynew.cpp`:

```cpp
#include "Sub.h"

bool ModeMyNew::init(bool ignore_checks) {
    // Check prerequisites
    if (requires_altitude() && !sub.control_check_barometer()) {
        return false;
    }

    // Initialize controllers
    position_control->D_set_max_speed_accel_cm(
        sub.get_pilot_speed_dn(), g.pilot_speed_up, g.pilot_accel_z);
    position_control->D_init_controller();

    enter_time_ms = AP_HAL::millis();
    sub.last_pilot_heading = ahrs.yaw_sensor;

    return true;
}

void ModeMyNew::run() {
    // Check armed state
    if (!motors.armed()) {
        motors.set_desired_spool_state(AP_Motors::DesiredSpoolState::GROUND_IDLE);
        attitude_control->set_throttle_out(0.5f, true, g.throttle_filt);
        attitude_control->relax_attitude_controllers();
        return;
    }

    motors.set_desired_spool_state(AP_Motors::DesiredSpoolState::THROTTLE_UNLIMITED);

    // Get pilot inputs
    float target_roll, target_pitch;
    sub.get_pilot_desired_lean_angles(
        channel_roll->get_control_in(),
        channel_pitch->get_control_in(),
        target_roll, target_pitch,
        attitude_control->get_althold_lean_angle_max_cd());

    float target_yaw_rate = sub.get_pilot_desired_yaw_rate(
        channel_yaw->get_control_in());

    // Attitude control
    attitude_control->input_euler_angle_roll_pitch_euler_rate_yaw_cd(
        target_roll, target_pitch, target_yaw_rate);

    // Depth control
    float target_climb_rate = sub.get_pilot_desired_climb_rate(
        channel_throttle->get_control_in());
    position_control->D_set_pos_target_from_climb_rate_cms(target_climb_rate);
    position_control->D_update_controller();

    // Forward/lateral
    motors.set_forward(channel_forward->norm_input());
    motors.set_lateral(channel_lateral->norm_input());
}
```

### Step 4: Add Mode Instance

In `Sub.h`:

```cpp
class Sub : public AP_Vehicle {
    // ... existing members
    ModeMyNew mode_mynew;
};
```

### Step 5: Register Mode

In `mode.cpp`:

```cpp
Mode *Sub::mode_from_mode_num(const Mode::Number num) {
    switch (num) {
        // ... existing cases
        case Mode::Number::MY_NEW_MODE:
            return &mode_mynew;
    }
    return nullptr;
}
```

## Adding a New Parameter

### Simple Parameter

```cpp
// 1. Add enum in Parameters.h
enum {
    // ...
    k_param_my_new_param = 250,
};

// 2. Add variable in Parameters.h
class Parameters {
    AP_Float my_new_param;
};

// 3. Add definition in Parameters.cpp
// @Param: MY_NEW_PARAM
// @DisplayName: My New Parameter
// @Description: Description of what this parameter does
// @Range: 0 100
// @User: Standard
GSCALAR(my_new_param, "MY_NEW", 50.0f),

// 4. Use in code
float val = g.my_new_param.get();
```

### Mode-Specific Parameter

```cpp
// In mode.h class definition
class ModeMyNew : public Mode {
    static const struct AP_Param::GroupInfo var_info[];
    AP_Float my_mode_param;
};

// In mode_mynew.cpp
const AP_Param::GroupInfo ModeMyNew::var_info[] = {
    // @Param: MYNEW_PARAM
    // @DisplayName: My mode parameter
    // @Description: Parameter specific to this mode
    // @Range: 0 10
    AP_GROUPINFO("PARAM", 1, ModeMyNew, my_mode_param, 5.0f),

    AP_GROUPEND
};
```

## Adding a Mission Command

### Navigation Command

In `commands_logic.cpp`:

```cpp
// 1. Add to start_command()
bool Sub::start_command(const AP_Mission::Mission_Command& cmd) {
    switch (cmd.id) {
        // ... existing cases
        case MAV_CMD_NAV_MY_COMMAND:
            return do_nav_my_command(cmd);
    }
}

// 2. Implement handler
bool Sub::do_nav_my_command(const AP_Mission::Mission_Command& cmd) {
    // Extract parameters
    Location target = cmd.content.location;
    float param1 = cmd.p1;

    // Setup navigation
    mode_auto.auto_wp_start(target);

    return true;
}

// 3. Add verification
bool Sub::verify_nav_my_command(const AP_Mission::Mission_Command& cmd) {
    // Check if command is complete
    return wp_nav.reached_wp_destination();
}

// 4. Add to verify_command()
bool Sub::verify_command(const AP_Mission::Mission_Command& cmd) {
    switch (cmd.id) {
        case MAV_CMD_NAV_MY_COMMAND:
            return verify_nav_my_command(cmd);
    }
}
```

### DO Command

```cpp
bool Sub::start_command(const AP_Mission::Mission_Command& cmd) {
    switch (cmd.id) {
        case MAV_CMD_DO_MY_ACTION:
            return do_my_action(cmd);
    }
}

bool Sub::do_my_action(const AP_Mission::Mission_Command& cmd) {
    // Execute immediate action
    // DO commands complete immediately
    return true;
}
```

## Adding a Scheduler Task

In `Sub.cpp`:

```cpp
// 1. Declare function
void Sub::my_custom_task();

// 2. Add to scheduler table
const AP_Scheduler::Task Sub::scheduler_tasks[] = {
    // ... existing tasks

    // Function, Rate(Hz), MaxTime(us), Priority
    SCHED_TASK(my_custom_task, 10, 100, 200),
};

// 3. Implement
void Sub::my_custom_task() {
    // Runs at 10Hz
    // Keep execution under 100us typically
}
```

## Adding a MAVLink Handler

In `GCS_MAVLink_Sub.cpp`:

```cpp
void GCS_MAVLINK_Sub::handle_message(const mavlink_message_t &msg) {
    switch (msg.msgid) {
        // ... existing handlers

        case MAVLINK_MSG_ID_MY_MESSAGE:
            handle_my_message(msg);
            break;
    }

    // Call parent
    GCS_MAVLINK::handle_message(msg);
}

void GCS_MAVLINK_Sub::handle_my_message(const mavlink_message_t &msg) {
    mavlink_my_message_t packet;
    mavlink_msg_my_message_decode(&msg, &packet);

    // Process
    sub.handle_my_data(packet.field1, packet.field2);
}
```

## Adding a Log Message

In `Log.cpp`:

```cpp
// 1. Define structure
struct PACKED log_MyData {
    LOG_PACKET_HEADER;
    uint64_t time_us;
    float value1;
    float value2;
    int16_t state;
};

// 2. Add to log formats (in log_structure)
{ LOG_MYDATA_MSG, sizeof(log_MyData),
    "MYDT", "Qffh", "TimeUS,V1,V2,Sta", "s---", "F---" },

// 3. Write function
void Sub::Log_Write_MyData() {
    struct log_MyData pkt = {
        LOG_PACKET_HEADER_INIT(LOG_MYDATA_MSG),
        time_us : AP_HAL::micros64(),
        value1  : my_value1,
        value2  : my_value2,
        state   : my_state
    };
    logger.WriteBlock(&pkt, sizeof(pkt));
}
```

## Adding a Joystick Button Function

### Define Function

In `AP_JSButton.h`:

```cpp
enum button_function_t {
    // ... existing functions
    k_my_function = 100,
};
```

### Handle in joystick.cpp

```cpp
void Sub::handle_jsbutton_press(uint8_t _button, bool shift, bool held) {
    switch (get_button(_button)->function(shift)) {
        // ... existing cases

        case JSButton::button_function_t::k_my_function:
            if (!held) {
                // Action on press
                my_function_action();
            }
            break;
    }
}

void Sub::handle_jsbutton_release(uint8_t _button, bool shift) {
    switch (get_button(_button)->function(shift)) {
        case JSButton::button_function_t::k_my_function:
            // Action on release (if needed)
            break;
    }
}
```

## Testing in SITL

```bash
# Build for SITL
./waf configure --board sitl
./waf sub

# Run simulation
cd Tools/autotest
./sim_vehicle.py -v ArduSub --console --map

# With specific location
./sim_vehicle.py -v ArduSub --map --console -L underwater_location
```

## Best Practices

1. **Mode design**: Check prerequisites in `init()`, handle disarmed state in `run()`
2. **Parameter naming**: Use consistent prefixes related to feature
3. **Logging**: Log enough data for post-dive analysis
4. **Safety**: Always consider failsafe implications
5. **Testing**: Test in SITL before real hardware
6. **Code style**: Follow ArduPilot coding standards
7. **Documentation**: Add @Param comments for all parameters
