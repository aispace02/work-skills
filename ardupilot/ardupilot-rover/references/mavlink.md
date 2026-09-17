# Rover MAVLink Handling

## GCS_MAVLINK_Rover

**Location**: `Rover/GCS_MAVLink_Rover.h`, `Rover/GCS_MAVLink_Rover.cpp`

Rover-specific MAVLink message handling.

## Class Hierarchy

```
GCS_MAVLINK (base)
    └── GCS_MAVLINK_Rover
            └── Handles Rover-specific messages

GCS (base)
    └── GCS_Rover
            └── Creates GCS_MAVLINK_Rover instances
```

## Key Message Handlers

### handle_message()

```cpp
void GCS_MAVLINK_Rover::handle_message(const mavlink_message_t &msg) {
    switch (msg.msgid) {
        case MAVLINK_MSG_ID_SET_POSITION_TARGET_LOCAL_NED:
            handle_set_position_target_local_ned(msg);
            break;
        case MAVLINK_MSG_ID_SET_POSITION_TARGET_GLOBAL_INT:
            handle_set_position_target_global_int(msg);
            break;
        case MAVLINK_MSG_ID_SET_ATTITUDE_TARGET:
            handle_set_attitude_target(msg);
            break;
        // ... other handlers
    }
    // Call parent handler
    GCS_MAVLINK::handle_message(msg);
}
```

### Position Target (Global)

```cpp
void GCS_MAVLINK_Rover::handle_set_position_target_global_int(
    const mavlink_message_t &msg
) {
    mavlink_set_position_target_global_int_t packet;
    mavlink_msg_set_position_target_global_int_decode(&msg, &packet);

    // Create target location
    Location target_loc(packet.lat_int, packet.lon_int, 0, Location::AltFrame::ABOVE_HOME);

    // Set in Guided mode
    if (rover.control_mode == &rover.mode_guided) {
        rover.mode_guided.set_desired_location(target_loc);
    }
}
```

### Position Target (Local NED)

```cpp
void GCS_MAVLINK_Rover::handle_set_position_target_local_ned(
    const mavlink_message_t &msg
) {
    mavlink_set_position_target_local_ned_t packet;
    mavlink_msg_set_position_target_local_ned_decode(&msg, &packet);

    // Convert NED offset to Location
    Location target_loc = rover.home;
    target_loc.offset(packet.x, packet.y);

    if (rover.control_mode == &rover.mode_guided) {
        rover.mode_guided.set_desired_location(target_loc);
    }
}
```

### Attitude Target

```cpp
void GCS_MAVLINK_Rover::handle_set_attitude_target(
    const mavlink_message_t &msg
) {
    mavlink_set_attitude_target_t packet;
    mavlink_msg_set_attitude_target_decode(&msg, &packet);

    // Extract yaw from quaternion
    float yaw;
    if (!(packet.type_mask & ATTITUDE_TARGET_TYPEMASK_ATTITUDE_IGNORE)) {
        yaw = Quaternion(packet.q[0], packet.q[1], packet.q[2], packet.q[3]).get_euler_yaw();
    }

    // Extract yaw rate
    float yaw_rate = 0;
    if (!(packet.type_mask & ATTITUDE_TARGET_TYPEMASK_BODY_RATE_IGNORE)) {
        yaw_rate = packet.body_yaw_rate;
    }

    // Throttle
    float throttle = packet.thrust;

    // Set in Guided mode
    rover.mode_guided.set_desired_attitude(yaw, yaw_rate, throttle);
}
```

### Manual Control

```cpp
void GCS_MAVLINK_Rover::handle_manual_control_axes(
    const mavlink_manual_control_t &packet
) {
    // Set RC override from joystick
    // x = pitch (-1000 to 1000) → throttle
    // y = roll (-1000 to 1000) → steering
    // r = yaw (-1000 to 1000) → lateral (boats)

    float throttle = packet.x / 1000.0f;
    float steering = packet.y / 1000.0f;
    float lateral = packet.r / 1000.0f;

    // Apply to manual control
    rover.handle_manual_input(throttle, steering, lateral);
}
```

## Command Handling

### handle_command_int_packet()

```cpp
MAV_RESULT GCS_MAVLINK_Rover::handle_command_int_packet(
    const mavlink_command_int_t &packet
) {
    switch (packet.command) {
        case MAV_CMD_NAV_SET_YAW_SPEED:
            return handle_command_nav_set_yaw_speed(packet);

        case MAV_CMD_DO_CHANGE_SPEED:
            return handle_command_do_change_speed(packet);

        case MAV_CMD_MISSION_START:
            rover.set_mode(Mode::Number::AUTO, ModeReason::GCS_COMMAND);
            return MAV_RESULT_ACCEPTED;

        // ... other commands
    }
    return GCS_MAVLINK::handle_command_int_packet(packet);
}
```

### NAV_SET_YAW_SPEED

