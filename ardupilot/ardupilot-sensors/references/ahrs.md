# AHRS (Attitude Heading Reference System)

AP_AHRS is the primary interface for attitude, position, and velocity estimates. It fuses data from all sensors through EKF backends.

## AP_AHRS

**Location**: `libraries/AP_AHRS/`
**Singleton**: `AP::ahrs()`

### EKF Types

```cpp
enum class EKFType : uint8_t {
    DCM = 0,       // Dead-reckoning only (fallback)
    TWO = 2,       // EKF2
    THREE = 3,     // EKF3 (recommended)
    SIM = 10,      // Simulation
    EXTERNAL = 11, // External AHRS
};
```

### Core Methods - Attitude

```cpp
// Euler angles (radians)
float get_roll_rad();
float get_pitch_rad();
float get_yaw_rad();

// Euler angles (degrees)
float get_roll_deg();
float get_pitch_deg();
float get_yaw_deg();

// Quaternion
bool get_quaternion(Quaternion &quat);

// Rotation matrices
const Matrix3f &get_rotation_body_to_ned();

// Trig helpers
float cos_roll(), cos_pitch(), cos_yaw();
float sin_roll(), sin_pitch(), sin_yaw();

// Gyro (drift-corrected)
const Vector3f &get_gyro();
const Vector3f &get_gyro_drift();
float get_yaw_rate_earth();  // rad/s
```

### Core Methods - Position

```cpp
// Current location (WGS84)
bool get_location(Location &loc);

// Home
const Location &get_home();
bool home_is_set();
bool set_home(const Location &loc);

// Origin (EKF reference)
bool get_origin(Location &ret);
bool set_origin(const Location &loc);

// Relative position (meters from origin/home)
bool get_relative_position_NED_origin(Vector3p &vec);
bool get_relative_position_NED_home(Vector3f &vec);
bool get_relative_position_NE_origin(Vector2p &posNE);
void get_relative_position_D_home(float &posD);

// Height above ground
bool get_hagl(float &hagl);
```

### Core Methods - Velocity

```cpp
// NED velocity (m/s)
bool get_velocity_NED(Vector3f &vec);

// Ground speed
const Vector2f &groundspeed_vector();  // NE (m/s)
float groundspeed();                    // magnitude (m/s)

// Vertical rate
bool get_vert_pos_rate_D(float &velocity);  // m/s, positive down
```

### Core Methods - Wind & Airspeed

```cpp
// Wind estimate (m/s, NED)
const Vector3f &wind_estimate();
bool wind_estimate(Vector3f &wind);

// Airspeed
bool airspeed_EAS(float &airspeed_ret);  // Equivalent airspeed
bool airspeed_TAS(float &airspeed_ret);  // True airspeed
float get_EAS2TAS();                      // Conversion ratio
```

### Health & Status

```cpp
bool healthy();                           // AHRS healthy
bool initialised();                       // Init complete
bool pre_arm_check(bool requires_position, char *msg, uint8_t len);
bool get_filter_status(nav_filter_status &status);

// Vibration
bool is_vibration_affected();
Vector3f get_vibration();
```

### Parameters (AHRS_)

| Parameter | Description |
|-----------|-------------|
| `AHRS_EKF_TYPE` | EKF type (2, 3, 10, 11) |
| `AHRS_ORIENTATION` | Board orientation |
| `AHRS_GPS_USE` | GPS usage for DCM |
| `AHRS_WIND_MAX` | Max wind for estimates |
| `AHRS_TRIM_X/Y/Z` | Trim angles |

### Usage Example

```cpp
#include <AP_AHRS/AP_AHRS.h>

void get_vehicle_state() {
    AP_AHRS &ahrs = AP::ahrs();

    // Attitude
    float roll = ahrs.get_roll_rad();
    float pitch = ahrs.get_pitch_rad();
    float yaw = ahrs.get_yaw_rad();

    // Position
    Location loc;
    if (ahrs.get_location(loc)) {
        // loc.lat, loc.lng in 1e7 degrees
        // loc.alt in cm
    }

    // Velocity
    Vector3f vel;
    if (ahrs.get_velocity_NED(vel)) {
        // vel.x = north, vel.y = east, vel.z = down (m/s)
    }
}
```

### Writing External Data to EKF

```cpp
void send_external_data() {
    AP_AHRS &ahrs = AP::ahrs();

    // Optical flow
    ahrs.writeOptFlowMeas(quality, rawFlowRates, rawGyroRates,
                          timestamp_ms, posOffset, heightOverride);

    // External navigation (VICON, etc.)
    ahrs.writeExtNavData(pos, quat, posErr, angErr,
                         timestamp_ms, delay_ms, resetTime_ms);

    // External velocity
    ahrs.writeExtNavVelData(vel, err, timestamp_ms, delay_ms);
}
```

### Secondary Estimates

For redundancy, access secondary attitude/position sources:

```cpp
void check_secondary() {
    AP_AHRS &ahrs = AP::ahrs();

    Vector3f secondary_euler;
    if (ahrs.get_secondary_attitude(secondary_euler)) {
        // Compare with primary
    }

    Location secondary_pos;
    if (ahrs.get_secondary_position(secondary_pos)) {
        // Check agreement
    }
}
```

### EKF Lane Switching

```cpp
// Check for lane switch possibility
ahrs.check_lane_switch();

// Request yaw reset to avoid failsafe
ahrs.request_yaw_reset();

// Get active core
int8_t core = ahrs.get_primary_core_index();
```
