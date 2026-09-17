# Alternative Telemetry Protocols

Non-MAVLink telemetry protocols for RC receivers, OSDs, and other devices.

## FrSky Telemetry

**Library**: `libraries/AP_Frsky_Telem/`
**Protocols**: FrSky D, FrSky SPort, SPort Passthrough

### Configuration

| SERIALn_PROTOCOL | Mode |
|------------------|------|
| 3 | FrSky D (D-receivers) |
| 4 | FrSky SPort (X-receivers) |
| 10 | SPort Passthrough (OpenTX scripts) |

### SPort Passthrough

Most common mode - sends rich telemetry compatible with OpenTX/EdgeTX Lua scripts.

```cpp
// Telemetry data includes:
// - GPS position, speed, heading
// - Attitude (roll, pitch, yaw)
// - Battery voltage, current, capacity
// - Flight mode, arm status
// - Altitude (baro and GPS)
// - Vibration, temperature
// - Custom sensors
```

### Custom Sensors

Add custom FrSky sensors via Lua scripting:

```cpp
// From Lua script
frsky_sport:get_value(sensor_id)

// Sensor IDs in AP_Frsky_SPort.h
```

---

## CRSF / ELRS Telemetry

**Library**: `libraries/AP_RCTelemetry/`
**Protocol**: Crossfire (TBS) / ExpressLRS

### Configuration

```
SERIALn_PROTOCOL = 29  (CRSF)
SERIALn_OPTIONS = 0    (non-inverted)
SERIALn_BAUD = 416     (416000 baud for CRSF)
```

### Telemetry Data

CRSF telemetry includes:
- GPS position and ground speed
- Attitude (pitch, roll)
- Battery voltage/current/remaining
- Flight mode
- Link quality (RSSI, SNR)

### ELRS Differences

ExpressLRS uses CRSF protocol but with:
- Lower bandwidth (50-500Hz link rate)
- Optimized packet structure
- Telemetry ratio setting affects data rate

---

## MSP Telemetry (Betaflight OSD)

**Library**: `libraries/AP_MSP/`
**Protocol**: MultiWii Serial Protocol

### Configuration

```
SERIALn_PROTOCOL = 32  (MSP)
```

### Use Case

Feed telemetry data to Betaflight-compatible OSDs (e.g., built into VTX).

### Supported Data

```cpp
// MSP telemetry provides:
// - GPS data
// - Battery voltage/current
// - Altitude
// - Flight mode (mapped to BF modes)
// - RSSI
// - Arm status
```

### DJI FPV OSD

```
SERIALn_PROTOCOL = 33  (DJI_FPV)
```

Uses MSP protocol variant for DJI FPV goggles/air units.

---

## LTM Telemetry

**Library**: `libraries/AP_LTM_Telem/`
**Protocol**: Lightweight TeleMetry

### Configuration

```
SERIALn_PROTOCOL = 25  (LTM)
```

### Use Case

Simple, low-bandwidth telemetry for basic ground stations and antenna trackers.

### Frame Types

| Frame | Content | Rate |
|-------|---------|------|
| G | GPS position | 2Hz |
| A | Attitude | 5Hz |
| S | Status (voltage, RSSI, mode) | 2Hz |
| O | Origin (home position) | 1Hz |
| N | Navigation (GPS fix, sat count) | 2Hz |

---

## Devo Telemetry

**Library**: `libraries/AP_Devo_Telem/`
**Protocol**: Walkera Devo

### Configuration

```
SERIALn_PROTOCOL = 17  (Devo)
```

### Use Case

Telemetry for Walkera Devo transmitters.

---

## HoTT Telemetry

**Library**: via AP_RCTelemetry
**Protocol**: Graupner HoTT

### Configuration

```
SERIALn_PROTOCOL = 27  (HoTT)
```

---

## DisplayPort / Canvas Mode

**Library**: `libraries/AP_MSP/`
**Protocol**: MSP DisplayPort

### Configuration

```
SERIALn_PROTOCOL = 42  (MSP_DisplayPort)
```

### Use Case

Direct OSD rendering on HD FPV systems (DJI O3, HDZero, etc.).

ArduPilot sends OSD graphics commands directly to the display system instead of pre-rendered character maps.

### Enabling

```
OSD_TYPE = 5  (MSP_DISPLAYPORT)
```

---

## Implementing New Telemetry

### Pattern

```cpp
class AP_MyTelem {
public:
    void init();
    void update();      // Called from scheduler

private:
    AP_HAL::UARTDriver *_port;

    void send_frame();
    void send_gps();
    void send_attitude();
};

void AP_MyTelem::init() {
    _port = AP::serialmanager().find_serial(
        AP_SerialManager::SerialProtocol_MyProtocol, 0);
}

void AP_MyTelem::update() {
    if (_port == nullptr) return;

    // Send telemetry frames
    send_gps();
    send_attitude();
}
```

### Adding Protocol

1. Add to `SerialProtocol` enum in `AP_SerialManager.h`
2. Create library with protocol implementation
3. Initialize in vehicle code
4. Add to scheduler

---

## VTX Control Protocols

### SmartAudio

```
SERIALn_PROTOCOL = 37  (SmartAudio)
```

Control VTX power, channel, band via TBS SmartAudio.

### Tramp

```
SERIALn_PROTOCOL = 44  (Tramp)
```

Control VTX via IRC Tramp protocol.
