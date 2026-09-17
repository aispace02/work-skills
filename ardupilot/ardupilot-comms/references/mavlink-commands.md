# MAVLink Commands

Handling MAV_CMD commands via COMMAND_INT and COMMAND_LONG messages.

## Command Flow

```
GCS sends COMMAND_LONG or COMMAND_INT
        ↓
handle_command_long() / handle_command_int()
        ↓
convert_COMMAND_LONG_to_COMMAND_INT() (if LONG)
        ↓
handle_command_int_packet()
        ↓
Send COMMAND_ACK with MAV_RESULT
```

## Handling Commands

### Override Pattern

```cpp
// In vehicle's GCS_MAVLINK subclass
MAV_RESULT GCS_MAVLINK_Copter::handle_command_int_packet(
    const mavlink_command_int_t &packet,
    const mavlink_message_t &msg)
{
    switch (packet.command) {
        case MAV_CMD_NAV_TAKEOFF:
            return handle_command_takeoff(packet);

        case MAV_CMD_DO_SET_MODE:
            return handle_command_do_set_mode(packet);

        case MAV_CMD_COMPONENT_ARM_DISARM:
            return handle_command_component_arm_disarm(packet);

        default:
            return GCS_MAVLINK::handle_command_int_packet(packet, msg);
    }
}
```

### Command Packet Structure

```cpp
typedef struct {
    float param1;       // Parameter 1
    float param2;       // Parameter 2
    float param3;       // Parameter 3
    float param4;       // Parameter 4
    int32_t x;          // Latitude (1e7) or local X
    int32_t y;          // Longitude (1e7) or local Y
    float z;            // Altitude
    uint16_t command;   // MAV_CMD enum
    uint8_t target_system;
    uint8_t target_component;
    uint8_t frame;      // MAV_FRAME enum
    uint8_t current;    // Not used
    uint8_t autocontinue;
} mavlink_command_int_t;
```

---

## MAV_RESULT Responses

```cpp
enum MAV_RESULT {
    MAV_RESULT_ACCEPTED = 0,              // Command accepted and executed
    MAV_RESULT_TEMPORARILY_REJECTED = 1,  // Retry later
    MAV_RESULT_DENIED = 2,                // Not supported or denied
    MAV_RESULT_UNSUPPORTED = 3,           // Unknown command
    MAV_RESULT_FAILED = 4,                // Execution failed
    MAV_RESULT_IN_PROGRESS = 5,           // Still executing (long-running)
    MAV_RESULT_CANCELLED = 6,             // Cancelled by new command
    MAV_RESULT_COMMAND_LONG_ONLY = 7,     // Only COMMAND_LONG supported
    MAV_RESULT_COMMAND_INT_ONLY = 8,      // Only COMMAND_INT supported
    MAV_RESULT_COMMAND_UNSUPPORTED_MAV_FRAME = 9,
};
```

### Example Handler

```cpp
MAV_RESULT GCS_MAVLINK_Copter::handle_command_takeoff(const mavlink_command_int_t &packet) {
    // packet.z is target altitude
    float target_alt = packet.z;

    // Validate
    if (!motors->armed()) {
        return MAV_RESULT_DENIED;
    }

    if (!copter.do_user_takeoff(target_alt, true)) {
        return MAV_RESULT_FAILED;
    }

    return MAV_RESULT_ACCEPTED;
}
```

---

## Long-Running Commands

For commands that take time to complete:

### Using GCS_MAVLINK_InProgress

