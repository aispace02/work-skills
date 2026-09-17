# MAVLink Protocols

Standard MAVLink microservices: Parameter, Mission, Fence, Rally, and FTP.

## Parameter Protocol

### Download All Parameters

```
GCS                         Vehicle
 |-- PARAM_REQUEST_LIST ------->|
 |<------ PARAM_VALUE ----------| (repeated for each param)
 |<------ PARAM_VALUE ----------|
 |          ...                 |
```

### Read Single Parameter

```
GCS                         Vehicle
 |-- PARAM_REQUEST_READ ------->|
 |<------ PARAM_VALUE ----------|
```

### Set Parameter

```
GCS                         Vehicle
 |-- PARAM_SET ---------------->|
 |<------ PARAM_VALUE ----------| (confirms new value)
```

### Handling Code

```cpp
void GCS_MAVLINK::handle_param_request_list(const mavlink_message_t &msg) {
    // Queue all parameters for sending
    _queued_parameter = AP_Param::first(&_queued_parameter_token, &_queued_parameter_type);
    _queued_parameter_index = 0;
    _queued_parameter_count = AP_Param::count_parameters();
}

void GCS_MAVLINK::handle_param_set(const mavlink_message_t &msg) {
    mavlink_param_set_t packet;
    mavlink_msg_param_set_decode(&msg, &packet);

    // Find and set parameter
    AP_Param *vp = AP_Param::find(packet.param_id, &ptype);
    if (vp != nullptr) {
        vp->set_float(packet.param_value, ptype);
        // Send confirmation
        send_parameter_value(packet.param_id, ptype, vp->get_float());
    }
}
```

---

## Mission Protocol

**Class**: `MissionItemProtocol_Waypoints`
**Location**: `libraries/GCS_MAVLink/MissionItemProtocol_Waypoints.h`

### Download Mission

```
GCS                         Vehicle
 |-- MISSION_REQUEST_LIST ----->|
 |<---- MISSION_COUNT ----------|
 |-- MISSION_REQUEST_INT ------>| (for item 0)
 |<---- MISSION_ITEM_INT -------|
 |-- MISSION_REQUEST_INT ------>| (for item 1)
 |<---- MISSION_ITEM_INT -------|
 |          ...                 |
 |-- MISSION_ACK -------------->| (download complete)
```

### Upload Mission

```
GCS                         Vehicle
 |-- MISSION_COUNT ------------>|
 |<---- MISSION_REQUEST_INT ----| (for item 0)
 |-- MISSION_ITEM_INT --------->|
 |<---- MISSION_REQUEST_INT ----| (for item 1)
 |-- MISSION_ITEM_INT --------->|
 |          ...                 |
 |<---- MISSION_ACK ------------| (upload complete)
```

### Mission Types

```cpp
enum MAV_MISSION_TYPE {
    MAV_MISSION_TYPE_MISSION = 0,  // Regular waypoints
    MAV_MISSION_TYPE_FENCE = 1,    // Geofence
    MAV_MISSION_TYPE_RALLY = 2,    // Rally points
    MAV_MISSION_TYPE_ALL = 255,    // All types
};
```

### Implementation

```cpp
// Get protocol handler for mission type
MissionItemProtocol *proto = gcs().get_prot_for_mission_type(MAV_MISSION_TYPE_MISSION);

// Protocol handles message dispatch
void GCS_MAVLINK::handle_common_mission_message(const mavlink_message_t &msg) {
    MissionItemProtocol *prot = gcs().get_prot_for_mission_type(mission_type);
    if (prot != nullptr) {
        prot->handle_mission_message(*this, msg);
    }
}
```

---

## Fence Protocol

**Class**: `MissionItemProtocol_Fence`
**Location**: `libraries/GCS_MAVLink/MissionItemProtocol_Fence.h`

Uses same protocol as Mission but with `MAV_MISSION_TYPE_FENCE`.

```cpp
// Fence message handling in handle_fence_message()
void GCS_MAVLINK::handle_fence_message(const mavlink_message_t &msg) {
    switch (msg.msgid) {
        case MAVLINK_MSG_ID_FENCE_POINT:
            handle_fence_point(msg);
            break;
        case MAVLINK_MSG_ID_FENCE_FETCH_POINT:
            handle_fence_fetch_point(msg);
            break;
    }
}
```

---

## Rally Protocol

**Class**: `MissionItemProtocol_Rally`
**Location**: `libraries/GCS_MAVLink/MissionItemProtocol_Rally.h`

Uses same protocol as Mission but with `MAV_MISSION_TYPE_RALLY`.

Rally points are alternate landing locations for failsafe.

---

## FTP Protocol

**Class**: `GCS_FTP`
**Location**: `libraries/GCS_MAVLink/GCS_FTP.h`

File transfer over MAVLink for parameter files, logs, etc.

### Operations

```cpp
enum FTP_OP {
    kCmdNone = 0,
    kCmdTerminateSession = 1,
    kCmdResetSessions = 2,
    kCmdListDirectory = 3,
    kCmdOpenFileRO = 4,
    kCmdReadFile = 5,
    kCmdCreateFile = 6,
    kCmdWriteFile = 7,
    kCmdRemoveFile = 8,
    kCmdCreateDirectory = 9,
    kCmdRemoveDirectory = 10,
    kCmdOpenFileWO = 11,
    kCmdTruncateFile = 12,
    kCmdRename = 13,
    kCmdCalcFileCRC32 = 14,
    kCmdBurstReadFile = 15,
};
```

### Handling

```cpp
// FTP is handled via FILE_TRANSFER_PROTOCOL message
void GCS_MAVLINK::handle_file_transfer_protocol(const mavlink_message_t &msg) {
#if AP_MAVLINK_FTP_ENABLED
    ftp.handle_message(*this, msg);
#endif
}
```

---

## Mission Item Reached

Sent when vehicle reaches a waypoint:

```cpp
// Queue sending when waypoint reached
gcs().send_mission_item_reached_message(mission_index);

// Sends MISSION_ITEM_REACHED message
void GCS::send_mission_item_reached_message(uint16_t mission_index) {
    for (uint8_t i = 0; i < num_gcs(); i++) {
        chan(i)->mission_item_reached_index = mission_index;
        chan(i)->send_message(MSG_MISSION_ITEM_REACHED);
    }
}
```

---

## Mission Current

Sent when current waypoint changes:

```cpp
void GCS_MAVLINK::send_mission_current(const AP_Mission &mission, uint16_t seq) {
    CHECK_PAYLOAD_SIZE2_VOID(chan, MISSION_CURRENT);

    mavlink_msg_mission_current_send(
        chan,
        seq,                              // seq
        mission.get_item_count(),         // total
        mission_state(mission),           // mission_state
        mission.get_mission_id(),         // mission_id (CRC32)
        fence_mission_id(),               // fence_id
        rally_mission_id()                // rally_id
    );
}
```

---

## Command Protocol

For immediate commands (not waypoints), uses COMMAND_INT/COMMAND_LONG:

```
GCS                         Vehicle
 |-- COMMAND_INT/LONG --------->|
 |<---- COMMAND_ACK ------------|
```

For long-running commands:

```
GCS                         Vehicle
 |-- COMMAND_INT ----------------->|
 |<---- COMMAND_ACK (IN_PROGRESS) -|
 |          ...                    | (command executing)
 |<---- COMMAND_ACK (ACCEPTED) ----| (command complete)
```

See [mavlink-commands.md](mavlink-commands.md) for details.
