# Extending ArduCopter

Guide to adding new functionality to ArduPilot Copter.

## Adding a New Flight Mode

### Step 1: Define Mode Number

Add to `mode.h` enum:

```cpp
enum class Number : uint8_t {
    STABILIZE = 0,
    // ... existing modes
    MY_NEW_MODE = 30,  // Pick unused number
};
```

### Step 2: Create Mode Class

Add to `mode.h`:

```cpp
class ModeMyNew : public Mode {
public:
    using Mode::Mode;

    Number mode_number() const override { return Number::MY_NEW_MODE; }

    bool init(bool ignore_checks) override;
    void run() override;

    bool requires_GPS() const override { return false; }
    bool has_manual_throttle() const override { return false; }
    bool allows_arming(AP_Arming::Method method) const override { return true; }
    bool is_autopilot() const override { return false; }

    // Optional overrides
    bool has_user_takeoff(bool must_navigate) const override { return true; }
    bool allows_flip() const override { return true; }

protected:
    const char *name() const override { return "MY_NEW"; }
    const char *name4() const override { return "MNEW"; }

private:
    uint32_t enter_time_ms;
};
```

### Step 3: Implement Mode

Create `mode_mynew.cpp`:

```cpp
#include "Copter.h"

bool ModeMyNew::init(bool ignore_checks) {
    // Initialize controllers
    pos_control->D_init_controller();
    pos_control->D_set_max_speed_accel_m(
        get_pilot_speed_dn_ms(),
        get_pilot_speed_up_ms(),
        get_pilot_accel_D_mss()
    );

    enter_time_ms = AP_HAL::millis();
    return true;
}

void ModeMyNew::run() {
    // Apply simple mode
    update_simple_mode();

    // Get pilot inputs
    float target_roll_rad, target_pitch_rad;
    get_pilot_desired_lean_angles_rad(
        target_roll_rad, target_pitch_rad,
        attitude_control->lean_angle_max_rad(),
        attitude_control->lean_angle_max_rad()
    );

    float target_yaw_rate = get_pilot_desired_yaw_rate_rads();
    float target_climb_rate = get_pilot_desired_climb_rate_ms();

    // Get flight state
    AltHoldModeState state = get_alt_hold_state_D_ms(target_climb_rate);

    switch (state) {
        case AltHoldModeState::MotorStopped:
            attitude_control->reset_rate_controller_I_terms();
            attitude_control->reset_yaw_target_and_rate();
            pos_control->D_relax_controller(0.0f);
            break;

        case AltHoldModeState::Landed_Ground_Idle:
        case AltHoldModeState::Landed_Pre_Takeoff:
            attitude_control->reset_rate_controller_I_terms_smoothly();
            pos_control->D_relax_controller(0.0f);
            break;

        case AltHoldModeState::Flying:
            motors->set_desired_spool_state(AP_Motors::DesiredSpoolState::THROTTLE_UNLIMITED);
            pos_control->D_set_pos_target_from_climb_rate_ms(target_climb_rate);
            break;
    }

    // Attitude control
    attitude_control->input_euler_angle_roll_pitch_euler_rate_yaw_rad(
        target_roll_rad, target_pitch_rad, target_yaw_rate);

    // Vertical control
    pos_control->D_update_controller();
}
```

### Step 4: Add Mode Instance

In `Copter.h`:

```cpp
class Copter : public AP_Vehicle {
    // ... existing members
    ModeMyNew mode_mynew;
};
```

### Step 5: Register Mode

In `mode.cpp`:

```cpp
Mode *Copter::mode_from_mode_num(const Mode::Number num) {
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
    k_param_my_new_param = 250,
};

// 2. Add variable in Parameters class
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

## Adding a Mission Command

### Navigation Command

In `mode_auto.cpp`:

```cpp
// 1. Add to start_command()
bool ModeAuto::start_command(const AP_Mission::Mission_Command& cmd) {
    switch (cmd.id) {
        // ... existing cases
        case MAV_CMD_NAV_MY_COMMAND:
            return do_nav_my_command(cmd);
    }
}

// 2. Implement handler
bool ModeAuto::do_nav_my_command(const AP_Mission::Mission_Command& cmd) {
    // Extract parameters
    Location target = cmd.content.location;

    // Start waypoint navigation
    return wp_start(target);
}

// 3. Add verification
bool ModeAuto::verify_nav_my_command(const AP_Mission::Mission_Command& cmd) {
    return wp_nav->reached_wp_destination();
}

// 4. Add to verify_command()
bool ModeAuto::verify_command(const AP_Mission::Mission_Command& cmd) {
    switch (cmd.id) {
        case MAV_CMD_NAV_MY_COMMAND:
            return verify_nav_my_command(cmd);
    }
}
```

## Adding a Scheduler Task

In `Copter.cpp`:

```cpp
// 1. Declare function
void Copter::my_custom_task();

// 2. Add to scheduler table
const AP_Scheduler::Task Copter::scheduler_tasks[] = {
    // ... existing tasks

    // Function, Rate(Hz), MaxTime(us), Priority
    SCHED_TASK(my_custom_task, 10, 100, 200),
};

// 3. Implement
void Copter::my_custom_task() {
    // Runs at 10Hz
}
```

## Adding a MAVLink Handler

In `GCS_MAVLink_Copter.cpp`:

```cpp
void GCS_MAVLINK_Copter::handle_message(const mavlink_message_t &msg) {
    switch (msg.msgid) {
        // ... existing handlers

        case MAVLINK_MSG_ID_MY_MESSAGE:
            handle_my_message(msg);
            break;
    }

    GCS_MAVLINK::handle_message(msg);
}

void GCS_MAVLINK_Copter::handle_my_message(const mavlink_message_t &msg) {
    mavlink_my_message_t packet;
    mavlink_msg_my_message_decode(&msg, &packet);

    copter.handle_my_data(packet.field1, packet.field2);
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

// 2. Add to log formats
{ LOG_MYDATA_MSG, sizeof(log_MyData),
    "MYDT", "Qffh", "TimeUS,V1,V2,Sta", "s---", "F---" },

// 3. Write function
void Copter::Log_Write_MyData() {
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

## Testing in SITL

```bash
# Build for SITL
./waf configure --board sitl
./waf copter

# Run simulation
cd Tools/autotest
./sim_vehicle.py -v ArduCopter --console --map

# With specific frame
./sim_vehicle.py -v ArduCopter --frame quad --console --map
./sim_vehicle.py -v ArduCopter --frame hexa --console --map

# With specific location
./sim_vehicle.py -v ArduCopter --map --console -L CMAC
```

## Best Practices

1. **Mode design**: Use `get_alt_hold_state_D_ms()` for consistent altitude behavior
2. **Safety**: Always handle disarmed/landed states in `run()`
3. **Simple mode**: Call `update_simple_mode()` for user-friendly controls
4. **Parameters**: Use consistent naming with prefixes
5. **Testing**: Test in SITL before real hardware
6. **Logging**: Log enough data for debugging
7. **Code style**: Follow ArduPilot coding standards
