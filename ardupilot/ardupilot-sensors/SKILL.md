---
name: ardupilot-sensors
description: |
  ArduPilot sensor libraries (AP_InertialSensor, AP_GPS, AP_Compass, AP_Baro, RangeFinder,
  AP_Airspeed, AP_OpticalFlow, AP_BattMonitor, AP_Proximity, AP_AHRS, and more). Use when:
  (1) Reading sensor data in ArduPilot code
  (2) Adding new sensor drivers or backends
  (3) Understanding frontend/backend architecture
  (4) Debugging sensor health, calibration, or data flow
  (5) Working with peripheral sensors (ESC telemetry, RPM, temperature, etc.)
---

# ArduPilot Sensor Libraries

## Reference Lookup

| Sensor | Library | Reference |
|--------|---------|-----------|
| IMU (Gyro/Accel) | AP_InertialSensor | [imu.md](references/imu.md) |
| GPS/GNSS | AP_GPS | [gps.md](references/gps.md) |
| Compass | Compass/AP_Compass | [compass.md](references/compass.md) |
| Barometer | AP_Baro | [baro.md](references/baro.md) |
| Distance Sensors | RangeFinder | [rangefinder.md](references/rangefinder.md) |
| Airspeed | AP_Airspeed | [airspeed.md](references/airspeed.md) |
| Optical Flow | AP_OpticalFlow | [opticalflow.md](references/opticalflow.md) |
| Battery | AP_BattMonitor | [battery.md](references/battery.md) |
| Proximity/360° | AP_Proximity | [proximity.md](references/proximity.md) |
| State Estimation | AP_AHRS | [ahrs.md](references/ahrs.md) |
| Indoor Positioning | AP_Beacon, AP_VisualOdom | [positioning.md](references/positioning.md) |
| Peripheral Sensors | ESC_Telem, RPM, Temp, Wind, etc. | [peripheral.md](references/peripheral.md) |
| Common Patterns | Architecture, thread safety | [common-patterns.md](references/common-patterns.md) |
| Adding New Drivers | Backend development | [new-driver-guide.md](references/new-driver-guide.md) |

## Singleton Accessors

| Library | Accessor |
|---------|----------|
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

## Frontend/Backend Pattern

```
Vehicle Code → Frontend (AP_Baro) → Backend (AP_Baro_BMP280) → HAL (I2C/SPI)
               - Unified API         - Hardware-specific        - Bus access
               - Multi-sensor mgmt   - Timer callbacks
               - Calibration         - Data accumulation
```

## Basic Usage Pattern

```cpp
SensorClass &sensor = AP::sensor();
sensor.init();

void loop() {
    sensor.update();
    if (sensor.healthy()) {
        auto value = sensor.get_value();
    }
}
```

## Scripts

- `scripts/find_sensor_backends.py <library>` - List backends for a sensor
- `scripts/sensor_params.py <library>` - Extract parameters
- `scripts/find_sensor_usage.py <library>` - Find usage in vehicle code

## File Locations

All sensor libraries are in `libraries/`:
- `AP_InertialSensor/` - IMU (gyro/accel)
- `AP_GPS/` - GPS/GNSS
- `AP_Compass/` - Magnetometer
- `AP_Baro/` - Barometer
- `AP_RangeFinder/` - Distance sensors
- `AP_Airspeed/` - Airspeed
- `AP_OpticalFlow/` - Optical flow
- `AP_BattMonitor/` - Battery
- `AP_Proximity/` - 360° sensors
- `AP_AHRS/` - State estimation
