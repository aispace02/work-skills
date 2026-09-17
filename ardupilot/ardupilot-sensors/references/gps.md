# GPS/GNSS

AP_GPS provides position, velocity, and timing from GNSS receivers.

## AP_GPS

**Location**: `libraries/AP_GPS/`
**Singleton**: `AP::gps()`

### Status Enum

```cpp
enum GPS_Status {
    NO_GPS = 0,              // No GPS detected
    NO_FIX = 1,              // No position fix
    GPS_OK_FIX_2D = 2,       // 2D fix
    GPS_OK_FIX_3D = 3,       // 3D fix
    GPS_OK_FIX_3D_DGPS = 4,  // Differential GPS
    GPS_OK_FIX_3D_RTK_FLOAT = 5,  // RTK float
    GPS_OK_FIX_3D_RTK_FIXED = 6,  // RTK fixed (cm accuracy)
};
```

### Core Methods

```cpp
// Initialization
void init();
void update();                                // Call at 10Hz+

// Fix status
GPS_Status status();                          // Primary status
GPS_Status status(uint8_t i);                 // Instance i status

// Position
const Location& location();                   // Current position
const Location& location(uint8_t i);          // Position from instance i

// Velocity
const Vector3f& velocity();                   // 3D velocity NED (m/s)
float ground_speed();                         // Speed over ground (m/s)
float ground_course();                        // Course over ground (degrees)
bool have_vertical_velocity();                // Has vertical velocity

// Accuracy estimates
bool horizontal_accuracy(float &hacc);        // Horizontal accuracy (m)
bool vertical_accuracy(float &vacc);          // Vertical accuracy (m)
bool speed_accuracy(float &sacc);             // Speed accuracy (m/s)

// Satellite info
uint8_t num_sats();                           // Satellite count
uint8_t num_sats(uint8_t i);                  // Satellites for instance i
uint16_t hdop();                              // Horizontal DOP × 100
uint16_t vdop();                              // Vertical DOP × 100

// GPS heading (dual antenna)
bool gps_yaw_deg(uint8_t i, float &yaw);      // GPS heading (degrees)

// Multi-GPS
uint8_t num_sensors();                        // GPS count
uint8_t primary_sensor();                     // Primary instance

// Timing
uint16_t time_week();                         // GPS week number
uint32_t time_week_ms();                      // ms into GPS week
uint32_t last_fix_time_ms();                  // Time of last fix
```

### Location Structure

```cpp
struct Location {
    int32_t lat;   // Latitude in degrees × 10^7
    int32_t lng;   // Longitude in degrees × 10^7
    int32_t alt;   // Altitude in cm (AMSL or relative)
};
```

### Parameters (GPS_)

| Parameter | Description |
|-----------|-------------|
| `GPS_TYPE` | GPS type (1=Auto, various specific) |
| `GPS_TYPE2` | Second GPS type |
| `GPS_NAVFILTER` | Navigation filter mode |
| `GPS_AUTO_SWITCH` | Auto-switch between GPS |
| `GPS_MIN_DGPS` | Min satellites for DGPS |
| `GPS_SBAS_MODE` | SBAS mode |
| `GPS_INJECT_TO` | Inject to (for RTK) |
| `GPS_SBP_LOGMASK` | SBP logging mask |
| `GPS_RAW_DATA` | Raw data logging |
| `GPS_GNSS_MODE` | GNSS constellation selection |
| `GPS_SAVE_CFG` | Save GPS config |
| `GPS_AUTO_CONFIG` | Auto-configure GPS |
| `GPS_RATE_MS` | Update rate (ms) |
| `GPS_POS_X/Y/Z` | Antenna position offset |

### Supported Backends

u-blox (M8, F9P), Septentrio SBF, Swift SBP, Trimble, NMEA, DroneCAN, MAVLink, SITL

### Usage Example

```cpp
#include <AP_GPS/AP_GPS.h>

void read_gps() {
    AP_GPS &gps = AP::gps();

    // Check fix quality first
    if (gps.status() < AP_GPS::GPS_OK_FIX_3D) {
        return;  // No valid 3D fix
    }

    // Get position
    Location loc = gps.location();
    double lat_deg = loc.lat * 1.0e-7;
    double lon_deg = loc.lng * 1.0e-7;
    float alt_m = loc.alt * 0.01f;  // Convert cm to m

    // Get velocity
    Vector3f vel = gps.velocity();  // NED in m/s
    float ground_speed = gps.ground_speed();  // m/s
    float course = gps.ground_course();  // degrees

    // Get accuracy estimates
    float hacc, vacc;
    if (gps.horizontal_accuracy(hacc)) {
        // hacc in meters
    }

    // Satellite info
    uint8_t num_sats = gps.num_sats();
    uint16_t hdop = gps.hdop();  // × 100
}
```

### Multi-GPS Handling

```cpp
void check_all_gps() {
    AP_GPS &gps = AP::gps();

    uint8_t num = gps.num_sensors();
    for (uint8_t i = 0; i < num; i++) {
        if (gps.status(i) >= AP_GPS::GPS_OK_FIX_3D) {
            Location loc = gps.location(i);
            // Process each GPS
        }
    }

    // Get primary (blended or selected)
    uint8_t primary = gps.primary_sensor();
}
```

### RTK Status Check

```cpp
bool has_rtk_fix() {
    AP_GPS &gps = AP::gps();
    return gps.status() >= AP_GPS::GPS_OK_FIX_3D_RTK_FLOAT;
}

bool has_rtk_fixed() {
    AP_GPS &gps = AP::gps();
    return gps.status() == AP_GPS::GPS_OK_FIX_3D_RTK_FIXED;
}
```
