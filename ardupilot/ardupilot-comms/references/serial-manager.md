# Serial Port Manager

AP_SerialManager handles serial port configuration and protocol assignment.

## AP_SerialManager

**Location**: `libraries/AP_SerialManager/AP_SerialManager.h`
**Singleton**: `AP::serialmanager()`

## Parameters

Each serial port has parameters (SERIALn_ where n is port number):

| Parameter | Description |
|-----------|-------------|
| `SERIALn_PROTOCOL` | Protocol assigned to port |
| `SERIALn_BAUD` | Baud rate |
| `SERIALn_OPTIONS` | Port options (inverted, half-duplex, etc.) |

### Protocol Values

```cpp
enum SerialProtocol {
    SerialProtocol_None = -1,
    SerialProtocol_Console = 0,       // USB console
    SerialProtocol_MAVLink = 1,       // MAVLink (GCS)
    SerialProtocol_MAVLink2 = 2,      // MAVLink2 (use MAVLink with instance=1)
    SerialProtocol_FrSky_D = 3,       // FrSky D protocol
    SerialProtocol_FrSky_SPort = 4,   // FrSky SPort
    SerialProtocol_GPS = 5,           // GPS
    SerialProtocol_GPS2 = 6,          // GPS (use GPS with instance=1)
    SerialProtocol_AlexMos = 7,       // AlexMos gimbal
    SerialProtocol_Gimbal = 8,        // SToRM32/Siyi gimbal
    SerialProtocol_Rangefinder = 9,   // Rangefinder
    SerialProtocol_FrSky_SPort_Passthrough = 10,  // FrSky passthrough
    SerialProtocol_Lidar360 = 11,     // Proximity lidar
    SerialProtocol_Beacon = 13,       // Indoor positioning
    SerialProtocol_Volz = 14,         // Volz servo
    SerialProtocol_Sbus1 = 15,        // SBUS1 servo
    SerialProtocol_ESCTelemetry = 16, // ESC telemetry
    SerialProtocol_Devo_Telem = 17,   // Devo telemetry
    SerialProtocol_OpticalFlow = 18,  // Optical flow
    SerialProtocol_Robotis = 19,      // Robotis servo
    SerialProtocol_NMEAOutput = 20,   // NMEA GPS output
    SerialProtocol_WindVane = 21,     // Wind vane
    SerialProtocol_SLCAN = 22,        // CAN over serial
    SerialProtocol_RCIN = 23,         // RC input
    SerialProtocol_EFI = 24,          // EFI engine
    SerialProtocol_LTM_Telem = 25,    // LTM telemetry
    SerialProtocol_RunCam = 26,       // RunCam control
    SerialProtocol_Hott = 27,         // HoTT telemetry
    SerialProtocol_Scripting = 28,    // Lua scripting
    SerialProtocol_CRSF = 29,         // Crossfire/ELRS
    SerialProtocol_Generator = 30,    // Generator
    SerialProtocol_Winch = 31,        // Winch
    SerialProtocol_MSP = 32,          // MSP (Betaflight OSD)
    SerialProtocol_DJI_FPV = 33,      // DJI FPV OSD
    SerialProtocol_AirSpeed = 34,     // Serial airspeed
    SerialProtocol_ADSB = 35,         // ADSB receiver
    SerialProtocol_AHRS = 36,         // External AHRS
    SerialProtocol_SmartAudio = 37,   // VTX SmartAudio
    SerialProtocol_FETtecOneWire = 38,// FETtec ESC
    SerialProtocol_Torqeedo = 39,     // Torqeedo motor
    SerialProtocol_AIS = 40,          // AIS receiver
    SerialProtocol_CoDevESC = 41,     // CoDevESC
    SerialProtocol_MSP_DisplayPort = 42, // MSP DisplayPort
    SerialProtocol_MAVLinkHL = 43,    // MAVLink High Latency
    SerialProtocol_Tramp = 44,        // VTX Tramp
    SerialProtocol_DDS_XRCE = 45,     // DDS/XRCE (ROS2)
    SerialProtocol_IMUOUT = 46,       // IMU output
    SerialProtocol_PPP = 48,          // PPP networking
};
```

---

## Finding Serial Ports

### By Protocol

