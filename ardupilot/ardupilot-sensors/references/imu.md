# IMU - Inertial Measurement Unit

AP_InertialSensor provides gyroscope and accelerometer data.

## AP_InertialSensor

**Location**: `libraries/AP_InertialSensor/`
**Singleton**: `AP::ins()`

### Core Methods

```cpp
// Initialization
void init(uint16_t sample_rate_hz);           // Init at specified rate (typically 400Hz)
void periodic();                               // Call from main loop

// Gyroscope (angular rates in rad/s)
const Vector3f& get_gyro();                   // Primary gyro
const Vector3f& get_gyro(uint8_t i);          // Gyro instance i
bool get_gyro_health();                       // Primary healthy
bool get_gyro_health(uint8_t i);              // Instance i healthy
uint8_t get_gyro_count();                     // Number of gyros
uint8_t get_primary_gyro();                   // Primary instance

// Accelerometer (m/s²)
const Vector3f& get_accel();                  // Primary accel
const Vector3f& get_accel(uint8_t i);         // Accel instance i
bool get_accel_health();                      // Primary healthy
bool get_accel_health(uint8_t i);             // Instance i healthy
uint8_t get_accel_count();                    // Number of accels
uint8_t get_primary_accel();                  // Primary instance

// Delta (integrated) values - for EKF
bool get_delta_angle(uint8_t i, Vector3f &delta_angle, float &dt);
bool get_delta_velocity(uint8_t i, Vector3f &delta_velocity, float &dt);

// Calibration
bool calibrating();                           // Currently calibrating
void init_accel();                            // Simple level calibration
const Vector3f& get_gyro_offsets(uint8_t i);  // Gyro calibration offsets
const Vector3f& get_accel_offsets(uint8_t i); // Accel calibration offsets

// Clipping detection
uint32_t get_accel_clip_count(uint8_t i);     // Clipping events count

// Temperature
float get_temperature(uint8_t i);             // Sensor temp (°C)
```

### Parameters (INS_)

| Parameter | Description |
|-----------|-------------|
| `INS_GYRO_FILTER` | Gyro low-pass filter (Hz) |
| `INS_ACCEL_FILTER` | Accel low-pass filter (Hz) |
| `INS_USE` | IMU to use (0=all, 1=first, etc.) |
| `INS_GYROx_ID` | Device ID for gyro x |
| `INS_ACCx_ID` | Device ID for accel x |
| `INS_GYROx_CALTEMP` | Calibration temperature |
| `INS_ACC_BODYFIX` | Body-fixed accel offsets |
| `INS_FAST_SAMPLE` | Fast sampling mode |

### Supported Backends

ICM20689, ICM20602, ICM20948, ICM42688, BMI055, BMI088, BMI160, BMI270, MPU6000, MPU9250, LSM9DS0, LSM9DS1, ADIS16xxx, DroneCAN, ExternalAHRS, SITL

### Usage Example

```cpp
#include <AP_InertialSensor/AP_InertialSensor.h>

void read_imu() {
    AP_InertialSensor &ins = AP::ins();

    // Get rotation rates (rad/s)
    Vector3f gyro = ins.get_gyro();
    float roll_rate = gyro.x;
    float pitch_rate = gyro.y;
    float yaw_rate = gyro.z;

    // Get acceleration (m/s²)
    Vector3f accel = ins.get_accel();
    float accel_x = accel.x;  // Forward
    float accel_y = accel.y;  // Right
    float accel_z = accel.z;  // Down

    // For EKF integration, use delta values
    Vector3f delta_angle;
    float dt;
    if (ins.get_delta_angle(0, delta_angle, dt)) {
        // delta_angle contains integrated rotation since last call
    }
}
```

### Multi-Instance

```cpp
void check_all_imus() {
    AP_InertialSensor &ins = AP::ins();

    uint8_t gyro_count = ins.get_gyro_count();
    for (uint8_t i = 0; i < gyro_count; i++) {
        if (ins.get_gyro_health(i)) {
            Vector3f gyro = ins.get_gyro(i);
            // Use gyro data
        }
    }

    uint8_t primary = ins.get_primary_gyro();
}
```

---

## Related: AP_AccelCal

Accelerometer calibration routines.

```cpp
// Start 6-position calibration
ins.accel_calibration_start();

// In loop during calibration
ins.accel_calibration_update();

// Check status
if (ins.calibrating()) {
    // Still calibrating
}
```

---

## Related: AP_GyroFFT

FFT analysis for motor harmonic filtering.

**Singleton**: `AP_GyroFFT::get_singleton()`

```cpp
AP_GyroFFT *fft = AP_GyroFFT::get_singleton();
if (fft != nullptr && fft->enabled()) {
    float freq = fft->get_weighted_freq_hz(0);  // Dominant frequency
    float energy = fft->get_weighted_energy();
}
```

### Parameters (FFT_)

| Parameter | Description |
|-----------|-------------|
| `FFT_ENABLE` | Enable FFT |
| `FFT_WINDOW_SIZE` | FFT window size |
| `FFT_WINDOW_OLAP` | Window overlap |
| `FFT_FREQ_HOVER` | Expected hover frequency |
| `FFT_MINHZ` | Minimum tracked frequency |
| `FFT_MAXHZ` | Maximum tracked frequency |
