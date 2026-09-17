# Battery Monitor

AP_BattMonitor provides voltage, current, and capacity tracking.

## AP_BattMonitor

**Location**: `libraries/AP_BattMonitor/`
**Singleton**: `AP::battery()`

### Failsafe Enum

```cpp
enum class Failsafe : uint8_t {
    None = 0,
    Unhealthy,
    Low,
    Critical
};
```

### Core Methods

```cpp
// Initialization
void init();

// Update
void read();                                  // Update readings (call at 10Hz)

// Multi-instance
uint8_t num_instances();                      // Battery count

// Voltage
float voltage();                              // Primary voltage (V)
float voltage(uint8_t i);                     // Voltage of battery i
float voltage_resting_estimate(uint8_t i);    // Estimated resting voltage

// Current
bool current_amps(float &current, uint8_t i = 0);  // Current (A)
bool consumed_mah(float &mah, uint8_t i = 0);      // Consumed (mAh)
bool consumed_wh(float &wh, uint8_t i = 0);        // Consumed (Wh)

// Capacity
bool capacity_remaining_pct(uint8_t &pct, uint8_t i = 0);  // Remaining %
int32_t pack_capacity_mah(uint8_t i = 0);     // Total capacity (mAh)
bool time_remaining(uint32_t &secs, uint8_t i = 0);        // Time remaining (s)

// Health
bool healthy();                               // All healthy
bool healthy(uint8_t i);                      // Instance i healthy

// Temperature
bool get_temperature(float &temp, uint8_t i = 0);  // Temp (°C)

// Failsafe
bool has_failsafed();                         // Failsafe triggered
Failsafe failsafe_status(uint8_t i = 0);

// Cell monitoring (smart batteries)
bool has_cell_voltages(uint8_t i = 0);
uint16_t get_cell_voltage(uint8_t i, uint8_t cell);  // Cell voltage (mV)

// Power
float power_w(uint8_t i = 0);                 // Current power (W)
```

### Parameters (BATTn_)

| Parameter | Description |
|-----------|-------------|
| `BATTn_MONITOR` | Monitor type |
| `BATTn_CAPACITY` | Pack capacity (mAh) |
| `BATTn_LOW_VOLT` | Low voltage threshold |
| `BATTn_CRT_VOLT` | Critical voltage threshold |
| `BATTn_LOW_MAH` | Low mAh threshold |
| `BATTn_CRT_MAH` | Critical mAh threshold |
| `BATTn_LOW_TIMER` | Low voltage timeout |
| `BATTn_FS_VOLTSRC` | Failsafe voltage source |
| `BATTn_FS_LOW_ACT` | Low failsafe action |
| `BATTn_FS_CRT_ACT` | Critical failsafe action |
| `BATTn_CURR_PIN` | Current sense pin |
| `BATTn_VOLT_PIN` | Voltage sense pin |
| `BATTn_AMP_PERVLT` | Amps per volt |
| `BATTn_VOLT_MULT` | Voltage multiplier |
| `BATTn_ARM_VOLT` | Min arm voltage |

### Supported Backends

Analog, SMBus smart batteries (Solo, Maxell, Rotoye, NeoDesign), DroneCAN, FuelFlow, Generator, INA2xx, INA3221, ESC telemetry, Scripting

### Usage Example

```cpp
#include <AP_BattMonitor/AP_BattMonitor.h>

void read_battery() {
    AP_BattMonitor &battery = AP::battery();

    battery.read();

    if (!battery.healthy()) {
        return;
    }

    // Primary battery
    float voltage = battery.voltage();

    float current;
    if (battery.current_amps(current)) {
        // current in Amps
    }

    float mah;
    if (battery.consumed_mah(mah)) {
        // mah consumed
    }

    uint8_t remaining_pct;
    if (battery.capacity_remaining_pct(remaining_pct)) {
        // remaining_pct is 0-100
    }

    // Check failsafe
    if (battery.has_failsafed()) {
        // Handle failsafe
    }
}
```

### Multi-Battery

```cpp
void check_all_batteries() {
    AP_BattMonitor &battery = AP::battery();

    uint8_t num = battery.num_instances();
    for (uint8_t i = 0; i < num; i++) {
        if (battery.healthy(i)) {
            float voltage = battery.voltage(i);
            float current;
            battery.current_amps(current, i);

            uint8_t pct;
            if (battery.capacity_remaining_pct(pct, i)) {
                // Use remaining percentage
            }
        }
    }
}
```

### Failsafe Handling

```cpp
void check_battery_failsafe() {
    AP_BattMonitor &battery = AP::battery();

    if (battery.has_failsafed()) {
        AP_BattMonitor::Failsafe fs = battery.failsafe_status();

        switch (fs) {
            case AP_BattMonitor::Failsafe::Low:
                // Low battery action
                break;
            case AP_BattMonitor::Failsafe::Critical:
                // Critical battery action (land immediately)
                break;
            case AP_BattMonitor::Failsafe::Unhealthy:
                // Sensor failed
                break;
            default:
                break;
        }
    }
}
```

### Smart Battery Cell Monitoring

```cpp
void check_cells() {
    AP_BattMonitor &battery = AP::battery();

    if (battery.has_cell_voltages(0)) {
        // Typically 3-12 cells for LiPo
        for (uint8_t cell = 0; cell < 12; cell++) {
            uint16_t mv = battery.get_cell_voltage(0, cell);
            if (mv == 0) break;  // No more cells

            // Check for low cell
            if (mv < 3200) {  // 3.2V per cell warning
                // Cell voltage low
            }
        }
    }
}
```

### Power Consumption Tracking

```cpp
void log_power() {
    AP_BattMonitor &battery = AP::battery();

    float power = battery.power_w();  // Current power draw in Watts

    float wh;
    if (battery.consumed_wh(wh)) {
        // Total energy used in Wh
    }
}
```
