# Adding a New Sensor Driver to ArduPilot

Step-by-step guide for implementing a new sensor backend.

## Overview

ArduPilot uses a Frontend/Backend architecture:
- **Frontend**: Unified API (`AP_Baro`, `AP_GPS`, etc.) - manages multiple backends
- **Backend**: Hardware-specific driver (`AP_Baro_BMP280`, `AP_GPS_UBLOX`, etc.)

## Step 1: Understand the Existing Architecture

Before writing code, study an existing backend in the same sensor family:

| Sensor Type | Study These | Location |
|-------------|-------------|----------|
| Barometer | `AP_Baro_BMP280`, `AP_Baro_MS5611` | `libraries/AP_Baro/` |
| IMU | `AP_InertialSensor_BMI088` | `libraries/AP_InertialSensor/` |
| Compass | `AP_Compass_HMC5843` | `libraries/AP_Compass/` |
| GPS | `AP_GPS_UBLOX`, `AP_GPS_NMEA` | `libraries/AP_GPS/` |
| RangeFinder | `AP_RangeFinder_LightWareI2C` | `libraries/AP_RangeFinder/` |

## Step 2: Create Header File

```cpp
// AP_Baro_MyDevice.h
#pragma once

#include "AP_Baro_Backend.h"

#if AP_BARO_MYDEVICE_ENABLED  // Define in AP_Baro_config.h

#include <AP_HAL/AP_HAL.h>
#include <AP_HAL/Device.h>

class AP_Baro_MyDevice : public AP_Baro_Backend {
public:
    // Constructor takes frontend reference and HAL device
    AP_Baro_MyDevice(AP_Baro &baro, AP_HAL::Device &dev);

    // Required: transfer accumulated data to frontend
    void update() override;

    // Static factory method for auto-detection
    static AP_Baro_Backend *probe(AP_Baro &baro, AP_HAL::Device &dev);

private:
    bool _init();
    void _timer();  // Periodic callback

    AP_HAL::Device *_dev;
    uint8_t _instance;

    // Calibration data (read from sensor)
    struct {
        uint16_t c1, c2, c3, c4, c5, c6;
    } _cal;

    // Thread-safe accumulation
    float _pressure_sum;
    uint32_t _pressure_count;
    float _temperature;
};

#endif  // AP_BARO_MYDEVICE_ENABLED
```

## Step 3: Implement Source File

```cpp
// AP_Baro_MyDevice.cpp
#include "AP_Baro_MyDevice.h"

#if AP_BARO_MYDEVICE_ENABLED

#include <AP_Math/definitions.h>

extern const AP_HAL::HAL &hal;

// Device registers
#define MYDEV_REG_ID        0x00
#define MYDEV_REG_CONFIG    0x01
#define MYDEV_REG_DATA      0x10
#define MYDEV_REG_CALIB     0x20

#define MYDEV_CHIP_ID       0x5A

AP_Baro_MyDevice::AP_Baro_MyDevice(AP_Baro &baro, AP_HAL::Device &dev)
    : AP_Baro_Backend(baro)
    , _dev(&dev)
{
}

// Static probe function - called during sensor detection
AP_Baro_Backend *AP_Baro_MyDevice::probe(AP_Baro &baro, AP_HAL::Device &dev) {
    AP_Baro_MyDevice *sensor = NEW_NOTHROW AP_Baro_MyDevice(baro, dev);
    if (!sensor || !sensor->_init()) {
        delete sensor;
        return nullptr;
    }
    return sensor;
}

bool AP_Baro_MyDevice::_init() {
    if (!_dev) {
        return false;
    }

    // Get bus semaphore for thread-safe access
    WITH_SEMAPHORE(_dev->get_semaphore());

    // Set bus speed
    _dev->set_speed(AP_HAL::Device::SPEED_HIGH);

    // Check chip ID
    uint8_t id;
    if (!_dev->read_registers(MYDEV_REG_ID, &id, 1) || id != MYDEV_CHIP_ID) {
        return false;
    }

    // Read calibration data
    uint8_t cal_buf[12];
    if (!_dev->read_registers(MYDEV_REG_CALIB, cal_buf, sizeof(cal_buf))) {
        return false;
    }
    _cal.c1 = (cal_buf[0] << 8) | cal_buf[1];
    _cal.c2 = (cal_buf[2] << 8) | cal_buf[3];
    // ... parse remaining calibration

    // Configure sensor
    if (!_dev->write_register(MYDEV_REG_CONFIG, 0x03)) {
        return false;
    }

    // Register this sensor instance with frontend
    _instance = _frontend.register_sensor();

    // Set device type for logging
    _dev->set_device_type(DEVTYPE_BARO_MYDEVICE);
    set_bus_id(_instance, _dev->get_bus_id());

    // Register periodic callback at 50Hz (20ms = 20000us)
    _dev->register_periodic_callback(
        20000,
        FUNCTOR_BIND_MEMBER(&AP_Baro_MyDevice::_timer, void)
    );

    return true;
}

// Called from timer thread at 50Hz
void AP_Baro_MyDevice::_timer() {
    uint8_t buf[6];

    if (!_dev->read_registers(MYDEV_REG_DATA, buf, sizeof(buf))) {
        return;
    }

    // Parse raw data
    int32_t raw_pressure = (buf[0] << 16) | (buf[1] << 8) | buf[2];
    int32_t raw_temp = (buf[3] << 16) | (buf[4] << 8) | buf[5];

    // Apply calibration (device-specific formula)
    float pressure = calculate_pressure(raw_pressure, raw_temp);
    float temperature = calculate_temperature(raw_temp);

    // Validate pressure
    if (!pressure_ok(pressure)) {
        return;
    }

    // Thread-safe accumulation
    WITH_SEMAPHORE(_sem);
    _pressure_sum += pressure;
    _pressure_count++;
    _temperature = temperature;
}

// Called from main thread at ~10Hz
void AP_Baro_MyDevice::update() {
    WITH_SEMAPHORE(_sem);

    if (_pressure_count == 0) {
        return;
    }

    // Calculate average and send to frontend
    float avg_pressure = _pressure_sum / _pressure_count;
    _copy_to_frontend(_instance, avg_pressure, _temperature);

    // Reset accumulators
    _pressure_sum = 0;
    _pressure_count = 0;
}

#endif  // AP_BARO_MYDEVICE_ENABLED
```

