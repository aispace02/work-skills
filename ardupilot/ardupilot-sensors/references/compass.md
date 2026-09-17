# Compass / Magnetometer

Compass (AP_Compass) provides magnetic field measurements for heading.

## Compass

**Location**: `libraries/AP_Compass/`
**Singleton**: `AP::compass()`

### Core Methods

```cpp
// Initialization
void init();
bool read();                                  // Read and update values

// Magnetic field (milligauss)
const Vector3f& get_field();                  // Primary field
const Vector3f& get_field(uint8_t i);         // Field from instance i

// Heading
float calculate_heading(const Matrix3f &dcm); // Heading in radians
float calculate_heading(const Matrix3f &dcm, uint8_t i);

// Health
bool healthy();                               // Primary healthy
bool healthy(uint8_t i);                      // Instance i healthy
bool available();                             // Enabled and initialized

// Multi-instance
uint8_t get_count();                          // Compass count
uint8_t get_primary();                        // Primary instance
bool use_for_yaw();                           // Used for yaw
bool use_for_yaw(uint8_t i);                  // Instance i used for yaw

// Declination
float get_declination();                      // Magnetic declination (rad)
void set_declination(float dec, bool save_to_eeprom = true);

// Calibration
void set_offsets(uint8_t i, const Vector3f &offsets);
const Vector3f& get_offsets(uint8_t i);
void set_diagonals(uint8_t i, const Vector3f &diagonals);
const Vector3f& get_diagonals(uint8_t i);
void set_offdiagonals(uint8_t i, const Vector3f &offdiagonals);
const Vector3f& get_offdiagonals(uint8_t i);

// Motor compensation
void set_motor_compensation(uint8_t i, const Vector3f &compensation);
void motor_compensation_type(uint8_t comp_type);
```

### Parameters (COMPASS_)

| Parameter | Description |
|-----------|-------------|
| `COMPASS_USE` | Use compass for yaw |
| `COMPASS_USE2/3` | Use additional compasses |
| `COMPASS_AUTODEC` | Auto declination |
| `COMPASS_DEC` | Declination (rad) |
| `COMPASS_OFSx_X/Y/Z` | Offsets for compass x |
| `COMPASS_DIAx_X/Y/Z` | Diagonal correction |
| `COMPASS_ODIx_X/Y/Z` | Off-diagonal correction |
| `COMPASS_MOTx_X/Y/Z` | Motor compensation |
| `COMPASS_MOTCT` | Motor compensation type |
| `COMPASS_ORIENT` | External compass orientation |
| `COMPASS_EXTERN` | External compass |
| `COMPASS_LEARN` | Learn offsets |

### Supported Backends

HMC5843, HMC5883, AK8963, AK09916, LIS3MDL, LIS2MDL, IST8310, IST8308, QMC5883L, BMM150, RM3100, DroneCAN, ExternalAHRS

### Usage Example

```cpp
#include <AP_Compass/AP_Compass.h>
#include <AP_AHRS/AP_AHRS.h>

void read_compass() {
    Compass &compass = AP::compass();

    if (!compass.read() || !compass.healthy()) {
        return;
    }

    // Raw magnetic field (milligauss)
    Vector3f field = compass.get_field();

    // Calculate heading (need attitude for tilt compensation)
    AP_AHRS &ahrs = AP::ahrs();
    float heading_rad = compass.calculate_heading(ahrs.get_rotation_body_to_ned());
    float heading_deg = degrees(heading_rad);
}
```

### Calibration

```cpp
void start_compass_cal() {
    Compass &compass = AP::compass();

    // Start calibration for all compasses
    for (uint8_t i = 0; i < compass.get_count(); i++) {
        compass.start_calibration(i);
    }
}

void update_compass_cal() {
    Compass &compass = AP::compass();

    // Call periodically during calibration
    compass.compass_cal_update();

    // Check if complete
    for (uint8_t i = 0; i < compass.get_count(); i++) {
        auto status = compass.get_calibration_status(i);
        // Handle status
    }
}
```

### Multi-Instance

```cpp
void check_all_compasses() {
    Compass &compass = AP::compass();

    uint8_t count = compass.get_count();
    for (uint8_t i = 0; i < count; i++) {
        if (compass.healthy(i) && compass.use_for_yaw(i)) {
            Vector3f field = compass.get_field(i);
            // Use field data
        }
    }
}
```

### Motor Compensation

Compass readings can be affected by motor currents. ArduPilot supports automatic compensation:

```cpp
// Types of motor compensation
// 0 = Disabled
// 1 = Use throttle
// 2 = Use current

// Set via COMPASS_MOTCT parameter
// Calibration happens during COMPASS_MOT procedure
```
