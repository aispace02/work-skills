# Failsafe Systems

## Overview

ArduSub implements multiple failsafe systems specific to underwater operation.

**File**: `ArduSub/failsafe.cpp`

## Failsafe Types

| Failsafe | Parameter | Actions |
|----------|-----------|---------|
| Leak | `FS_LEAK_ENABLE` | Warn, Surface |
| Pressure | `FS_PRESS_ENABLE` | Warn |
| Temperature | `FS_TEMP_ENABLE` | Warn |
| GCS | `FS_GCS_ENABLE` | Warn, Disarm, Hold, Surface |
| EKF | `FS_EKF_ACTION` | Warn, Disarm |
| Pilot Input | `FS_PILOT_INPUT` | Warn, Disarm |
| Terrain | `FS_TERRAIN_ENABLE` | Disarm, Hold, Surface |
| Crash | `FS_CRASH_CHECK` | Warn, Disarm |
| Sensor | Internal | Mode change |

## Leak Failsafe

### Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `FS_LEAK_ENABLE` | Enable leak failsafe | 1 |
| `LEAK1_PIN` | Leak detector 1 pin | -1 |
| `LEAK2_PIN` | Leak detector 2 pin | -1 |
| `LEAK3_PIN` | Leak detector 3 pin | -1 |

### Actions

| Value | Action |
|-------|--------|
| 0 | Disabled |
| 1 | Warn only |
| 2 | Surface |

### Implementation

```cpp
void Sub::failsafe_leak_check() {
    // Check leak detector
    if (!leak_detector.get_status()) {
        return;  // No leak
    }

    // Already in failsafe?
    if (failsafe.leak) {
        return;
    }

    failsafe.leak = true;
    LOGGER_WRITE_ERROR(LogErrorSubsystem::FAILSAFE_LEAK, LogErrorCode::FAILSAFE_OCCURRED);
    gcs().send_text(MAV_SEVERITY_CRITICAL, "Leak Detected");

    // Take action
    if (g.failsafe_leak == FS_LEAK_SURFACE && motors.armed()) {
        set_mode(Mode::Number::SURFACE, ModeReason::LEAK_FAILSAFE);
    }
}
```

## Internal Pressure Failsafe

Monitors internal enclosure pressure.

### Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `FS_PRESS_ENABLE` | Enable pressure failsafe | 0 |
| `FS_PRESS_MAX` | Max pressure (Pa) | 105000 |

### Implementation

```cpp
void Sub::failsafe_internal_pressure_check() {
    if (g.failsafe_pressure == FS_PRESS_DISABLED) {
        return;
    }

    if (AP::baro().get_pressure() < g.failsafe_pressure_max) {
        failsafe.internal_pressure = false;
        return;
    }

    // Pressure exceeded
    if (!failsafe.internal_pressure) {
        failsafe.internal_pressure = true;
        gcs().send_text(MAV_SEVERITY_WARNING, "Internal pressure critical!");
        LOGGER_WRITE_ERROR(LogErrorSubsystem::FAILSAFE_SENSORS,
                          LogErrorCode::HIGH_INTERNAL_PRESSURE);
    }
}
```

## Internal Temperature Failsafe

Monitors internal enclosure temperature.

### Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `FS_TEMP_ENABLE` | Enable temperature failsafe | 0 |
| `FS_TEMP_MAX` | Max temperature (C) | 62 |

### Implementation

```cpp
void Sub::failsafe_internal_temperature_check() {
    if (g.failsafe_temperature == FS_TEMP_DISABLED) {
        return;
    }

    if (AP::baro().get_temperature() < g.failsafe_temperature_max) {
        failsafe.internal_temperature = false;
        return;
    }

    // Temperature exceeded
    if (!failsafe.internal_temperature) {
        failsafe.internal_temperature = true;
        gcs().send_text(MAV_SEVERITY_WARNING, "Internal temperature critical!");
        LOGGER_WRITE_ERROR(LogErrorSubsystem::FAILSAFE_SENSORS,
                          LogErrorCode::HIGH_INTERNAL_TEMP);
    }
}
```

## GCS Failsafe

Triggers when GCS heartbeat is lost.

### Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `FS_GCS_ENABLE` | Enable GCS failsafe | 0 |
| `FS_GCS_TIMEOUT` | Timeout (seconds) | 5.0 |

### Actions

| Value | Action |
|-------|--------|
| 0 | Disabled |
| 1 | Warn only |
| 2 | Disarm |
| 3 | Hold (depth or position) |
| 4 | Surface |

### Implementation

```cpp
void Sub::failsafe_gcs_check() {
    if (g.failsafe_gcs == FS_GCS_DISABLED) {
        return;
    }

    uint32_t tnow = AP_HAL::millis();
    uint32_t last_gcs = gcs().sysid_myggcs_last_seen_time_ms();

    if (tnow - last_gcs < g.failsafe_gcs_timeout * 1000) {
        // GCS OK
        if (failsafe.gcs) {
            failsafe.gcs = false;
            LOGGER_WRITE_ERROR(LogErrorSubsystem::FAILSAFE_GCS,
                              LogErrorCode::FAILSAFE_RESOLVED);
        }
        return;
    }

    // GCS lost
    if (!failsafe.gcs) {
        failsafe.gcs = true;
        gcs().send_text(MAV_SEVERITY_WARNING, "GCS Failsafe");
        LOGGER_WRITE_ERROR(LogErrorSubsystem::FAILSAFE_GCS,
                          LogErrorCode::FAILSAFE_OCCURRED);

        switch (g.failsafe_gcs) {
            case FS_GCS_DISARM:
                arming.disarm(AP_Arming::Method::GCSFAILSAFE);
                break;
            case FS_GCS_HOLD:
                if (sub.position_ok()) {
                    set_mode(Mode::Number::POSHOLD, ModeReason::GCS_FAILSAFE);
                } else {
                    set_mode(Mode::Number::ALT_HOLD, ModeReason::GCS_FAILSAFE);
                }
                break;
            case FS_GCS_SURFACE:
                set_mode(Mode::Number::SURFACE, ModeReason::GCS_FAILSAFE);
                break;
        }
    }
}
```

## Pilot Input Failsafe

Triggers when pilot input (joystick) is lost.

### Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `FS_PILOT_INPUT` | Enable pilot input failsafe | 0 |
| `FS_PILOT_TIMEOUT` | Timeout (seconds) | 3.0 |

### Actions

| Value | Action |
|-------|--------|
| 0 | Disabled |
| 1 | Warn only |
| 2 | Disarm |

### Implementation

```cpp
void Sub::failsafe_pilot_input_check() {
    if (g.failsafe_pilot_input == FS_PILOT_INPUT_DISABLED) {
        return;
    }

    uint32_t tnow = AP_HAL::millis();

    if (tnow - failsafe.last_pilot_input_ms < g.failsafe_pilot_input_timeout * 1000) {
        // Input OK
        if (failsafe.pilot_input) {
            failsafe.pilot_input = false;
            gcs().send_text(MAV_SEVERITY_INFO, "Pilot input restored");
        }
        return;
    }

    // Input lost
    if (!failsafe.pilot_input) {
        failsafe.pilot_input = true;
        gcs().send_text(MAV_SEVERITY_WARNING, "Pilot input failsafe");

        if (g.failsafe_pilot_input == FS_PILOT_INPUT_DISARM && motors.armed()) {
            arming.disarm(AP_Arming::Method::PILOT_INPUT_FAILSAFE);
        }
    }
}
```

## EKF Failsafe

Triggers when EKF estimation becomes unreliable.

### Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `FS_EKF_ACTION` | EKF failsafe action | 0 |
| `FS_EKF_THRESH` | Variance threshold | 0.8 |

### Actions

| Value | Action |
|-------|--------|
| 0 | Disabled |
| 1 | Warn only |
| 2 | Disarm |

### Implementation

