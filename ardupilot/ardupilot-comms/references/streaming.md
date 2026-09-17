# Telemetry Streaming

Configuring and implementing telemetry data streams.

## Stream Rate Parameters

Each telemetry port has stream rate parameters (SRx_ where x is port number):

| Parameter | Stream | Messages Included |
|-----------|--------|-------------------|
| `SRx_RAW_SENS` | Raw sensors | RAW_IMU, SCALED_IMU, SCALED_PRESSURE |
| `SRx_EXT_STAT` | Extended status | SYS_STATUS, POWER_STATUS, MCU_STATUS, MEMINFO, GPS_RAW, GPS_RTK |
| `SRx_RC_CHAN` | RC channels | RC_CHANNELS, SERVO_OUTPUT_RAW |
| `SRx_RAW_CTRL` | Raw controller | (vehicle-specific) |
| `SRx_POSITION` | Position | GLOBAL_POSITION_INT, LOCAL_POSITION_NED |
| `SRx_EXTRA1` | Extra 1 | ATTITUDE, SIMSTATE |
| `SRx_EXTRA2` | Extra 2 | VFR_HUD |
| `SRx_EXTRA3` | Extra 3 | AHRS, SYSTEM_TIME, WIND, RANGEFINDER, DISTANCE_SENSOR |
| `SRx_PARAMS` | Parameters | PARAM_VALUE (during param download) |
| `SRx_ADSB` | ADSB | ADSB_VEHICLE |

### Rate Values

- **0**: Disabled
- **1-50**: Messages per second (Hz)
- **-1**: Use default rate from stream definition

---

## Stream Definitions

Defined per-vehicle in `GCS_Mavlink.cpp`:

```cpp
// Example from ArduCopter
static const ap_message STREAM_RAW_SENSORS_msgs[] = {
    MSG_RAW_IMU,
    MSG_SCALED_IMU2,
    MSG_SCALED_IMU3,
    MSG_SCALED_PRESSURE,
    MSG_SCALED_PRESSURE2,
    MSG_SCALED_PRESSURE3,
};

static const ap_message STREAM_EXTENDED_STATUS_msgs[] = {
    MSG_SYS_STATUS,
    MSG_POWER_STATUS,
    MSG_MCU_STATUS,
    MSG_MEMINFO,
    MSG_CURRENT_WAYPOINT,
    MSG_GPS_RAW,
    MSG_GPS_RTK,
    MSG_GPS2_RAW,
    MSG_GPS2_RTK,
    MSG_NAV_CONTROLLER_OUTPUT,
    MSG_FENCE_STATUS,
    MSG_POSITION_TARGET_GLOBAL_INT,
};

// All streams array
const GCS_MAVLINK::stream_entries GCS_MAVLINK::all_stream_entries[] = {
    { STREAM_RAW_SENSORS, STREAM_RAW_SENSORS_msgs, ARRAY_SIZE(STREAM_RAW_SENSORS_msgs) },
    { STREAM_EXTENDED_STATUS, STREAM_EXTENDED_STATUS_msgs, ARRAY_SIZE(STREAM_EXTENDED_STATUS_msgs) },
    // ... more streams
    { (streams)0, nullptr, 0 }  // Terminator
};
```

---

## Message Sending

### Deferred Message System

Messages are queued in buckets and sent when bandwidth allows:

```cpp
// Queue message for deferred sending
void GCS_MAVLINK::send_message(ap_message id) {
    // Adds to bucket based on message type and rate
}

// Called periodically to send queued messages
void GCS_MAVLINK::update_send() {
    // Sends messages from buckets based on rate and available space
}
```

### try_send_message Pattern

Override to implement message sending:

```cpp
bool GCS_MAVLINK_Copter::try_send_message(ap_message id) {
    switch (id) {
        case MSG_ATTITUDE:
            CHECK_PAYLOAD_SIZE(ATTITUDE);
            send_attitude();
            break;

        case MSG_LOCATION:
            CHECK_PAYLOAD_SIZE(GLOBAL_POSITION_INT);
            send_global_position_int();
            break;

        default:
            return GCS_MAVLINK::try_send_message(id);
    }
    return true;
}
```

---

## Setting Message Intervals

### Via MAV_CMD

```cpp
// MAV_CMD_SET_MESSAGE_INTERVAL
// param1: message_id (MAVLink message ID)
// param2: interval_us (microseconds, -1 to disable)
MAV_RESULT GCS_MAVLINK::handle_command_set_message_interval(const mavlink_command_int_t &packet) {
    return set_message_interval((uint32_t)packet.param1, (int32_t)packet.param2);
}
```

### Programmatically

```cpp
// Set interval for specific MAVLink message ID
MAV_RESULT result = set_message_interval(MAVLINK_MSG_ID_ATTITUDE, 100000);  // 100ms = 10Hz

// Set interval for ap_message
bool set_ap_message_interval(ap_message id, uint16_t interval_ms);
```

### Query Current Interval

```cpp
// MAV_CMD_GET_MESSAGE_INTERVAL returns interval in COMMAND_ACK.result_param2
bool get_ap_message_interval(ap_message id, uint16_t &interval_ms);
```

---

## Stream Slowdown

When telemetry bandwidth is limited (e.g., low RSSI), streaming is automatically slowed:

```cpp
// Get current slowdown
uint16_t slowdown_ms = get_stream_slowdown_ms();

// Applied to bucket reschedule interval
uint16_t get_reschedule_interval_ms(const deferred_message_bucket_t &deferred) {
    return deferred.interval_ms + stream_slowdown_ms;
}
```

Slowdown is calculated from RADIO_STATUS message txbuf field.

---

## Sending to All Channels

```cpp
// Send to all active, non-private channels
gcs().send_message(MSG_ATTITUDE);

// Implementation iterates channels
void GCS::send_message(ap_message id) {
    for (uint8_t i = 0; i < num_gcs(); i++) {
        GCS_MAVLINK *link = chan(i);
        if (link != nullptr && link->is_active()) {
            link->send_message(id);
        }
    }
}
```

---

## Named Values

For custom telemetry without defining new messages:

```cpp
// Send named float
gcs().send_named_float("myvalue", 123.45f);

// Sends NAMED_VALUE_FLOAT message
// name: up to 10 chars
// value: float

// Or from GCS_MAVLINK instance
send_named_float("rpm", motor_rpm);
```

---

## High Latency Mode

For satellite/LoRa links with very limited bandwidth:

```cpp
// Enable via MAV_CMD_CONTROL_HIGH_LATENCY
// Sends HIGH_LATENCY2 message with condensed telemetry

// Check if high latency link
if (is_high_latency_link) {
    // Use minimal bandwidth
}
```

Parameters:
- `HL_ID` - High Latency link instance
- HIGH_LATENCY2 message sent at 0.2Hz typical
