# MAVLink Messages

Handling incoming messages and sending outgoing messages.

## Receiving Messages

### Message Dispatch

Messages are dispatched through `handle_message()`:

```cpp
// In GCS_MAVLINK::handle_message() - libraries/GCS_MAVLink/GCS_Common.cpp
void GCS_MAVLINK::handle_message(const mavlink_message_t &msg) {
    switch (msg.msgid) {
        case MAVLINK_MSG_ID_HEARTBEAT:
            handle_heartbeat(msg);
            break;
        case MAVLINK_MSG_ID_PARAM_REQUEST_LIST:
            handle_param_request_list(msg);
            break;
        // ... more common messages
        default:
            break;
    }
}
```

### Vehicle-Specific Override

```cpp
// In ArduCopter/GCS_Mavlink.cpp
void GCS_MAVLINK_Copter::handle_message(const mavlink_message_t &msg) {
    switch (msg.msgid) {
        case MAVLINK_MSG_ID_SET_POSITION_TARGET_LOCAL_NED:
            handle_set_position_target_local_ned(msg);
            break;
        case MAVLINK_MSG_ID_SET_ATTITUDE_TARGET:
            handle_set_attitude_target(msg);
            break;
        default:
            GCS_MAVLINK::handle_message(msg);  // Call parent
            break;
    }
}
```

### Parsing Message Data

```cpp
void GCS_MAVLINK::handle_set_home(const mavlink_message_t &msg) {
    mavlink_set_home_position_t packet;
    mavlink_msg_set_home_position_decode(&msg, &packet);

    // Use packet.latitude, packet.longitude, etc.
    Location loc;
    loc.lat = packet.latitude;
    loc.lng = packet.longitude;
    loc.alt = packet.altitude / 10;  // mm to cm
}
```

---

## Sending Messages

### Direct Send

```cpp
// Check space and send
if (HAVE_PAYLOAD_SPACE(chan, HEARTBEAT)) {
    mavlink_msg_heartbeat_send(
        chan,
        MAV_TYPE_QUADROTOR,
        MAV_AUTOPILOT_ARDUPILOTMEGA,
        base_mode,
        custom_mode,
        system_status
    );
}

// Alternative with CHECK macro (returns false if no space)
CHECK_PAYLOAD_SIZE(ATTITUDE);
mavlink_msg_attitude_send(chan, ...);
```

### Space Checking Macros

```cpp
// Check if message fits in TX buffer
HAVE_PAYLOAD_SPACE(chan, MESSAGE_NAME)  // Returns bool

// Check and return false if no space
CHECK_PAYLOAD_SIZE(MESSAGE_NAME)        // For methods returning bool

// Check and return void if no space
CHECK_PAYLOAD_SIZE2_VOID(chan, MESSAGE_NAME)
```

### Queued Sending via ap_message

For messages that should be sent at configured rates:

```cpp
// Queue a message for sending
void GCS_MAVLINK::send_message(ap_message id);

// Example: queue attitude for next send cycle
send_message(MSG_ATTITUDE);
```

### ap_message Enum

Defined in `libraries/GCS_MAVLink/ap_message.h`:

```cpp
enum ap_message : uint8_t {
    MSG_HEARTBEAT = 0,
    MSG_ATTITUDE = 3,
    MSG_LOCATION = 5,
    MSG_SYS_STATUS = 7,
    MSG_GPS_RAW = 22,
    MSG_BATTERY_STATUS = 65,
    // ... see ap_message.h for full list
    MSG_LAST
};
```

### try_send_message Pattern

Override to handle vehicle-specific messages:

```cpp
bool GCS_MAVLINK_Copter::try_send_message(ap_message id) {
    switch (id) {
        case MSG_WIND:
            CHECK_PAYLOAD_SIZE(WIND);
            send_wind();
            break;
        default:
            return GCS_MAVLINK::try_send_message(id);
    }
    return true;
}
```

---

## Common Send Functions

Built-in send functions in GCS_MAVLINK:

```cpp
// Status
void send_heartbeat();
void send_sys_status();
void send_power_status();
void send_battery_status(uint8_t instance);

// Attitude/Position
void send_attitude();
void send_attitude_quaternion();
void send_global_position_int();
void send_local_position();
void send_vfr_hud();

// Sensors
void send_raw_imu();
void send_scaled_pressure();
void send_distance_sensor();
void send_opticalflow();

// Navigation
void send_nav_controller_output();  // Pure virtual - vehicle must implement
void send_mission_current(AP_Mission &mission, uint16_t seq);

// System
void send_autopilot_version();
void send_home_position();
void send_gps_global_origin();
```

---

## Sending Text Messages

```cpp
// From anywhere via global macro
GCS_SEND_TEXT(MAV_SEVERITY_INFO, "Motor %d failed", motor_num);

// From GCS_MAVLINK method
send_text(MAV_SEVERITY_WARNING, "Battery low: %.1fV", voltage);

// From GCS singleton
gcs().send_text(MAV_SEVERITY_ERROR, "Critical failure");

// Severity levels
MAV_SEVERITY_EMERGENCY  // 0 - System unusable
MAV_SEVERITY_ALERT      // 1 - Immediate action required
MAV_SEVERITY_CRITICAL   // 2 - Critical conditions
MAV_SEVERITY_ERROR      // 3 - Error conditions
MAV_SEVERITY_WARNING    // 4 - Warning conditions
MAV_SEVERITY_NOTICE     // 5 - Normal but significant
MAV_SEVERITY_INFO       // 6 - Informational
MAV_SEVERITY_DEBUG      // 7 - Debug messages
```

---

## Thread Safety

When sending from non-main threads:

```cpp
// Get channel lock
HAL_Semaphore &lock = comm_chan_lock(chan);

{
    WITH_SEMAPHORE(lock);
    mavlink_msg_named_value_float_send(chan, AP_HAL::millis(), "myvalue", value);
}
```

---

## Broadcast vs Targeted

```cpp
// Send to all active channels
gcs().send_message(MSG_ATTITUDE);

// Send to specific channel
GCS_MAVLINK *link = gcs().chan(0);
if (link != nullptr) {
    link->send_message(MSG_ATTITUDE);
}

// Send to components (via routing)
GCS_MAVLINK::send_to_components(MAVLINK_MSG_ID_COMMAND_ACK, (char*)&ack, sizeof(ack));
```
