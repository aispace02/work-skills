# AntennaTracker Architecture

## Overview

The AntennaTracker is a stationary ground system that automatically points a directional antenna at a moving vehicle. It receives position data via MAVLink telemetry and controls pan (yaw) and tilt (pitch) servos.

## System Architecture

```
                    ┌─────────────────────────────────────────────────┐
                    │              AntennaTracker                      │
                    │                                                  │
  RC Input ────────►│  ┌─────────┐    ┌──────────┐    ┌──────────┐   │
                    │  │  Mode   │───►│ Tracking │───►│  Servos  │───┼──► Pan Servo
  MAVLink ─────────►│  │ Manager │    │  Logic   │    │ Control  │───┼──► Tilt Servo
  (Vehicle Pos)     │  └─────────┘    └──────────┘    └──────────┘   │
                    │       │              │               │          │
                    │       ▼              ▼               ▼          │
                    │  ┌─────────┐    ┌──────────┐    ┌──────────┐   │
                    │  │  AHRS   │    │   PID    │    │  Servo   │   │
                    │  │(Heading)│    │ Control  │    │  Output  │   │
                    │  └─────────┘    └──────────┘    └──────────┘   │
                    └─────────────────────────────────────────────────┘
```

## Main Class: Tracker

**Files**: `Tracker.h`, `Tracker.cpp`

```cpp
class Tracker : public AP_Vehicle {
public:
    // Mode management
    Mode *mode_from_mode_num(Mode::Number num);
    bool set_mode(Mode &newmode, ModeReason reason);

    // Servo control
    void update_pitch_servo(float pitch);
    void update_yaw_servo(float yaw);

    // Tracking
    void update_vehicle_pos_estimate();
    void update_bearing_and_distance();

    // State
    NavStatus nav_status;
    VehicleState vehicle;

    // Modes
    ModeAuto mode_auto;
    ModeGuided mode_guided;
    ModeManual mode_manual;
    ModeScan mode_scan;
    ModeServoTest mode_servotest;
    ModeStop mode_stop;
    ModeInitialising mode_initialising;

    // Parameters
    Parameters g;
};
```

## Data Structures

### NavStatus
```cpp
struct NavStatus {
    float bearing;              // Target bearing (degrees)
    float distance;             // Target distance (m)
    float pitch;                // Target pitch (degrees)
    float angle_error_pitch;    // Pitch error (centidegrees)
    float angle_error_yaw;      // Yaw error (centidegrees)
    bool manual_control_yaw;    // Manual yaw override
    bool manual_control_pitch;  // Manual pitch override
    bool scan_reverse_yaw;      // Scan direction
    bool scan_reverse_pitch;    // Scan direction
};
```

### VehicleState
```cpp
struct VehicleState {
    Location location;          // Vehicle location
    Vector3f vel;               // Velocity (m/s)
    uint32_t location_time_ms;  // Last update time
    bool location_valid;        // Position validity
    bool initialised;           // Tracking initialized
};
```

## Main Loop

```cpp
void Tracker::loop() {
    // 50Hz main loop

    // Read sensors
    ins.update();
    ahrs.update();

    // Read vehicle telemetry
    update_vehicle_pos_estimate();
    update_bearing_and_distance();

    // Run current mode
    mode->update();

    // Update logging
    Log_Write_Attitude();
    Log_Write_Nav_Status();
}
```

## Scheduler Tasks

| Task | Rate (Hz) | Purpose |
|------|-----------|---------|
| `ins_update` | 50 | IMU updates |
| `ahrs_update` | 50 | Attitude estimation |
| `tracking_update` | 1 | Vehicle position update |
| `compass_save` | 0.02 | Save compass offsets |
| `update_notify` | 50 | LED/buzzer updates |
| `gcs_send_message` | 50 | MAVLink output |
| `gcs_data_stream_send` | 50 | Data streaming |
| `one_second_loop` | 1 | Periodic housekeeping |
| `ten_hz_logging` | 10 | Logging |

## File Structure

```
AntennaTracker/
├── Tracker.h/cpp           # Main class
├── mode.h                  # Mode base class
├── mode.cpp                # Mode utilities
├── mode_auto.cpp           # Auto tracking mode
├── mode_guided.cpp         # GCS-guided mode
├── mode_manual.cpp         # RC pass-through
├── mode_scan.cpp           # Scanning mode
├── mode_servotest.cpp      # Servo test mode
├── servos.cpp              # Servo control
├── tracking.cpp            # Vehicle tracking
├── Parameters.h/cpp        # Parameters
├── GCS_Tracker.h/cpp       # GCS class
├── GCS_MAVLink_Tracker.cpp # MAVLink handling
├── Log.cpp                 # Logging
└── system.cpp              # System init
```

## Coordinate Systems

### Earth Frame (EF)
- Yaw: 0-360 degrees clockwise from north
- Pitch: -90 (down) to +90 (up) degrees

### Body Frame (BF)
- Accounts for tracker mounting angle
- Converted from earth frame for servo output

### Conversion
```cpp
// Earth to body frame
bf_pitch = cos_roll * ef_pitch + sin_roll * cos_pitch * ef_yaw;
bf_yaw = -sin_roll * ef_pitch + cos_pitch * cos_roll * ef_yaw;

// Body to earth frame
ef_pitch = cos_roll * bf_pitch - sin_roll * bf_yaw;
ef_yaw = (sin_roll / cos_pitch) * bf_pitch + (cos_roll / cos_pitch) * bf_yaw;
```

## Control Flow

```
1. MAVLink message received
   └── GCS_MAVLink_Tracker::handle_message()
       └── handle_global_position_int() / handle_set_attitude_target()

2. Vehicle position updated
   └── Tracker::update_vehicle_pos_estimate()
       └── Extrapolate position using velocity

3. Bearing/distance calculated
   └── Tracker::update_bearing_and_distance()
       └── get_bearing_cd(), get_horizontal_distance_cm()

4. Mode update called
   └── Mode::update()
       └── ModeAuto::update() / ModeScan::update() / etc.
           └── Mode::update_auto() or Mode::update_scan()

5. Angle error calculated
   └── Mode::calc_angle_error()
       └── Compare target to actual attitude

6. Servo output
   └── Tracker::update_pitch_servo() / update_yaw_servo()
       └── Apply PID, slew rate limits, output PWM
```

## Dependencies

### ArduPilot Libraries Used
- `AP_Vehicle` - Base vehicle class
- `AP_AHRS` - Attitude and heading reference
- `AP_GPS` - GPS interface
- `AP_Baro` - Barometer
- `AP_Compass` - Compass
- `AC_PID` - PID controllers
- `SRV_Channel` - Servo output
- `RC_Channel` - RC input
- `GCS_MAVLink` - MAVLink communication
