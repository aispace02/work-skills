# Peripheral Sensors

Specialized sensors for propulsion, environment, and auxiliary systems.

---

## AP_ESC_Telem (ESC Telemetry)

**Location**: `libraries/AP_ESC_Telem/`
**Singleton**: `AP::esc_telem()`

Collects telemetry from ESCs including RPM, current, voltage, and temperature.

### Core Methods

```cpp
// RPM
bool get_rpm(uint8_t esc_index, float &rpm);
float get_average_motor_rpm(uint32_t servo_channel_mask = 0xFFFFFFFF);
float get_average_motor_frequency_hz();
uint8_t get_motor_frequencies_hz(uint8_t nfreqs, float *freqs);

// Electrical
bool get_current(uint8_t esc_index, float &amps);
bool get_voltage(uint8_t esc_index, float &volts);
bool get_consumption_mah(uint8_t esc_index, float &mah);

// Temperature (centi-degrees)
bool get_temperature(uint8_t esc_index, int16_t &temp);
bool get_motor_temperature(uint8_t esc_index, int16_t &temp);
bool get_highest_temperature(int16_t &temp);

// Status
bool get_usage_seconds(uint8_t esc_index, uint32_t &usage_sec);
uint8_t get_num_active_escs();
uint32_t get_active_esc_mask();
bool are_motors_running(uint32_t mask, float min_rpm, float max_rpm);

// Update (call from scripts)
void update_rpm(uint8_t esc_index, float rpm, float error_rate);
```

### Usage Example

```cpp
#include <AP_ESC_Telem/AP_ESC_Telem.h>

void read_esc_telemetry() {
    AP_ESC_Telem &telem = AP::esc_telem();

    // Average motor RPM for harmonic notch
    float avg_rpm = telem.get_average_motor_rpm();

    // Individual ESC data
    for (uint8_t i = 0; i < 4; i++) {
        float rpm, current, voltage;
        int16_t temp;

        if (telem.get_rpm(i, rpm)) {
            // rpm valid
        }
        if (telem.get_current(i, current)) {
            // current in Amps
        }
        if (telem.get_temperature(i, temp)) {
            // temp in centi-degrees
        }
    }
}
```

---

## AP_RPM

**Location**: `libraries/AP_RPM/`
**Singleton**: `AP::rpm()`

General RPM measurement for engines, rotors, etc.

### Core Methods

```cpp
void init();
void update();

uint8_t num_sensors();
bool get_rpm(uint8_t instance, float &rpm);
float get_signal_quality(uint8_t instance);
bool healthy(uint8_t instance);
bool enabled(uint8_t instance);
```

### Parameters (RPM_)

| Parameter | Description |
|-----------|-------------|
| `RPMn_TYPE` | Sensor type (1=PWM, 2=Pin, 3=EFI, 4=HarmonicNotch, 5=ESCTelem, 6=Generator) |
| `RPMn_SCALING` | Scaling factor |
| `RPMn_MAX` | Maximum RPM |
| `RPMn_MIN` | Minimum RPM |
| `RPMn_MIN_QUAL` | Minimum quality |
| `RPMn_PIN` | Input pin |

### Backends

PWM input, GPIO pin, EFI, Harmonic Notch, ESC Telemetry, Generator, DroneCAN, SITL

---

## AP_TemperatureSensor

**Location**: `libraries/AP_TemperatureSensor/`
**Singleton**: `AP::temperature_sensor()`

External temperature sensors for monitoring motors, batteries, environment.

### Core Methods

```cpp
void init();
void update();

uint8_t num_instances();
bool get_temperature(float &temp, uint8_t instance = 0);  // Celsius
bool healthy(uint8_t instance = 0);
```

### Parameters (TEMP_)

| Parameter | Description |
|-----------|-------------|
| `TEMPn_TYPE` | Sensor type |
| `TEMPn_BUS` | I2C bus |
| `TEMPn_ADDR` | I2C address |
| `TEMPn_SRC` | Data source (None, ESC, Motor, Battery, etc.) |
| `TEMPn_SRC_ID` | Source ID |

### Backends

TSYS01, TSYS03, MCP9600 (thermocouple), MAX31865 (RTD), MLX90614 (IR), SHT3x, Analog, DroneCAN

---

## AP_WindVane

**Location**: `libraries/AP_WindVane/`
**Singleton**: `AP::windvane()`

Wind direction and speed for sailboats and weather monitoring.

### Core Methods

```cpp
void init(const AP_SerialManager &serial_manager);
void update();

bool enabled();
bool wind_speed_enabled();

// Apparent wind (relative to vehicle)
float get_apparent_wind_direction_rad();  // 0 = head to wind
float get_apparent_wind_speed();          // m/s

// True wind (absolute)
float get_true_wind_direction_rad();      // 0 = from North
float get_true_wind_speed();              // m/s

// Tacking
enum Sailboat_Tack { TACK_PORT, TACK_STARBOARD };
Sailboat_Tack get_current_tack();
```

