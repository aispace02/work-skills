# Extending MAVLink

Adding new MAVLink messages and commands.

## Adding a New MAVLink Message

### Step 1: Define Message in XML

Edit `libraries/GCS_MAVLink/message_definitions/v1.0/ardupilotmega.xml`:

```xml
<message id="12345" name="MY_NEW_MESSAGE">
  <description>My new message description</description>
  <field type="uint32_t" name="time_boot_ms">Timestamp (ms)</field>
  <field type="float" name="value1">First value</field>
  <field type="float" name="value2">Second value</field>
  <field type="uint8_t" name="status">Status flags</field>
</message>
```

### Step 2: Regenerate Headers

```bash
cd libraries/GCS_MAVLink
python3 pymavlink/generator/mavgen.py \
    --lang=C \
    --wire-protocol=2.0 \
    --output=include/mavlink/v2.0 \
    message_definitions/v1.0/all.xml
```

Or use the convenience script:

```bash
./libraries/GCS_MAVLink/generate.sh
```

### Step 3: Add ap_message Entry (if streaming)

In `libraries/GCS_MAVLink/ap_message.h`:

```cpp
enum ap_message : uint8_t {
    // ... existing messages ...
    MSG_MY_NEW_MESSAGE = XX,  // Use next available number
    MSG_LAST
};
```

### Step 4: Implement Send Function

In `libraries/GCS_MAVLink/GCS_Common.cpp` or vehicle code:

```cpp
void GCS_MAVLINK::send_my_new_message() {
    mavlink_msg_my_new_message_send(
        chan,
        AP_HAL::millis(),
        some_value1,
        some_value2,
        status_flags
    );
}
```

### Step 5: Add to try_send_message

```cpp
bool GCS_MAVLINK::try_send_message(ap_message id) {
    switch (id) {
        // ... existing cases ...

        case MSG_MY_NEW_MESSAGE:
            CHECK_PAYLOAD_SIZE(MY_NEW_MESSAGE);
            send_my_new_message();
            break;
    }
    return true;
}
```

### Step 6: Add to Stream (optional)

In vehicle's `GCS_Mavlink.cpp`:

```cpp
static const ap_message STREAM_EXTRA3_msgs[] = {
    // ... existing messages ...
    MSG_MY_NEW_MESSAGE,
};
```

---

## Adding a New MAV_CMD Command

### Step 1: Define Command in XML

Edit `message_definitions/v1.0/common.xml` or `ardupilotmega.xml`:

```xml
<enum name="MAV_CMD">
  <!-- ... existing commands ... -->
  <entry value="43001" name="MAV_CMD_MY_NEW_COMMAND">
    <description>My new command description</description>
    <param index="1">First parameter</param>
    <param index="2">Second parameter</param>
    <param index="3" reserved="true"/>
    <param index="4" reserved="true"/>
    <param index="5">X coordinate (if location)</param>
    <param index="6">Y coordinate (if location)</param>
    <param index="7">Z coordinate (altitude)</param>
  </entry>
</enum>
```

### Step 2: Regenerate Headers

Same as for messages.

### Step 3: Implement Handler

In vehicle's `GCS_Mavlink.cpp`:

```cpp
MAV_RESULT GCS_MAVLINK_Copter::handle_command_int_packet(
    const mavlink_command_int_t &packet,
    const mavlink_message_t &msg)
{
    switch (packet.command) {
        // ... existing commands ...

        case MAV_CMD_MY_NEW_COMMAND:
            return handle_my_new_command(packet);

        default:
            return GCS_MAVLINK::handle_command_int_packet(packet, msg);
    }
}

MAV_RESULT GCS_MAVLINK_Copter::handle_my_new_command(
    const mavlink_command_int_t &packet)
{
    float param1 = packet.param1;
    float param2 = packet.param2;

    // Validate parameters
    if (param1 < 0 || param1 > 100) {
        return MAV_RESULT_DENIED;
    }

    // Execute command
    if (!copter.do_my_action(param1, param2)) {
        return MAV_RESULT_FAILED;
    }

    return MAV_RESULT_ACCEPTED;
}
```

---

## Handling New Incoming Message

### Step 1: Add to handle_message

In vehicle's `GCS_Mavlink.cpp`:

```cpp
void GCS_MAVLINK_Copter::handle_message(const mavlink_message_t &msg) {
    switch (msg.msgid) {
        // ... existing cases ...

        case MAVLINK_MSG_ID_MY_NEW_MESSAGE:
            handle_my_new_message(msg);
            break;

        default:
            GCS_MAVLINK::handle_message(msg);
            break;
    }
}
```

### Step 2: Implement Handler

```cpp
void GCS_MAVLINK_Copter::handle_my_new_message(const mavlink_message_t &msg) {
    mavlink_my_new_message_t packet;
    mavlink_msg_my_new_message_decode(&msg, &packet);

    // Use packet.value1, packet.value2, etc.
    copter.process_my_data(packet.value1, packet.value2);
}
```

---

## Common Message Patterns

### Request/Response

```cpp
// Requester sends REQUEST message
// Responder handles and sends DATA message

void GCS_MAVLINK::handle_my_request(const mavlink_message_t &msg) {
    mavlink_my_request_t request;
    mavlink_msg_my_request_decode(&msg, &request);

    // Send response
    mavlink_msg_my_data_send(chan,
        request.request_id,
        data1,
        data2);
}
```

### Periodic Updates

```cpp
// Add to stream definition
static const ap_message STREAM_EXTRA1_msgs[] = {
    MSG_ATTITUDE,
    MSG_MY_STATUS,  // Sent at EXTRA1 rate
};
```

---

## Message ID Ranges

| Range | Dialect |
|-------|---------|
| 0-149 | Common (cross-platform) |
| 150-219 | ArduPilotMega specific |
| 220-255 | Reserved |
| 256+ | Extended (MAVLink 2) |

Use IDs in ArduPilot range (150-219) or extended range (12000-12999 suggested for custom).

---

## Testing New Messages

### SITL

```bash
# Run SITL
sim_vehicle.py -v ArduCopter

# In MAVProxy, send command
command_int 0 0 0 MAV_CMD_MY_NEW_COMMAND 0 0 param1 param2 0 0 0 0 0
```

### Python Test

```python
from pymavlink import mavutil

mav = mavutil.mavlink_connection('udp:127.0.0.1:14550')

# Send custom message
mav.mav.my_new_message_send(
    mav.target_system,
    mav.target_component,
    value1,
    value2,
    status
)

# Receive custom message
msg = mav.recv_match(type='MY_NEW_MESSAGE', blocking=True)
print(msg.value1, msg.value2)
```

---

## Checklist

- [ ] XML message/command definition added
- [ ] Headers regenerated (`./generate.sh`)
- [ ] ap_message enum updated (if streaming)
- [ ] Send function implemented
- [ ] Handler implemented (for incoming)
- [ ] Added to try_send_message (if streaming)
- [ ] Added to stream definition (if periodic)
- [ ] Tested in SITL
- [ ] Documentation updated
