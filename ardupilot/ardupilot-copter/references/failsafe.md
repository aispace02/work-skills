# Failsafe Systems

## Overview

ArduCopter implements comprehensive failsafe systems to handle various failure conditions.

**Files**:
- `ArduCopter/failsafe.cpp`
- `ArduCopter/events.cpp`
- `ArduCopter/ekf_check.cpp`
- `ArduCopter/crash_check.cpp`

## Failsafe Types

| Failsafe | Parameter | Trigger |
|----------|-----------|---------|
| Radio | `FS_THR_ENABLE` | RC signal lost |
| GCS | `FS_GCS_ENABLE` | GCS heartbeat lost |
| Battery | `BATT_FS_*` | Low voltage/capacity |
| EKF | `FS_EKF_ACTION` | EKF variance too high |
| Terrain | `FS_TERRAIN_*` | Terrain data unavailable |
| Crash | `FS_CRASH_CHECK` | Crash detected |

## Failsafe Actions

```cpp
enum class FailsafeAction : uint8_t {
    NONE               = 0,
    LAND               = 1,
    RTL                = 2,
    SMARTRTL           = 3,
    SMARTRTL_LAND      = 4,
    TERMINATE          = 5,
    AUTO_DO_LAND_START = 6,
    BRAKE_LAND         = 7
};
```

## Radio Failsafe

### Configuration

| Parameter | Description |
|-----------|-------------|
| `FS_THR_ENABLE` | Action on radio failsafe |
| `FS_THR_VALUE` | PWM threshold for failsafe |

### Actions (FS_THR_ENABLE)

| Value | Action |
|-------|--------|
| 0 | Disabled |
| 1 | RTL |
| 3 | Land |
| 4 | SmartRTL or RTL |
| 5 | SmartRTL or Land |
| 6 | Auto DO_LAND_START or RTL |
| 7 | Brake then Land |

### Implementation

```cpp
void Copter::failsafe_radio_on_event() {
    // Determine action
    FailsafeAction desired_action;
    switch (g.failsafe_throttle) {
        case FS_THR_ENABLED_ALWAYS_RTL:
            desired_action = FailsafeAction::RTL;
            break;
        case FS_THR_ENABLED_ALWAYS_LAND:
            desired_action = FailsafeAction::LAND;
            break;
        // ... other cases
    }

    // Check exceptions
    if (should_disarm_on_failsafe()) {
        arming.disarm(AP_Arming::Method::RADIOFAILSAFE);
        return;
    }

    if (flightmode->is_landing() && failsafe_option(CONTINUE_IF_LANDING)) {
        desired_action = FailsafeAction::LAND;
    }

    // Execute action
    do_failsafe_action(desired_action, ModeReason::RADIO_FAILSAFE);
}
```

## GCS Failsafe

### Configuration

| Parameter | Description |
|-----------|-------------|
| `FS_GCS_ENABLE` | Action on GCS failsafe |
| `FS_GCS_TIMEOUT` | Timeout before failsafe (seconds) |

### Actions (FS_GCS_ENABLE)

| Value | Action |
|-------|--------|
| 0 | Disabled |
| 1 | RTL |
| 3 | SmartRTL or RTL |
| 4 | SmartRTL or Land |
| 5 | Land |
| 6 | Auto DO_LAND_START or RTL |
| 7 | Brake then Land |

### Implementation

```cpp
void Copter::failsafe_gcs_check() {
    const uint32_t last_gcs_update_ms = millis() - gcs_last_seen_ms;
    const uint32_t gcs_timeout_ms = g2.fs_gcs_timeout * 1000;

    if (last_gcs_update_ms < gcs_timeout_ms) {
        if (failsafe.gcs) {
            // Recovery
            set_failsafe_gcs(false);
            failsafe_gcs_off_event();
        }
    } else if (!failsafe.gcs) {
        // Trigger failsafe
        set_failsafe_gcs(true);
        failsafe_gcs_on_event();
    }
}
```

## Battery Failsafe

### Configuration

| Parameter | Description |
|-----------|-------------|
| `BATT_FS_LOW_ACT` | Low battery action |
| `BATT_FS_CRT_ACT` | Critical battery action |
| `BATT_LOW_VOLT` | Low voltage threshold |
| `BATT_CRT_VOLT` | Critical voltage threshold |
| `BATT_LOW_MAH` | Low capacity threshold |
| `BATT_CRT_MAH` | Critical capacity threshold |

### Implementation

```cpp
void Copter::handle_battery_failsafe(const char *type_str, const int8_t action) {
    FailsafeAction desired_action = (FailsafeAction)action;

    if (should_disarm_on_failsafe()) {
        arming.disarm(AP_Arming::Method::BATTERYFAILSAFE);
        return;
    }

    do_failsafe_action(desired_action, ModeReason::BATTERY_FAILSAFE);
}
```