```cpp
void Sub::failsafe_ekf_check() {
    if (g.fs_ekf_action == FS_EKF_ACTION_DISABLED) {
        return;
    }

    float posVar, hgtVar, tasVar;
    Vector3f magVar;
    float compass_variance, vel_variance;
    ahrs.get_variances(vel_variance, posVar, hgtVar, magVar, tasVar);
    compass_variance = magVar.length();

    if (compass_variance < g.fs_ekf_thresh && vel_variance < g.fs_ekf_thresh) {
        last_ekf_good_ms = AP_HAL::millis();
        failsafe.ekf = false;
        return;
    }

    // Bad EKF for 2 seconds triggers failsafe
    if (AP_HAL::millis() < last_ekf_good_ms + 2000) {
        return;
    }

    if (!failsafe.ekf) {
        failsafe.ekf = true;
        gcs().send_text(MAV_SEVERITY_WARNING, "EKF bad");
        LOGGER_WRITE_ERROR(LogErrorSubsystem::EKFCHECK,
                          LogErrorCode::EKFCHECK_BAD_VARIANCE);

        if (g.fs_ekf_action == FS_EKF_ACTION_DISARM) {
            arming.disarm(AP_Arming::Method::EKFFAILSAFE);
        }
    }
}
```

## Sensor Failsafe

Triggers when depth sensor fails in depth-dependent modes.

```cpp
void Sub::failsafe_sensors_check() {
    if (!ap.depth_sensor_present) {
        return;
    }

    if (sensor_health.depth) {
        if (failsafe.sensor_health) {
            failsafe.sensor_health = false;
            LOGGER_WRITE_ERROR(LogErrorSubsystem::FAILSAFE_SENSORS,
                              LogErrorCode::ERROR_RESOLVED);
        }
        return;
    }

    // Depth sensor failed
    if (!failsafe.sensor_health) {
        failsafe.sensor_health = true;
        gcs().send_text(MAV_SEVERITY_CRITICAL, "Depth sensor error!");
        LOGGER_WRITE_ERROR(LogErrorSubsystem::FAILSAFE_SENSORS,
                          LogErrorCode::BAD_DEPTH);

        // Switch to MANUAL if in depth-dependent mode
        if (control_mode == Mode::Number::ALT_HOLD ||
            control_mode == Mode::Number::SURFACE ||
            flightmode->requires_GPS()) {
            set_mode(Mode::Number::MANUAL, ModeReason::BAD_DEPTH);
        }
    }
}
```

## Terrain Failsafe

Triggers when terrain data is unavailable in terrain-following modes.

### Actions

| Value | Action |
|-------|--------|
| 0 | Disarm |
| 1 | Hold position |
| 2 | Surface |

## Crash Failsafe

Detects abnormal accelerations indicating impact.

```cpp
void Sub::failsafe_crash_check() {
    if (g.fs_crash_check == FS_CRASH_DISABLED) {
        return;
    }

    // Check for abnormal accelerations
    if (crash_detected()) {
        if (!failsafe.crash) {
            failsafe.crash = true;
            gcs().send_text(MAV_SEVERITY_CRITICAL, "Crash detected");

            if (g.fs_crash_check == FS_CRASH_DISARM) {
                arming.disarm(AP_Arming::Method::CRASH);
            }
        }
    }
}
```

## Failsafe Priority

When multiple failsafes trigger, highest priority action is taken:

```cpp
static constexpr int8_t _failsafe_priorities[] = {
    Failsafe_Action_Disarm,   // Highest priority
    Failsafe_Action_Surface,
    Failsafe_Action_Warn,
    Failsafe_Action_None,
    -1  // Sentinel
};
```

## Checking Any Failsafe

```cpp
bool Sub::any_failsafe_triggered() const {
    return (
        failsafe.pilot_input
        || battery.has_failsafed()
        || failsafe.gcs
        || failsafe.ekf
        || failsafe.terrain
        || failsafe.leak
        || failsafe.internal_pressure
        || failsafe.internal_temperature
        || failsafe.crash
        || failsafe.sensor_health
    );
}
```

## Mainloop Failsafe

Detects if main loop has locked up:

```cpp
void Sub::mainloop_failsafe_check() {
    if (tnow - failsafe_last_timestamp > 2000000) {
        // 2 seconds without mainloop
        in_failsafe = true;
        motors.output_min();
        LOGGER_WRITE_ERROR(LogErrorSubsystem::CPU,
                          LogErrorCode::FAILSAFE_OCCURRED);
    }

    if (in_failsafe && tnow - failsafe_last_timestamp > 1000000) {
        // Disarm every second while locked up
        motors.armed(false);
        motors.output();
    }
}
```
