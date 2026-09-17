---
name: ardupilot-comms
description: |
  ArduPilot communication libraries (GCS_MAVLink, AP_SerialManager, MAVLink routing,
  telemetry protocols). Use when:
  (1) Working on GCS_MAVLink or MAVLink message handling
  (2) Adding new MAVLink messages or MAV_CMD commands
  (3) Configuring serial ports or streaming rates
  (4) Implementing parameter, mission, or fence protocols
  (5) Working with FrSky, CRSF, MSP, or other telemetry
  (6) Setting up network communication (TCP/UDP MAVLink)
  (7) Debugging communication or routing issues
---

# ArduPilot Communication Libraries

## Reference Lookup

| Topic | Reference |
|-------|-----------|
| GCS class hierarchy, channels, routing | [gcs-architecture.md](references/gcs-architecture.md) |
| Sending/receiving MAVLink messages | [mavlink-messages.md](references/mavlink-messages.md) |
| MAV_CMD handling, acknowledgment | [mavlink-commands.md](references/mavlink-commands.md) |
| Telemetry streaming, SRx_ params | [streaming.md](references/streaming.md) |
| Param/Mission/Fence/FTP protocols | [protocols.md](references/protocols.md) |
| Serial port configuration | [serial-manager.md](references/serial-manager.md) |
| FrSky, CRSF, MSP, LTM telemetry | [alt-telemetry.md](references/alt-telemetry.md) |
| TCP/UDP, network links | [networking.md](references/networking.md) |
| Adding messages/commands | [extending.md](references/extending.md) |

## Key Singletons

| Class | Accessor | Purpose |
|-------|----------|---------|
| GCS | `gcs()` | Multi-link GCS manager |
| AP_SerialManager | `AP::serialmanager()` | Serial port configuration |

## File Locations

| Library | Location |
|---------|----------|
| GCS_MAVLink | `libraries/GCS_MAVLink/` |
| AP_SerialManager | `libraries/AP_SerialManager/` |
| AP_Frsky_Telem | `libraries/AP_Frsky_Telem/` |
| AP_RCTelemetry | `libraries/AP_RCTelemetry/` |
| AP_MSP | `libraries/AP_MSP/` |
| AP_Networking | `libraries/AP_Networking/` |
| Vehicle GCS | `ArduCopter/GCS_Mavlink.cpp`, etc. |

## Quick Patterns

### Send a MAVLink message
```cpp
// Direct send (check space first)
if (HAVE_PAYLOAD_SPACE(chan, HEARTBEAT)) {
    mavlink_msg_heartbeat_send(chan, type, autopilot, base_mode, custom_mode, state);
}
```

### Handle incoming message
```cpp
// Override in vehicle's GCS_MAVLINK subclass
void GCS_MAVLINK_Copter::handle_message(const mavlink_message_t &msg) {
    switch (msg.msgid) {
        case MAVLINK_MSG_ID_MY_MESSAGE:
            handle_my_message(msg);
            break;
        default:
            GCS_MAVLINK::handle_message(msg);  // Call parent
            break;
    }
}
```

### Handle MAV_CMD command
```cpp
MAV_RESULT GCS_MAVLINK_Copter::handle_command_int_packet(const mavlink_command_int_t &packet, const mavlink_message_t &msg) {
    switch (packet.command) {
        case MAV_CMD_DO_SOMETHING:
            return handle_do_something(packet);
        default:
            return GCS_MAVLINK::handle_command_int_packet(packet, msg);
    }
}
```

### Send text to GCS
```cpp
GCS_SEND_TEXT(MAV_SEVERITY_INFO, "Hello %s", "World");
gcs().send_text(MAV_SEVERITY_WARNING, "Low battery");
```

### Find serial port for protocol
```cpp
AP_HAL::UARTDriver *uart = AP::serialmanager().find_serial(
    AP_SerialManager::SerialProtocol_GPS, 0);  // First GPS port
```
