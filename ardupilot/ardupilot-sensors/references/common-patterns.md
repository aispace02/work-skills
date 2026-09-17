# Common ArduPilot Sensor Patterns

This document covers architecture patterns common to all ArduPilot sensor libraries.

## Singleton Access Pattern

All sensor libraries use singletons accessed via the `AP::` namespace:

```cpp
// Standard access pattern
AP_GPS &gps = AP::gps();
AP_Baro &baro = AP::baro();
AP_AHRS &ahrs = AP::ahrs();

// Pointer access (for optional sensors)
RangeFinder *rf = AP::rangefinder();
AP_Proximity *prx = AP::proximity();
if (rf != nullptr) {
    // Use rangefinder
}
```

### Common Singletons

| Library | Singleton |
|---------|-----------|
| AP_InertialSensor | `AP::ins()` |
| AP_GPS | `AP::gps()` |
| Compass | `AP::compass()` |
| AP_Baro | `AP::baro()` |
| RangeFinder | `AP::rangefinder()` |
| AP_Airspeed | `AP::airspeed()` |
| AP_OpticalFlow | `AP::opticalflow()` |
| AP_BattMonitor | `AP::battery()` |
| AP_Proximity | `AP::proximity()` |
| AP_AHRS | `AP::ahrs()` |
| AP_Beacon | `AP::beacon()` |
| AP_VisualOdom | `AP::visualodom()` |

---

## Frontend/Backend Architecture

Most sensor libraries separate the API (frontend) from hardware drivers (backends).

```
┌─────────────────────────────────────────────┐
│             Vehicle Code                     │
│         (Copter, Plane, Rover)              │
└─────────────────┬───────────────────────────┘
                  │ Uses API
                  ▼
┌─────────────────────────────────────────────┐
│           Frontend (e.g., AP_GPS)            │
│  - Public API methods                        │
│  - Multi-instance management                 │
│  - Backend selection                         │
│  - Data aggregation                          │
└─────────────────┬───────────────────────────┘
                  │ Calls backends
                  ▼
┌─────────────────────────────────────────────┐
│     Backend (e.g., AP_GPS_UBLOX)             │
│  - Hardware-specific communication           │
│  - Protocol parsing                          │
│  - Fills state structures                    │
└─────────────────────────────────────────────┘
```

### Adding a New Backend

1. Create backend class inheriting from `*_Backend`:
```cpp
class AP_RangeFinder_NewSensor : public AP_RangeFinder_Backend {
public:
    AP_RangeFinder_NewSensor(RangeFinder::RangeFinder_State &_state,
                              AP_RangeFinder_Params &_params);
    void update() override;

private:
    // Hardware communication
};
```

2. Register in frontend's `detect_instance()`:
```cpp
case Type::NewSensor:
    driver = new AP_RangeFinder_NewSensor(state[i], params[i]);
    break;
```

3. Add to type enum and parameter table.

---

## Multi-Instance Pattern

Sensors support multiple instances with indexed access:

```cpp
// Instance count
uint8_t num = gps.num_sensors();

// Indexed access
for (uint8_t i = 0; i < num; i++) {
    if (gps.status(i) >= AP_GPS::GPS_OK_FIX_3D) {
        Location loc = gps.location(i);
    }
}

// Primary instance (usually 0 or auto-selected)
Location loc = gps.location();  // Uses primary
```

### Primary Selection

Most sensors auto-select the primary instance based on:
- Health status
- Data quality
- Configuration (e.g., `GPS_PRIMARY` parameter)

---

## Health Checking Pattern

Standard health/status checking:

```cpp
// Boolean health
if (baro.healthy()) {
    float alt = baro.get_altitude();
}

// Per-instance health
for (uint8_t i = 0; i < baro.num_instances(); i++) {
    if (baro.healthy(i)) {
        float pressure = baro.get_pressure(i);
    }
}

// Status enum (more detailed)
if (gps.status() >= AP_GPS::GPS_OK_FIX_3D) {
    // 3D fix
}

// Pre-arm checks
char msg[50];
if (!rf->prearm_healthy(msg, sizeof(msg))) {
    // msg contains failure reason
}
```

---

## Update Pattern

Sensors require periodic updates, typically called from the scheduler:

```cpp
// In scheduler table
SCHED_TASK(update_GPS,        50,  200),
SCHED_TASK(update_compass,   100,  200),
SCHED_TASK(barometer_update, 100,  200),

// Update implementation
void Copter::update_GPS() {
    gps.update();
}
```