```cpp
MAV_RESULT handle_command_nav_set_yaw_speed(
    const mavlink_command_int_t &packet
) {
    // param1 = yaw angle (degrees)
    // param2 = speed (m/s)
    // param3 = angle type (0=absolute, 1=relative)

    float yaw_deg = packet.param1;
    float speed = packet.param2;
    bool relative = (packet.param3 > 0);

    if (relative) {
        yaw_deg += degrees(rover.ahrs.get_yaw());
    }

    rover.mode_guided.set_desired_speed_and_heading(speed, radians(yaw_deg));
    return MAV_RESULT_ACCEPTED;
}
```

## Telemetry Streaming

### send_nav_controller_output()

```cpp
void GCS_MAVLINK_Rover::send_nav_controller_output() const {
    mavlink_msg_nav_controller_output_send(
        chan,
        0,                                    // nav_roll (N/A for rover)
        0,                                    // nav_pitch (N/A)
        rover.nav_bearing_cd() * 0.01f,       // nav_bearing (deg)
        rover.target_bearing_cd() * 0.01f,    // target_bearing (deg)
        rover.get_distance_to_destination(),  // wp_dist (m)
        0,                                    // alt_error (N/A)
        0,                                    // aspd_error (N/A)
        rover.crosstrack_error()              // xtrack_error (m)
    );
}
```

### send_position_target_global_int()

```cpp
void GCS_MAVLINK_Rover::send_position_target_global_int() const {
    Location target;
    if (rover.control_mode->get_desired_location(target)) {
        mavlink_msg_position_target_global_int_send(
            chan,
            AP_HAL::millis(),
            MAV_FRAME_GLOBAL_INT,
            0,                          // type_mask
            target.lat,                 // lat_int
            target.lng,                 // lon_int
            0,                          // alt
            0, 0, 0,                    // vx, vy, vz
            0, 0, 0,                    // afx, afy, afz
            0, 0                        // yaw, yaw_rate
        );
    }
}
```

## Common MAVLink Commands for Rover

### Navigation Commands

| Command | Description | Parameters |
|---------|-------------|------------|
| `MAV_CMD_NAV_WAYPOINT` | Go to waypoint | lat, lon, alt |
| `MAV_CMD_NAV_RETURN_TO_LAUNCH` | RTL | - |
| `MAV_CMD_NAV_LOITER_UNLIM` | Loiter forever | radius |
| `MAV_CMD_NAV_SET_YAW_SPEED` | Heading + speed | yaw, speed, type |
| `MAV_CMD_DO_SET_HOME` | Set home | current, lat, lon |

### Mode Commands

| Command | Description | Parameters |
|---------|-------------|------------|
| `MAV_CMD_DO_SET_MODE` | Change mode | mode_id |
| `MAV_CMD_MISSION_START` | Start mission | - |
| `MAV_CMD_NAV_GUIDED_ENABLE` | Enable guided | enable |

### Speed Commands

| Command | Description | Parameters |
|---------|-------------|------------|
| `MAV_CMD_DO_CHANGE_SPEED` | Change speed | type, speed, throttle |
| `MAV_CMD_DO_SET_REVERSE` | Set reverse | reverse |

## Sending Messages from Rover

```cpp
// Send status text
gcs().send_text(MAV_SEVERITY_INFO, "Mode changed to Auto");

// Send named float
gcs().send_named_float("distance", distance_m);

// Send parameter value
gcs().send_parameter_value(param_name, AP_Param::cast_to_float(value));
```

## MAVLink Streaming Configuration

```cpp
// In Rover/GCS_MAVLink_Rover.cpp
static const ap_message STREAM_RAW_SENSORS_msgs[] = {
    MSG_RAW_IMU,
    MSG_SCALED_PRESSURE,
    // ...
};

static const ap_message STREAM_EXTENDED_STATUS_msgs[] = {
    MSG_SYS_STATUS,
    MSG_POWER_STATUS,
    MSG_NAV_CONTROLLER_OUTPUT,
    // ...
};

// Configure via SRn_* parameters
// SR0_RAW_SENS, SR0_EXT_STAT, etc.
```

## Custom Message Example

### Adding a New Handler

```cpp
// 1. In handle_message(), add case
case MAVLINK_MSG_ID_MY_CUSTOM_MSG:
    handle_my_custom_msg(msg);
    break;

// 2. Implement handler
void GCS_MAVLINK_Rover::handle_my_custom_msg(const mavlink_message_t &msg) {
    mavlink_my_custom_msg_t packet;
    mavlink_msg_my_custom_msg_decode(&msg, &packet);

    // Process packet
    rover.process_custom_data(packet.field1, packet.field2);
}
```

### Adding a New Telemetry Message

```cpp
// 1. Add to streaming setup in GCS_Rover.cpp
void GCS_Rover::update_vehicle_sensor_status_flags() {
    // ...
}

// 2. Add send method
void GCS_MAVLINK_Rover::send_my_telemetry() const {
    mavlink_msg_my_telemetry_send(
        chan,
        rover.get_my_value1(),
        rover.get_my_value2()
    );
}

// 3. Register for streaming
static const ap_message MY_STREAM_msgs[] = {
    MSG_MY_TELEMETRY,
};
```
