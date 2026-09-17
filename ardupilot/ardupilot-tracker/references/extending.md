# Extending AntennaTracker

Guide to adding new functionality to ArduPilot AntennaTracker.

## Adding a New Mode

### Step 1: Define Mode Number

Add to `mode.h` enum:

```cpp
enum class Number : uint8_t {
    MANUAL       = 0,
    STOP         = 1,
    SCAN         = 2,
    SERVOTEST    = 3,
    GUIDED       = 4,
    MY_NEW_MODE  = 5,   // Pick unused number
    AUTO         = 10,
    INITIALISING = 16,
};
```

### Step 2: Create Mode Class

Add to `mode.h`:

```cpp
class ModeMyNew : public Mode {
public:
    using Mode::Mode;

    void update() override;
    bool requires_armed_servos() const override { return false; }

protected:
    const char *name() const override { return "MYNEW"; }
    const char *name4() const override { return "MYNW"; }
    Number number() const override { return Number::MY_NEW_MODE; }

private:
    float custom_state;
};
```

### Step 3: Implement Mode

Create `mode_mynew.cpp`:

```cpp
#include "mode.h"
#include "Tracker.h"

void ModeMyNew::update()
{
    // Custom tracking logic
    // Example: Track a fixed location

    // Get target bearing and pitch
    float target_yaw = 45.0f;  // Northeast
    float target_pitch = 30.0f; // 30 degrees up

    // Apply trim
    target_yaw = wrap_180(target_yaw + tracker.g.yaw_trim);
    target_pitch = constrain_float(target_pitch + tracker.g.pitch_trim,
                                    tracker.g.pitch_min,
                                    tracker.g.pitch_max);

    // Convert to centidegrees
    float yaw_cd = target_yaw * 100;
    float pitch_cd = target_pitch * 100;

    // Calculate angle error
    calc_angle_error(pitch_cd, yaw_cd, false);

    // Convert to body frame
    float bf_pitch, bf_yaw;
    convert_ef_to_bf(pitch_cd, yaw_cd, bf_pitch, bf_yaw);

    // Update servos
    tracker.update_pitch_servo(bf_pitch);
    tracker.update_yaw_servo(bf_yaw);
}
```

### Step 4: Add Mode Instance

In `Tracker.h`:

```cpp
class Tracker : public AP_Vehicle {
    // ... existing members

    ModeMyNew mode_mynew;

    // Add friend declaration
    friend class ModeMyNew;
};
```

### Step 5: Register Mode

In `system.cpp` or appropriate location:

```cpp
Mode* Tracker::mode_from_mode_num(Mode::Number num)
{
    switch (num) {
        case Mode::Number::MANUAL: return &mode_manual;
        case Mode::Number::STOP: return &mode_stop;
        case Mode::Number::SCAN: return &mode_scan;
        case Mode::Number::SERVOTEST: return &mode_servotest;
        case Mode::Number::GUIDED: return &mode_guided;
        case Mode::Number::MY_NEW_MODE: return &mode_mynew;  // Add this
        case Mode::Number::AUTO: return &mode_auto;
        case Mode::Number::INITIALISING: return &mode_initialising;
    }
    return nullptr;
}
```

## Adding a New Parameter

### Simple Parameter

```cpp
// 1. Add enum in Parameters.h
enum {
    k_param_my_new_param = 250,  // Pick unused number
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
// @Units: deg
// @User: Standard
GSCALAR(my_new_param, "MY_NEW_PARAM", 50.0f),

// 4. Use in code
float val = g.my_new_param.get();
```

## Adding a MAVLink Handler

In `GCS_MAVLink_Tracker.cpp`:

```cpp
void GCS_MAVLINK_Tracker::handle_message(const mavlink_message_t &msg)
{
    switch (msg.msgid) {
        // ... existing handlers

        case MAVLINK_MSG_ID_MY_MESSAGE:
            handle_my_message(msg);
            break;
    }

    GCS_MAVLINK::handle_message(msg);
}

void GCS_MAVLINK_Tracker::handle_my_message(const mavlink_message_t &msg)
{
    mavlink_my_message_t packet;
    mavlink_msg_my_message_decode(&msg, &packet);

    // Process the message
    tracker.handle_my_data(packet.field1, packet.field2);
}
```

