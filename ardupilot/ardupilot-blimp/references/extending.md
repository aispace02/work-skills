# Extending Blimp

Guide to adding new functionality to ArduPilot Blimp.

## Adding a New Flight Mode

### Step 1: Define Mode Number

Add to `mode.h` enum:

```cpp
enum class Number : uint8_t {
    LAND = 0,
    MANUAL = 1,
    VELOCITY = 2,
    LOITER = 3,
    RTL = 4,
    MY_NEW_MODE = 5,  // Pick unused number
};
```

### Step 2: Create Mode Class

Add to `mode.h`:

```cpp
class ModeMyNew : public Mode {
public:
    using Mode::Mode;

    virtual bool init(bool ignore_checks) override;
    virtual void run() override;

    bool requires_GPS() const override { return true; }
    bool has_manual_throttle() const override { return false; }
    bool allows_arming(bool from_gcs) const override { return true; }
    bool is_autopilot() const override { return false; }

protected:
    const char *name() const override { return "MYNEW"; }
    const char *name4() const override { return "MNEW"; }
    Mode::Number number() const override { return Mode::Number::MY_NEW_MODE; }

private:
    Vector3f target_pos;
    float target_yaw;
};
```

### Step 3: Implement Mode

Create `mode_mynew.cpp`:

```cpp
#include "Blimp.h"

bool ModeMyNew::init(bool ignore_checks) {
    // Initialize target to current position
    target_pos = blimp.pos_ned;
    target_yaw = blimp.ahrs.get_yaw_rad();
    return true;
}

void ModeMyNew::run() {
    // Get pilot input
    Vector3f pilot;
    float pilot_yaw;
    get_pilot_input(pilot, pilot_yaw);

    // Scale input
    const float dt = blimp.scheduler.get_last_loop_time_s();
    pilot.x *= g.max_pos_xy * dt;
    pilot.y *= g.max_pos_xy * dt;
    pilot.z *= g.max_pos_z * dt;
    pilot_yaw *= g.max_pos_yaw * dt;

    // Transform if simple mode disabled
    if (g.simple_mode == 0) {
        blimp.rotate_BF_to_NE(pilot.xy());
    }

    // Update targets
    target_pos += pilot;
    target_yaw = wrap_PI(target_yaw + pilot_yaw);

    // Run position controller
    blimp.loiter->run(target_pos, target_yaw, Vector4b{false,false,false,false});
}
```

### Step 4: Add Mode Instance

In `Blimp.h`:

```cpp
class Blimp : public AP_Vehicle {
    // ... existing members
    ModeMyNew mode_mynew;
};

// Add friend declaration
friend class ModeMyNew;
```

### Step 5: Register Mode

In `mode.cpp`:

```cpp
Mode *Blimp::mode_from_mode_num(const Mode::Number mode) {
    switch (mode) {
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
    k_param_my_new_param = 70,  // Pick unused number
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

## Adding a Scheduler Task

In `Blimp.cpp`:

```cpp
// Add to scheduler table
const AP_Scheduler::Task Blimp::scheduler_tasks[] = {
    // ... existing tasks

    // Function, Rate(Hz), MaxTime(us), Priority
    SCHED_TASK(my_custom_task, 10, 100, 75),
};

// Implement
void Blimp::my_custom_task() {
    // Runs at 10Hz
}
```

## Adding a MAVLink Handler

In `GCS_MAVLink_Blimp.cpp`:

```cpp
void GCS_MAVLINK_Blimp::handle_message(const mavlink_message_t &msg) {
    switch (msg.msgid) {
        // ... existing handlers

        case MAVLINK_MSG_ID_MY_MESSAGE:
            handle_my_message(msg);
            break;
    }

    GCS_MAVLINK::handle_message(msg);
}

void GCS_MAVLINK_Blimp::handle_my_message(const mavlink_message_t &msg) {
    mavlink_my_message_t packet;
    mavlink_msg_my_message_decode(&msg, &packet);

    blimp.handle_my_data(packet.field1, packet.field2);
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
};

// 2. Add to log_structure
{ LOG_MYDATA_MSG, sizeof(log_MyData),
    "MYDT", "Qff", "TimeUS,V1,V2", "s--", "F--" },

// 3. Write function
void Blimp::Log_Write_MyData() {
    struct log_MyData pkt = {
        LOG_PACKET_HEADER_INIT(LOG_MYDATA_MSG),
        time_us : AP_HAL::micros64(),
        value1  : my_value1,
        value2  : my_value2,
    };
    logger.WriteBlock(&pkt, sizeof(pkt));
}
```

## Custom Fin Configuration

In `Fins.cpp`, modify `setup_fins()`:

```cpp
void Fins::setup_fins() {
    // Custom arrangement
    //          fin#  r_amp f_amp d_amp y_amp r_off f_off d_off y_off
    add_fin(0,  0.5,  0.5,  0,    0,    0,    0,    0,    0);
    add_fin(1, -0.5,  0.5,  0,    0,    0,    0,    0,    0);
    add_fin(2,  0,    0,    0.5,  0.5,  0,    0,    0,    0);
    add_fin(3,  0,    0,    0.5, -0.5,  0,    0,    0,    0);

    // Setup servo channels
    SRV_Channels::set_angle(SRV_Channel::k_motor1, FIN_SCALE_MAX);
    SRV_Channels::set_angle(SRV_Channel::k_motor2, FIN_SCALE_MAX);
    SRV_Channels::set_angle(SRV_Channel::k_motor3, FIN_SCALE_MAX);
    SRV_Channels::set_angle(SRV_Channel::k_motor4, FIN_SCALE_MAX);
}
```

## Testing in SITL

```bash
# Build for SITL
./waf configure --board sitl
./waf blimp

# Run simulation
cd Tools/autotest
./sim_vehicle.py -v Blimp --console --map
```

## Best Practices

1. **Mode design**: Initialize targets in `init()`, handle pilot input in `run()`
2. **Simple mode**: Support both body-frame and earth-frame inputs
3. **Deadzone**: Use `PID_DZ` parameter for position deadzone
4. **Scaling**: Respect `MAX_VEL_*` and `MAX_POS_*` limits
5. **Testing**: Test in SITL before real hardware
6. **Logging**: Log fin inputs and outputs for tuning
7. **Code style**: Follow ArduPilot coding standards
