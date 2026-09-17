# RangeFinder / Distance Sensors

RangeFinder provides distance measurements from lidar, sonar, and radar sensors.

## RangeFinder

**Location**: `libraries/AP_RangeFinder/`
**Singleton**: `AP::rangefinder()`

### Status Enum

```cpp
enum class Status {
    NotConnected = 0,
    NoData = 1,
    OutOfRangeLow = 2,
    OutOfRangeHigh = 3,
    Good = 4,
};
```

### Common Orientations

```cpp
ROTATION_NONE          // Forward (0°)
ROTATION_YAW_45        // Forward-Right
ROTATION_YAW_90        // Right
ROTATION_YAW_135       // Backward-Right
ROTATION_YAW_180       // Backward
ROTATION_YAW_225       // Backward-Left
ROTATION_YAW_270       // Left
ROTATION_YAW_315       // Forward-Left
ROTATION_PITCH_90      // Up
ROTATION_PITCH_270     // Down (most common for altitude)
```

### Core Methods

```cpp
// Initialization
void init(Rotation orientation = ROTATION_PITCH_270);
void update();                                // Update all rangefinders

// Multi-instance
uint8_t num_sensors();                        // Sensor count

// Distance by orientation (most common usage)
float distance_orient(Rotation rot);          // Distance (m)
Status status_orient(Rotation rot);           // Status for orientation
bool has_orientation(Rotation rot);           // Has sensor with orientation
bool has_data_orient(Rotation rot);           // Valid data for orientation

// Range limits
float max_distance_orient(Rotation rot);      // Max range (m)
float min_distance_orient(Rotation rot);      // Min range (m)

// Quality
int8_t signal_quality_pct_orient(Rotation rot);  // Quality 0-100

// Ground clearance (from sensor to ground when level)
float ground_clearance_orient(Rotation rot);

// Position offset
const Vector3f& get_pos_offset_orient(Rotation rot);

// Timing
uint32_t last_reading_ms(Rotation rot);       // Last reading time

// Pre-arm check
bool prearm_healthy(char *msg, uint8_t len);
```

### Parameters (RNGFND_)

| Parameter | Description |
|-----------|-------------|
| `RNGFNDn_TYPE` | Sensor type |
| `RNGFNDn_PIN` | Analog/PWM pin |
| `RNGFNDn_SCALING` | Scaling factor |
| `RNGFNDn_OFFSET` | Offset |
| `RNGFNDn_MIN_CM` | Minimum distance (cm) |
| `RNGFNDn_MAX_CM` | Maximum distance (cm) |
| `RNGFNDn_ORIENT` | Orientation |
| `RNGFNDn_ADDR` | I2C address |
| `RNGFNDn_POS_X/Y/Z` | Position offset |
| `RNGFNDn_GNDCLR_CM` | Ground clearance (cm) |

### Supported Backends (40+)

**Lidar**: LightWare SF02/SF10/SF11/SF40C/SF45B, Benewake TFmini/TF02/TF03/TFLuna, Garmin Lidar-Lite v3/v4, Leddar One, TeraRanger One/Evo, GYUS42v2, Lanbao

**Sonar**: MaxBotix (analog/I2C/serial), Blue Robotics Ping

**Radar**: USD1 CAN radar, Ainstein US-D1

**Other**: PWM input, Analog input, DroneCAN, MAVLink, Lua scripting, SITL

### Usage Example

```cpp
#include <AP_RangeFinder/AP_RangeFinder.h>

void read_rangefinder() {
    RangeFinder *rf = AP::rangefinder();
    if (rf == nullptr) return;

    rf->update();

    // Downward-facing sensor (most common)
    if (rf->has_data_orient(ROTATION_PITCH_270)) {
        float distance_m = rf->distance_orient(ROTATION_PITCH_270);
        RangeFinder::Status status = rf->status_orient(ROTATION_PITCH_270);

        if (status == RangeFinder::Status::Good) {
            // Valid reading
            float max_range = rf->max_distance_orient(ROTATION_PITCH_270);
            float min_range = rf->min_distance_orient(ROTATION_PITCH_270);
        }
    }

    // Forward-facing sensor (for obstacle avoidance)
    if (rf->has_data_orient(ROTATION_NONE)) {
        float forward_dist = rf->distance_orient(ROTATION_NONE);
    }
}
```

### Combining with Barometer

```cpp
float get_altitude_estimate() {
    AP_Baro &baro = AP::baro();
    RangeFinder *rf = AP::rangefinder();

    float baro_alt = baro.get_altitude();

    // Use rangefinder when close to ground
    if (rf != nullptr && rf->has_data_orient(ROTATION_PITCH_270)) {
        float rf_dist = rf->distance_orient(ROTATION_PITCH_270);
        float max_rf = rf->max_distance_orient(ROTATION_PITCH_270);

        if (rf->status_orient(ROTATION_PITCH_270) == RangeFinder::Status::Good) {
            // Blend based on altitude
            if (rf_dist < max_rf * 0.7f) {
                // Trust rangefinder more when low
                return rf_dist;
            }
        }
    }

    return baro_alt;
}
```

### Pre-arm Health Check

```cpp
bool check_rangefinder() {
    RangeFinder *rf = AP::rangefinder();
    if (rf == nullptr || rf->num_sensors() == 0) {
        return true;  // No rangefinder configured
    }

    char msg[50];
    if (!rf->prearm_healthy(msg, sizeof(msg))) {
        // msg contains failure reason
        return false;
    }
    return true;
}
```
