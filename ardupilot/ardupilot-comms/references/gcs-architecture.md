# GCS Architecture

The GCS (Ground Control Station) communication system uses a hierarchical design with a frontend managing multiple link backends.

## Class Hierarchy

```
GCS (singleton)                      # Multi-link manager
├── GCS_MAVLINK (per-link)           # Base per-link handler
│   ├── GCS_MAVLINK_Copter          # Vehicle-specific overrides
│   ├── GCS_MAVLINK_Plane
│   ├── GCS_MAVLINK_Rover
│   └── GCS_MAVLINK_Sub
└── MAVLink_routing                  # Message routing between links
```

## GCS Class (Singleton)

**Location**: `libraries/GCS_MAVLink/GCS.h`
**Accessor**: `gcs()`

Manages all GCS_MAVLINK instances and provides unified interface.

### Key Methods

```cpp
// Access channels
GCS_MAVLINK *chan(uint8_t ofs);      // Get channel by index
uint8_t num_gcs();                    // Number of active channels

// Sending
void send_message(ap_message id);     // Send to all active channels
void send_text(MAV_SEVERITY severity, const char *fmt, ...);
void send_named_float(const char *name, float value);

// Status
uint32_t sysid_mygcs_last_seen_time_ms();  // Last GCS traffic time
bool vehicle_initialised();

// Configuration
uint8_t sysid_this_mav();             // This vehicle's sysid (SYSID_THISMAV)
```

### Key Parameters

| Parameter | Description |
|-----------|-------------|
| `SYSID_THISMAV` | This vehicle's MAVLink system ID (1-255) |
| `SYSID_MYGCS` | Expected GCS system ID |

---

## GCS_MAVLINK Class (Per-Link)

**Location**: `libraries/GCS_MAVLink/GCS.h`

Handles MAVLink communication for a single channel/link.

### Key Methods

```cpp
// Initialization
bool init(uint8_t instance);

// Update (called from scheduler)
void update_receive(uint32_t max_time_us = 1000);
void update_send();

// Channel info
mavlink_channel_t get_chan();         // MAVLINK_COMM_0, etc.
bool is_active();
bool is_streaming();
uint16_t txspace();                   // Available TX buffer space

// Sending
void send_message(ap_message id);     // Queue message for sending
void send_text(MAV_SEVERITY severity, const char *fmt, ...);

// Message handling (override in vehicle subclass)
virtual void handle_message(const mavlink_message_t &msg);
virtual MAV_RESULT handle_command_int_packet(const mavlink_command_int_t &packet, const mavlink_message_t &msg);
```

### Stream Rates (SRx_ Parameters)

Each channel has configurable stream rates:

```cpp
enum streams : uint8_t {
    STREAM_RAW_SENSORS,      // SRx_RAW_SENS
    STREAM_EXTENDED_STATUS,  // SRx_EXT_STAT
    STREAM_RC_CHANNELS,      // SRx_RC_CHAN
    STREAM_RAW_CONTROLLER,   // SRx_RAW_CTRL
    STREAM_POSITION,         // SRx_POSITION
    STREAM_EXTRA1,           // SRx_EXTRA1
    STREAM_EXTRA2,           // SRx_EXTRA2
    STREAM_EXTRA3,           // SRx_EXTRA3
    STREAM_PARAMS,           // SRx_PARAMS
    STREAM_ADSB,             // SRx_ADSB
    NUM_STREAMS
};
```

---

## Channel Management

### Channel Masks

```cpp
// Get bitmask of active channels
mavlink_channel_mask_t active = GCS_MAVLINK::active_channel_mask();

// Check if channel is in mask
if (active & (1 << chan)) {
    // Channel is active
}

// Streaming channels
mavlink_channel_mask_t streaming = GCS_MAVLINK::streaming_channel_mask();

// Private channels (no forwarding/broadcast)
mavlink_channel_mask_t private_mask = GCS_MAVLINK::private_channel_mask();
```

### Channel Locking

```cpp
// Lock channel (prevent MAVLink use, e.g., for SERIAL_CONTROL)
chan->lock(true);

// Check if locked
if (chan->locked()) {
    return;
}
```

---

## MAVLink Routing

**Class**: `MAVLink_routing`
**Location**: `libraries/GCS_MAVLink/MAVLink_routing.h`

Routes messages between MAVLink channels based on target sysid/compid.

### Key Methods

```cpp
// Send to all components with this vehicle's sysid
static void send_to_components(uint32_t msgid, const char *pkt, uint8_t len);

// Find component by type
static bool find_by_mavtype(uint8_t mav_type, uint8_t &sysid, uint8_t &compid, mavlink_channel_t &chan);

// Disable routing on channel
static void disable_channel_routing(mavlink_channel_t chan);
```

---

## Vehicle Subclass Pattern

Each vehicle defines its own GCS_MAVLINK subclass:

```cpp
// In ArduCopter/GCS_Mavlink.h
class GCS_MAVLINK_Copter : public GCS_MAVLINK {
public:
    // Override message handling
    void handle_message(const mavlink_message_t &msg) override;

    // Override command handling
    MAV_RESULT handle_command_int_packet(const mavlink_command_int_t &packet,
                                          const mavlink_message_t &msg) override;

    // Vehicle-specific sends
    void send_nav_controller_output() const override;
    void send_pid_tuning() override;

protected:
    // Required overrides
    uint8_t base_mode() const override;
    MAV_STATE vehicle_system_status() const override;
};
```

### GCS Subclass

```cpp
// In ArduCopter/GCS_Copter.h
class GCS_Copter : public GCS {
public:
    // Define channel accessor with correct type
    GCS_MAVLINK_CHAN_METHOD_DEFINITIONS(GCS_MAVLINK_Copter);

protected:
    // Factory method
    GCS_MAVLINK *new_gcs_mavlink_backend(AP_HAL::UARTDriver &uart) override {
        return NEW_NOTHROW GCS_MAVLINK_Copter(uart);
    }

    // Vehicle-specific
    uint32_t custom_mode() const override;
    MAV_TYPE frame_type() const override;
};
```

---

## Initialization Flow

```cpp
// In vehicle setup()
void Copter::init_ardupilot() {
    // ...
    gcs().setup_console();  // Console UART
    gcs().setup_uarts();    // All other UARTs
    // ...
}

// In scheduler
void Copter::update_GCS() {
    gcs().update_receive();  // Process incoming
    gcs().update_send();     // Send queued messages
}
```