## Step 4: Add Configuration Flag

In `AP_Baro_config.h`:
```cpp
#ifndef AP_BARO_MYDEVICE_ENABLED
#define AP_BARO_MYDEVICE_ENABLED 1
#endif
```

## Step 5: Register Probe in Frontend

In `AP_Baro.cpp`:
```cpp
#include "AP_Baro_MyDevice.h"

void AP_Baro::init() {
    // ... existing probes ...

#if AP_BARO_MYDEVICE_ENABLED
    // Probe I2C bus for MyDevice
    probe_i2c_dev(AP_Baro_MyDevice::probe, HAL_BARO_MYDEVICE_I2C_BUS,
                  HAL_BARO_MYDEVICE_I2C_ADDR);
#endif
}
```

## Step 6: Add Device Type

In `libraries/AP_HAL/Util.h` add device type enum:
```cpp
enum DEVTYPE {
    // ... existing types ...
    DEVTYPE_BARO_MYDEVICE = 0x30,
};
```

## Step 7: Add to Build

In `libraries/AP_Baro/wscript` or ensure file is in the directory (auto-compiled).

## Step 8: Test with SITL

1. Build for SITL:
```bash
./waf configure --board sitl
./waf copter
```

2. Run simulation:
```bash
sim_vehicle.py -v ArduCopter --console --map
```

3. Check sensor detection in console

## Step 9: Test on Hardware

1. Build for target board:
```bash
./waf configure --board CubeBlack
./waf copter
```

2. Upload and check:
```
# In MAVProxy
status
# Look for BARO messages
```

## Key Patterns to Follow

### Semaphore Usage
```cpp
// Always use semaphore when accessing shared data
WITH_SEMAPHORE(_sem);  // Auto-releases on scope exit
```

### Error Handling
```cpp
// Check return values
if (!_dev->read_registers(...)) {
    return;  // or return false
}

// Validate readings
if (!pressure_ok(pressure)) {
    return;
}
```

### Timer Callbacks
```cpp
// Register at appropriate rate
_dev->register_periodic_callback(
    20000,  // microseconds (50Hz)
    FUNCTOR_BIND_MEMBER(&MyClass::_timer, void)
);
```

### Data Accumulation
```cpp
// In timer (fast thread):
_pressure_sum += reading;
_pressure_count++;

// In update (slow thread):
float avg = _pressure_sum / _pressure_count;
_copy_to_frontend(_instance, avg, _temp);
_pressure_sum = 0;
_pressure_count = 0;
```

## Checklist

- [ ] Header file with class declaration
- [ ] Source file with implementation
- [ ] Config flag in `*_config.h`
- [ ] Probe registered in frontend `init()`
- [ ] Device type enum added
- [ ] Compiles without errors
- [ ] Tested in SITL
- [ ] Tested on hardware
- [ ] Follows existing code style