## EKF Failsafe

### Configuration

| Parameter | Description |
|-----------|-------------|
| `FS_EKF_ACTION` | EKF failsafe action |
| `FS_EKF_THRESH` | Variance threshold |

### Actions (FS_EKF_ACTION)

| Value | Action |
|-------|--------|
| 0 | Report only |
| 1 | Land |
| 2 | AltHold |
| 3 | Land even in Stabilize |

### Implementation

```cpp
void Copter::ekf_check() {
    if (!ekf_over_threshold()) {
        // EKF OK
        if (failsafe.ekf) {
            failsafe_ekf_off_event();
        }
        return;
    }

    // EKF variance too high
    if (should_disarm_on_failsafe()) {
        arming.disarm(AP_Arming::Method::EKFFAILSAFE);
        return;
    }

    failsafe_ekf_event();
}

bool Copter::ekf_over_threshold() {
    // Check position and velocity variance
    return (pos_variance > fs_ekf_thresh || vel_variance > fs_ekf_thresh);
}
```

## Terrain Failsafe

Triggers when terrain data is unavailable in terrain-following modes.

```cpp
void Copter::failsafe_terrain_check() {
    if (!terrain.enabled()) return;

    if (terrain.status() == AP_Terrain::TerrainStatus::OK) {
        failsafe_terrain_set_status(true);
    } else {
        failsafe_terrain_set_status(false);
    }
}
```

## Crash Detection

### Thrust Loss

```cpp
void Copter::thrust_loss_check() {
    // Check if vehicle is losing altitude despite full throttle
    if (motors->limit.throttle_upper && rate_of_descent > threshold) {
        // Thrust loss detected
        if (option_is_enabled(FlightOption::RELEASE_GRIPPER_ON_THRUST_LOSS)) {
            // Release payload
        }
    }
}
```

### Crash Check

```cpp
void Copter::crash_check() {
    // Check for high angle error while on ground
    float angle_error = attitude_control->get_att_error_angle_deg();

    if (ap.land_complete_maybe && angle_error > threshold) {
        // Crash detected
        if (g.fs_crash_check == FS_CRASH_CHECK_ENABLED_DISARM) {
            arming.disarm(AP_Arming::Method::CRASH);
        }
    }
}
```

## Failsafe Options

```cpp
enum class FailsafeOption {
    RC_CONTINUE_IF_AUTO           = (1<<0),  // Continue AUTO if RC lost
    GCS_CONTINUE_IF_AUTO          = (1<<1),  // Continue AUTO if GCS lost
    RC_CONTINUE_IF_GUIDED         = (1<<2),  // Continue GUIDED if RC lost
    CONTINUE_IF_LANDING           = (1<<3),  // Continue landing
    GCS_CONTINUE_IF_PILOT_CONTROL = (1<<4),  // Continue if pilot has control
    RELEASE_GRIPPER               = (1<<5),  // Release gripper on failsafe
};
```

## Failsafe Priority

Actions are prioritized:

```cpp
static constexpr int8_t _failsafe_priorities[] = {
    (int8_t)FailsafeAction::TERMINATE,
    (int8_t)FailsafeAction::LAND,
    (int8_t)FailsafeAction::RTL,
    (int8_t)FailsafeAction::SMARTRTL_LAND,
    (int8_t)FailsafeAction::SMARTRTL,
    (int8_t)FailsafeAction::NONE,
    -1  // Sentinel
};
```

## Failsafe Action Execution

```cpp
void Copter::do_failsafe_action(FailsafeAction action, ModeReason reason) {
    switch (action) {
        case FailsafeAction::NONE:
            break;
        case FailsafeAction::LAND:
            set_mode_land_with_pause(reason);
            break;
        case FailsafeAction::RTL:
            set_mode(Mode::Number::RTL, reason);
            break;
        case FailsafeAction::SMARTRTL:
            set_mode_SmartRTL_or_RTL(reason);
            break;
        case FailsafeAction::SMARTRTL_LAND:
            set_mode_SmartRTL_or_land_with_pause(reason);
            break;
        case FailsafeAction::TERMINATE:
            arming.disarm(AP_Arming::Method::FAILSAFE_ACTION_TERMINATE);
            break;
    }
}
```

## Checking Failsafes

```cpp
bool Copter::any_failsafe_triggered() const {
    return failsafe.radio
        || battery.has_failsafed()
        || failsafe.gcs
        || failsafe.ekf
        || failsafe.terrain
        || failsafe.adsb
        || failsafe.deadreckon;
}
```