```cpp
MAV_RESULT GCS_MAVLINK::handle_command_preflight_calibration(
    const mavlink_command_int_t &packet,
    const mavlink_message_t &msg)
{
    if (packet.param1 == 1) {
        // Gyro calibration - long running
        GCS_MAVLINK_InProgress *task = GCS_MAVLINK_InProgress::get_task(
            MAV_CMD_PREFLIGHT_CALIBRATION,
            GCS_MAVLINK_InProgress::Type::GYRO_CAL,
            msg.sysid,
            msg.compid,
            chan
        );

        if (task == nullptr) {
            return MAV_RESULT_TEMPORARILY_REJECTED;
        }

        // Start calibration
        if (!ins.calibrate_gyros()) {
            task->abort();
            return MAV_RESULT_FAILED;
        }

        // Will call task->conclude(MAV_RESULT_ACCEPTED) when done
        return MAV_RESULT_IN_PROGRESS;
    }

    return MAV_RESULT_UNSUPPORTED;
}
```

### Progress Updates

```cpp
// Send intermediate progress ACK
task->send_in_progress();

// Complete the command
task->conclude(MAV_RESULT_ACCEPTED);

// Or abort without sending ACK
task->abort();
```

---

## Common Commands

### Arm/Disarm

```cpp
case MAV_CMD_COMPONENT_ARM_DISARM:
    // param1: 1=arm, 0=disarm
    // param2: 0=normal, 21196=force
    if (is_equal(packet.param1, 1.0f)) {
        if (!arming.arm(AP_Arming::Method::MAVLINK)) {
            return MAV_RESULT_FAILED;
        }
    } else {
        if (!arming.disarm(AP_Arming::Method::MAVLINK)) {
            return MAV_RESULT_FAILED;
        }
    }
    return MAV_RESULT_ACCEPTED;
```

### Set Mode

```cpp
case MAV_CMD_DO_SET_MODE:
    // param1: base_mode (not used much)
    // param2: custom_mode (flight mode number)
    if (!copter.set_mode((Mode::Number)packet.param2, ModeReason::GCS_COMMAND)) {
        return MAV_RESULT_FAILED;
    }
    return MAV_RESULT_ACCEPTED;
```

### Set Home

```cpp
case MAV_CMD_DO_SET_HOME:
    // param1: 1=use current location, 0=use specified
    if (is_equal(packet.param1, 1.0f)) {
        if (!set_home_to_current_location(true)) {
            return MAV_RESULT_FAILED;
        }
    } else {
        Location loc;
        if (!location_from_command_t(packet, loc)) {
            return MAV_RESULT_DENIED;
        }
        if (!set_home(loc, true)) {
            return MAV_RESULT_FAILED;
        }
    }
    return MAV_RESULT_ACCEPTED;
```

---

## Location from Command

Helper to extract Location from command packet:

```cpp
bool GCS_MAVLINK::location_from_command_t(const mavlink_command_int_t &in, Location &out) {
    Location::AltFrame frame;
    if (!mavlink_coordinate_frame_to_location_alt_frame(
            (MAV_FRAME)in.frame, frame)) {
        return false;
    }

    out.lat = in.x;
    out.lng = in.y;
    out.set_alt_cm((int32_t)(in.z * 100), frame);
    return true;
}
```

---

## Sending Command ACK

Automatic via return value, but can send manually:

```cpp
mavlink_msg_command_ack_send(
    chan,
    command,           // MAV_CMD
    result,            // MAV_RESULT
    0,                 // progress (0-100, 255=unknown)
    0,                 // result_param2
    msg.sysid,         // target_system
    msg.compid         // target_component
);
```

---

## COMMAND_LONG vs COMMAND_INT

- **COMMAND_INT**: Preferred. Uses int32 for lat/lon (1e7 degrees), avoiding float precision issues.
- **COMMAND_LONG**: Legacy. Uses float for all params including position.

ArduPilot converts COMMAND_LONG to COMMAND_INT internally:

```cpp
void GCS_MAVLINK::handle_command_long(const mavlink_message_t &msg) {
    mavlink_command_long_t packet;
    mavlink_msg_command_long_decode(&msg, &packet);

    mavlink_command_int_t int_packet;
    convert_COMMAND_LONG_to_COMMAND_INT(packet, int_packet);

    MAV_RESULT result = handle_command_int_packet(int_packet, msg);
    // ... send ACK
}
```