### Update Rates

| Sensor | Typical Rate |
|--------|--------------|
| IMU | 400-8000 Hz (handled by AP_InertialSensor) |
| GPS | 5-50 Hz |
| Baro | 50-100 Hz |
| Compass | 100 Hz |
| Rangefinder | 50-100 Hz |
| Optical Flow | 10-100 Hz |
| Battery | 10 Hz |

---

## Thread Safety

Sensor backends often run in separate threads. Use semaphores for safe access:

```cpp
// Backend thread fills data
{
    WITH_SEMAPHORE(_sem);
    _state.distance = new_reading;
    _state.status = Status::Good;
}

// Frontend reads data
bool RangeFinder::get_reading(uint8_t instance, float &distance) {
    WITH_SEMAPHORE(_sem);
    if (state[instance].status == Status::Good) {
        distance = state[instance].distance;
        return true;
    }
    return false;
}
```

### WITH_SEMAPHORE Macro

```cpp
// Acquires semaphore on entry, releases on scope exit
{
    WITH_SEMAPHORE(sem);
    // Protected code
}  // Semaphore auto-released
```

---

## Parameter Pattern

Sensors use AP_Param for configuration:

```cpp
// In header
AP_Int8 _type;
AP_Float _scale;

// In var_info
// @Param: TYPE
// @DisplayName: Sensor Type
// @Values: 0:None,1:Analog,2:Digital
const AP_Param::GroupInfo AP_Sensor::var_info[] = {
    // @Param: TYPE
    AP_GROUPINFO("TYPE", 0, AP_Sensor, _type, 0),

    // @Param: SCALE
    AP_GROUPINFO("SCALE", 1, AP_Sensor, _scale, 1.0f),

    AP_GROUPEND
};
```

### Multi-Instance Parameters

Use indexed parameters with prefix substitution:

```cpp
// GPS1_, GPS2_, etc.
AP_SUBGROUPINFO(params[0], "1_", 1, AP_GPS, AP_GPS_Params),
AP_SUBGROUPINFO(params[1], "2_", 2, AP_GPS, AP_GPS_Params),
```

---

## Calibration Pattern

Many sensors support runtime calibration:

```cpp
// Trigger calibration
compass.start_calibration_all();
compass.set_and_save_offsets(0, offsets);

// Blocking calibration (e.g., on startup)
baro.calibrate(true);  // true = save to EEPROM

// Background calibration (non-blocking)
ins.acal_init();  // Start accel cal
ins.acal_update();  // Call periodically
```

---

## Logging Pattern

Sensors log data using the DataFlash library:

```cpp
// In update loop
void AP_GPS::update() {
    // ... update logic ...

#if HAL_LOGGING_ENABLED
    Write_GPS(0);  // Log instance 0
#endif
}

// Log message format
void AP_GPS::Write_GPS(uint8_t i) {
    AP::logger().Write("GPS", "TimeUS,Status,GMS,GWk,NSats,HDop,Lat,Lng,Alt,Spd,GCrs,VZ,U",
        "s-ssnmDUmnnnn",
        "F-F--00B00000",
        "QBIHBcLLefffff",
        AP_HAL::micros64(),
        (uint8_t)status(i),
        // ... fields ...
    );
}
```

---

## MAVLink Integration

Sensors integrate with MAVLink for GCS communication:

```cpp
// Sending messages
void GCS_MAVLINK::send_gps_raw(AP_GPS &gps) {
    mavlink_msg_gps_raw_int_send(chan,
        gps.time_epoch_usec(),
        gps.status(),
        // ... fields ...
    );
}

// Receiving messages
void GCS_MAVLINK::handle_common_message(mavlink_message_t &msg) {
    switch (msg.msgid) {
        case MAVLINK_MSG_ID_GPS_INPUT:
            gps.handle_msg(msg);
            break;
    }
}
```

---

## Quick Reference: Adding Sensor Support

1. **Read existing sensor** - Understand the API you'll use
2. **Check if supported** - Many sensors have existing backends
3. **Check configuration** - Ensure sensor type is enabled in build
4. **Set parameters** - Configure via GCS or param file
5. **Call in scheduler** - Add update calls if not already present
6. **Access via singleton** - Use `AP::sensor_name()`
7. **Check health** - Always verify `healthy()` before using data
