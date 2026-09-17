# Barometer

AP_Baro provides pressure and altitude from barometric sensors.

## AP_Baro

**Location**: `libraries/AP_Baro/`
**Singleton**: `AP::baro()`

### Core Methods

```cpp
// Initialization
void init();
void calibrate(bool save = true);             // Calibrate ground pressure

// Update
void update();                                // Update readings

// Pressure (Pascals)
float get_pressure();                         // Primary pressure
float get_pressure(uint8_t i);                // Pressure from instance i

// Temperature (°C)
float get_temperature();                      // Primary temperature
float get_temperature(uint8_t i);             // Temperature from instance i

// Altitude (meters, relative to calibration)
float get_altitude();                         // Primary altitude
float get_altitude(uint8_t i);                // Altitude from instance i
float get_altitude_difference(float base_pressure, float pressure);

// Climb rate (m/s, positive up)
float get_climb_rate();

// Health
bool healthy();                               // Primary healthy
bool healthy(uint8_t i);                      // Instance i healthy

// Multi-instance
uint8_t num_instances();                      // Barometer count

// Calibration data
float get_ground_pressure();                  // Calibrated ground pressure
float get_ground_temperature();               // Ground temperature (°C)

// EAS to TAS conversion
float get_EAS2TAS();                          // EAS to TAS ratio

// Sea level pressure for altitude calculation
void set_sea_level_pressure(float pressure);
float get_sea_level_pressure();
```

### Parameters (BARO_)

| Parameter | Description |
|-----------|-------------|
| `BARO_PRIMARY` | Primary barometer |
| `BARO_EXT_BUS` | External barometer bus |
| `BARO_GND_TEMP` | Ground temperature |
| `BARO_ALT_OFFSET` | Altitude offset |
| `BARO_FLTR_RNG` | Filter range |
| `BARO_PROBE_EXT` | Probe external I2C bus |
| `BAROn_GND_PRESS` | Ground pressure for instance n |
| `BAROn_WCF_ENABLE` | Wind correction enable |

### Supported Backends

BMP085, BMP180, BMP280, BMP388, BMP390, MS5611, MS5607, MS5837, SPL06, DPS280, LPS22H, LPS25H, DroneCAN, SITL

### Usage Example

```cpp
#include <AP_Baro/AP_Baro.h>

void read_baro() {
    AP_Baro &baro = AP::baro();

    baro.update();

    if (!baro.healthy()) {
        return;
    }

    float pressure_pa = baro.get_pressure();
    float temp_c = baro.get_temperature();
    float altitude_m = baro.get_altitude();      // Relative to calibration
    float climb_rate = baro.get_climb_rate();    // m/s, positive up
}
```

### Calibration

```cpp
void calibrate_baro() {
    AP_Baro &baro = AP::baro();

    // Must be on ground, vehicle stationary
    // This is blocking
    baro.calibrate(true);  // true = save to EEPROM
}
```

### Multi-Instance

```cpp
void use_best_baro() {
    AP_Baro &baro = AP::baro();

    float best_alt = 0;
    bool found = false;

    for (uint8_t i = 0; i < baro.num_instances(); i++) {
        if (baro.healthy(i)) {
            if (!found) {
                best_alt = baro.get_altitude(i);
                found = true;
            }
        }
    }
}
```

### Altitude Calculation

Altitude is calculated from pressure using the barometric formula. The relationship depends on the ground pressure established during calibration:

```cpp
// Get altitude difference from pressure difference
float base_pressure = baro.get_ground_pressure();
float current_pressure = baro.get_pressure();
float alt_diff = baro.get_altitude_difference(base_pressure, current_pressure);
```

### Temperature Effects

Barometers are sensitive to temperature. ArduPilot includes:
- Internal temperature compensation in most backends
- Optional wind correction factor (BARO_WCF)
- Temperature logging for post-flight analysis
