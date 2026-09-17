# Airspeed

AP_Airspeed provides airspeed measurements for fixed-wing aircraft.

## AP_Airspeed

**Location**: `libraries/AP_Airspeed/`
**Singleton**: `AP::airspeed()`

### Core Methods

```cpp
// Initialization
void init();
void calibrate(bool in_startup);              // Calibrate zero offset

// Update
void update();                                // Update readings

// Airspeed (m/s)
float get_airspeed();                         // Indicated airspeed (primary)
float get_airspeed(uint8_t i);                // Airspeed from instance i
float get_raw_airspeed();                     // Unfiltered airspeed

// Pressure
float get_differential_pressure();            // Pressure difference (Pa)

// Temperature
bool get_temperature(float &temp);            // Probe temperature (°C)

// Health
bool healthy();                               // Primary healthy
bool healthy(uint8_t i);                      // Instance i healthy
bool enabled();                               // Airspeed enabled
bool use();                                   // Use for control

// Calibration
float get_airspeed_ratio();                   // Calibration ratio
void set_airspeed_ratio(float ratio);

// Timing
uint32_t last_update_ms();                    // Last update time

// Multi-instance
uint8_t get_num_sensors();                    // Number of sensors
uint8_t get_primary();                        // Primary instance
```

### Parameters (ARSPD_)

| Parameter | Description |
|-----------|-------------|
| `ARSPD_TYPE` | Sensor type |
| `ARSPD_USE` | Use airspeed |
| `ARSPD_OFFSET` | Pressure offset |
| `ARSPD_RATIO` | Airspeed ratio |
| `ARSPD_PIN` | Analog pin |
| `ARSPD_AUTOCAL` | Auto-calibrate |
| `ARSPD_TUBE_ORDER` | Pitot tube order |
| `ARSPD_SKIP_CAL` | Skip calibration |
| `ARSPD_PSI_RANGE` | Pressure range (PSI) |
| `ARSPD_BUS` | I2C bus |
| `ARSPD_PRIMARY` | Primary sensor |
| `ARSPD2_*` | Second sensor parameters |

### Supported Backends

MS4525DO, MS5525, DLVR, SDP3x, ASP5033, NMEA, Analog, DroneCAN, SITL

### Usage Example

```cpp
#include <AP_Airspeed/AP_Airspeed.h>

void read_airspeed() {
    AP_Airspeed *airspeed = AP::airspeed();
    if (airspeed == nullptr) return;

    airspeed->update();

    if (!airspeed->healthy() || !airspeed->enabled()) {
        return;
    }

    float ias = airspeed->get_airspeed();     // Indicated airspeed (m/s)
    float raw = airspeed->get_raw_airspeed(); // Unfiltered

    float diff_pressure = airspeed->get_differential_pressure();

    float temp;
    if (airspeed->get_temperature(temp)) {
        // temp in °C
    }
}
```

### True vs Indicated Airspeed

```cpp
// Indicated Airspeed (IAS) - what the sensor reads
float ias = airspeed->get_airspeed();

// True Airspeed (TAS) - corrected for altitude/density
AP_Baro &baro = AP::baro();
float eas2tas = baro.get_EAS2TAS();
float tas = ias * eas2tas;

// Or use AHRS which provides corrected airspeed
AP_AHRS &ahrs = AP::ahrs();
float airspeed_estimate;
if (ahrs.airspeed_estimate(airspeed_estimate)) {
    // airspeed_estimate is in m/s
}
```

### Calibration

Airspeed sensors need calibration for accurate readings:

```cpp
// Zero pressure calibration (on startup, no wind)
airspeed->calibrate(true);

// Ratio calibration (ARSPD_RATIO)
// Done automatically if ARSPD_AUTOCAL enabled
// Uses GPS ground speed vs airspeed comparison
```

### Synthetic Airspeed

When no airspeed sensor is available, ArduPilot can estimate airspeed:

```cpp
// AHRS provides estimated airspeed from GPS and attitude
AP_AHRS &ahrs = AP::ahrs();
float airspeed;
if (ahrs.airspeed_estimate(airspeed)) {
    // Uses GPS groundspeed and wind estimate
}
```

### Multi-Sensor

```cpp
void check_all_airspeed() {
    AP_Airspeed *airspeed = AP::airspeed();
    if (airspeed == nullptr) return;

    uint8_t num = airspeed->get_num_sensors();
    for (uint8_t i = 0; i < num; i++) {
        if (airspeed->healthy(i)) {
            float speed = airspeed->get_airspeed(i);
        }
    }

    uint8_t primary = airspeed->get_primary();
}
```