```cpp
// Find first serial port configured for GPS
AP_HAL::UARTDriver *uart = AP::serialmanager().find_serial(
    AP_SerialManager::SerialProtocol_GPS, 0);

// Find second GPS port
AP_HAL::UARTDriver *uart2 = AP::serialmanager().find_serial(
    AP_SerialManager::SerialProtocol_GPS, 1);

// Check if port exists
if (uart == nullptr) {
    return;  // No GPS port configured
}
```

### Check If Protocol Configured

```cpp
// Check if any port has this protocol
if (AP::serialmanager().have_serial(
        AP_SerialManager::SerialProtocol_Rangefinder, 0)) {
    // Rangefinder serial port exists
}
```

### Get Baud Rate

```cpp
uint32_t baud = AP::serialmanager().find_baudrate(
    AP_SerialManager::SerialProtocol_GPS, 0);
```

### Get Port Number

```cpp
// Get SERIALn index for a protocol
int8_t port_num = AP::serialmanager().find_portnum(
    AP_SerialManager::SerialProtocol_MAVLink, 0);
// Returns -1 if not found
```

---

## Port Access by ID

```cpp
// Direct access by SERIAL port number
AP_HAL::UARTDriver *uart = AP::serialmanager().get_serial_by_id(2);  // SERIAL2
```

---

## Port State

```cpp
// Get state for a protocol instance
const AP_SerialManager::UARTState *state =
    AP::serialmanager().find_protocol_instance(
        AP_SerialManager::SerialProtocol_MAVLink, 0);

if (state != nullptr) {
    uint32_t baud = state->baudrate();
    bool inverted = state->option_enabled(AP_HAL::UARTDriver::OPTION_RXINV);
}
```

---

## Initialization

```cpp
// In vehicle init
void Copter::init_ardupilot() {
    // Initialize console first
    serial_manager.init_console();

    // ... other init ...

    // Initialize all configured ports
    serial_manager.init();
}
```

---

## Common Usage Patterns

### GPS Driver

```cpp
void AP_GPS::init() {
    // Find all GPS ports
    for (uint8_t i = 0; i < GPS_MAX_INSTANCES; i++) {
        AP_HAL::UARTDriver *uart = AP::serialmanager().find_serial(
            AP_SerialManager::SerialProtocol_GPS, i);
        if (uart != nullptr) {
            // Initialize GPS driver on this port
            drivers[i] = new AP_GPS_UBLOX(*this, state[i], uart);
        }
    }
}
```

### Rangefinder Driver

```cpp
void AP_RangeFinder::init() {
    AP_HAL::UARTDriver *uart = AP::serialmanager().find_serial(
        AP_SerialManager::SerialProtocol_Rangefinder, 0);
    if (uart != nullptr) {
        // Create serial rangefinder driver
        drivers[0] = new AP_RangeFinder_LightWareSerial(state[0], uart);
    }
}
```

### Telemetry Output

```cpp
void AP_Frsky_Telem::init() {
    // Check for SPort passthrough first
    uart = AP::serialmanager().find_serial(
        AP_SerialManager::SerialProtocol_FrSky_SPort_Passthrough, 0);
    if (uart != nullptr) {
        _protocol = Protocol::SPORT_PASSTHROUGH;
        return;
    }

    // Check for regular SPort
    uart = AP::serialmanager().find_serial(
        AP_SerialManager::SerialProtocol_FrSky_SPort, 0);
    if (uart != nullptr) {
        _protocol = Protocol::SPORT;
        return;
    }
}
```

---

## Options

Port options set via SERIALn_OPTIONS:

```cpp
// Common options
#define OPTION_RXINV    (1U<<0)   // RX inverted
#define OPTION_TXINV    (1U<<1)   // TX inverted
#define OPTION_HDPLEX   (1U<<2)   // Half-duplex
#define OPTION_SWAP     (1U<<3)   // Swap TX/RX pins
#define OPTION_PULLDOWN (1U<<4)   // RX pulldown
#define OPTION_PULLUP   (1U<<5)   // RX pullup
#define OPTION_NODMA_TX (1U<<6)   // No DMA on TX
#define OPTION_NODMA_RX (1U<<7)   // No DMA on RX

// Check if option enabled
bool inverted = state->option_enabled(AP_HAL::UARTDriver::OPTION_RXINV);
```