### Parameters (WNDVN_)

| Parameter | Description |
|-----------|-------------|
| `WNDVN_TYPE` | Direction sensor type |
| `WNDVN_DIR_PIN` | Analog pin |
| `WNDVN_DIR_V_MIN/MAX` | Voltage range |
| `WNDVN_DIR_OFS` | Bearing offset |
| `WNDVN_SPEED_TYPE` | Speed sensor type |
| `WNDVN_SPEED_PIN` | Speed sensor pin |

---

## AP_EFI (Engine Fuel Injection)

**Location**: `libraries/AP_EFI/`
**Singleton**: `AP::efi()`

Engine management data from EFI systems.

### Core Methods

```cpp
void init();
void update();

bool enabled();
bool healthy();

// Engine state
bool get_fuel_consumption_rate(float &rate);  // L/hr
bool get_fuel_consumed(float &consumed);       // L
bool get_rpm(float &rpm);
bool get_engine_temp(float &temp);             // °C
bool get_throttle_pos(float &pos);             // %
bool get_ignition_timing(float &timing);       // degrees
float get_intake_manifold_pressure();          // kPa
```

### Parameters (EFI_)

| Parameter | Description |
|-----------|-------------|
| `EFI_TYPE` | EFI type |
| `EFI_COEF1/2` | Calibration coefficients |
| `EFI_FUEL_DENS` | Fuel density |

### Backends

MegaSquirt, NWPMU, Lutan, Hirth, DroneCAN, Scripting

---

## AP_Generator

**Location**: `libraries/AP_Generator/`
**Singleton**: `AP::generator()`

Generator/fuel cell monitoring.

### Core Methods

```cpp
void init();
void update();

bool healthy();

// Status
float get_voltage();              // V
float get_current();              // A
float get_output_power();         // W
uint32_t get_runtime_s();         // seconds
float get_fuel_remaining();       // 0-1
```

### Parameters (GEN_)

| Parameter | Description |
|-----------|-------------|
| `GEN_TYPE` | Generator type |

### Backends

RichenPower, IE2400 (fuel cell)

---

## AP_RSSI

**Location**: `libraries/AP_RSSI/`
**Singleton**: `AP::rssi()`

RC receiver signal strength indication.

### Core Methods

```cpp
void init();
void update();

bool enabled();

// Signal quality (0-1)
float read_receiver_rssi();

// Raw value (0-255)
uint8_t read_receiver_rssi_uint8();
```

### Parameters (RSSI_)

| Parameter | Description |
|-----------|-------------|
| `RSSI_TYPE` | Input type (0=disabled, 1=AnalogPin, 2=RCChannel, 3=ReceiverProtocol, 4=PWM) |
| `RSSI_ANA_PIN` | Analog pin |
| `RSSI_PIN_LOW/HIGH` | Voltage range |
| `RSSI_CHANNEL` | RC channel |

---

## AP_WheelEncoder

**Location**: `libraries/AP_WheelEncoder/`
**Singleton**: (accessed via vehicle)

Wheel odometry for ground vehicles.

### Core Methods

```cpp
void init();
void update();

uint8_t num_sensors();
bool healthy(uint8_t instance);

// Readings
Vector2f get_position(uint8_t instance);    // Position in meters
float get_distance(uint8_t instance);        // Total distance
float get_rate(uint8_t instance);            // Speed m/s
uint32_t get_last_reading_ms(uint8_t instance);
```

### Parameters (WENC_)

| Parameter | Description |
|-----------|-------------|
| `WENCn_TYPE` | Encoder type |
| `WENCn_CPR` | Counts per revolution |
| `WENCn_RADIUS` | Wheel radius (m) |
| `WENCn_PIN_A/B` | Quadrature pins |

---

## AP_LeakDetector

**Location**: `libraries/AP_LeakDetector/`
**Singleton**: (accessed via vehicle)

Water leak detection for submarines/ROVs.

### Core Methods

```cpp
void init();
void update();

bool get_status();  // true = leak detected
```

### Parameters (LEAK_)

| Parameter | Description |
|-----------|-------------|
| `LEAKn_PIN` | Input pin |
| `LEAKn_LOGIC` | Logic level (0=low, 1=high) |

---

## AP_ExternalAHRS

**Location**: `libraries/AP_ExternalAHRS/`
**Singleton**: `AP::externalAHRS()`

External AHRS/INS systems providing complete attitude/position solution.

### Core Methods

```cpp
void init();
void update();

bool enabled();
bool healthy();

// Direct access to external solution
bool get_quaternion(Quaternion &quat);
bool get_velocity_NED(Vector3f &vel);
bool get_location(Location &loc);
bool get_speed_NED(Vector3f &vel);
```

### Parameters (EAHRS_)

| Parameter | Description |
|-----------|-------------|
| `EAHRS_TYPE` | External AHRS type |
| `EAHRS_RATE` | Data rate |

### Backends

VectorNav (VN-100/200/300), MicroStrain, InertialLabs, ILabs INS, Scripting