## Adding a Scheduler Task

In `Tracker.cpp`:

```cpp
// Add to scheduler table
const AP_Scheduler::Task Tracker::scheduler_tasks[] = {
    // ... existing tasks

    // Function, Rate(Hz), MaxTime(us), Priority
    SCHED_TASK(my_custom_task, 10, 100, 75),
};

// Implement
void Tracker::my_custom_task()
{
    // Runs at 10Hz
    // Do periodic work here
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
void Tracker::Log_Write_MyData()
{
    struct log_MyData pkt = {
        LOG_PACKET_HEADER_INIT(LOG_MYDATA_MSG),
        time_us : AP_HAL::micros64(),
        value1  : my_value1,
        value2  : my_value2,
    };
    logger.WriteBlock(&pkt, sizeof(pkt));
}
```

## Custom Servo Type

To add a new servo control type:

### Step 1: Add Enum Value

```cpp
enum ServoType {
    SERVO_TYPE_ONOFF = 0,
    SERVO_TYPE_CR = 1,
    SERVO_TYPE_POSITION = 2,
    SERVO_TYPE_CUSTOM = 3,  // New type
};
```

### Step 2: Update Parameter Description

In `Parameters.cpp`:

```cpp
// @Param: SERVO_YAW_TYPE
// @DisplayName: Type of servo system being used for yaw
// @Description: This allows selection of position servos or on/off servos for yaw
// @Values: 0:Position,1:OnOff,2:ContinuousRotation,3:Custom
// @User: Standard
GSCALAR(servo_yaw_type, "SERVO_YAW_TYPE", SERVO_TYPE_POSITION),
```

### Step 3: Implement Control Function

In `servos.cpp`:

```cpp
void Tracker::update_yaw_custom_servo(float yaw)
{
    // Custom servo control logic
    float output = /* your algorithm */;
    SRV_Channels::set_output_scaled(SRV_Channel::k_tracker_yaw, output);
}
```

### Step 4: Add to Switch Statement

```cpp
void Tracker::update_yaw_servo(float yaw)
{
    switch ((enum ServoType)g.servo_yaw_type.get()) {
    case SERVO_TYPE_ONOFF:
        update_yaw_onoff_servo(yaw);
        break;
    case SERVO_TYPE_CR:
        update_yaw_cr_servo(yaw);
        break;
    case SERVO_TYPE_CUSTOM:
        update_yaw_custom_servo(yaw);  // New
        break;
    case SERVO_TYPE_POSITION:
    default:
        update_yaw_position_servo();
        break;
    }
}
```

## Testing in SITL

```bash
# Build for SITL
./waf configure --board sitl
./waf antennatracker

# Run simulation
cd Tools/autotest
./sim_vehicle.py -v AntennaTracker --console --map

# In MAVProxy, simulate a vehicle
module load tracker
tracker start

# Or connect to a real vehicle's telemetry
```

## Testing Mode Changes

```bash
# In MAVProxy
mode MANUAL
mode SCAN
mode AUTO

# Or by number
mode 0   # MANUAL
mode 2   # SCAN
mode 10  # AUTO
```

## Best Practices

1. **Frame conversion**: Always convert earth frame to body frame before servo output
2. **Angle wrapping**: Use `wrap_180()` for angles, `wrap_180_cd()` for centidegrees
3. **Limits**: Respect `PITCH_MIN`, `PITCH_MAX`, and `YAW_RANGE`
4. **Trim**: Apply `YAW_TRIM` and `PITCH_TRIM` to targets
5. **Distance check**: Honor `DISTANCE_MIN` parameter
6. **Testing**: Test in SITL before real hardware
7. **Logging**: Log key variables for debugging
8. **Code style**: Follow ArduPilot coding standards

## Common Pitfalls

1. **Forgetting body frame conversion**: Tracker may not be level
2. **Ignoring servo limits**: Can damage mechanical stops
3. **Not handling yaw wraparound**: 359° to 1° crossing
4. **Missing parameter validation**: Check ranges in code
5. **PID windup**: Reset integrator at limits
