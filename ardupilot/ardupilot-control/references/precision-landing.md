# Precision Landing

Autonomous precision landing on visual/IR targets.

## AC_PrecLand

**Location**: `libraries/AC_PrecLand/AC_PrecLand.h`

**Singleton**: `AC_PrecLand::get_singleton()`

### Backend Types

```cpp
enum PrecLandType {
    PRECLAND_TYPE_NONE        = 0,
    PRECLAND_TYPE_COMPANION   = 1,   // Companion computer
    PRECLAND_TYPE_IRLOCK      = 2,   // IR-LOCK sensor
    PRECLAND_TYPE_SITL_GAZEBO = 3,   // Gazebo simulation
    PRECLAND_TYPE_SITL        = 4,   // SITL simulation
};
```

### State Machine

```cpp
enum class Status {
    NOT_STARTED,
    SEARCHING,      // Looking for target
    DESCENDING,     // Target acquired, descending
    FINAL_APPROACH, // Close to ground
    RETRYING,       // Lost target, retrying
    COMPLETE,
    FAILED
};
```

### Core Methods

```cpp
// Lifecycle
void init(uint16_t update_rate_hz);
void update(float rangefinder_alt, bool rangefinder_valid);

// Target state
bool target_acquired();                           // Is target visible?
bool get_target_position_m(Vector3f &pos);        // Target position (NED)
bool get_target_velocity_relative_NE_ms(Vector2f &vel);  // Target velocity

// State
Status get_status() const;
bool healthy() const;

// Configuration
void set_backend(PrecLandType type);
```

### Parameters (PLND_)

| Parameter | Description |
|-----------|-------------|
| `PLND_ENABLED` | Enable precision landing |
| `PLND_TYPE` | Backend type (0-4) |
| `PLND_EST_TYPE` | Estimator (0=Raw, 1=Kalman) |
| `PLND_LAG` | Sensor lag (s) |
| `PLND_YAW_ALIGN` | Sensor yaw alignment (deg) |
| `PLND_LAND_OFS_X` | Landing offset X (m) |
| `PLND_LAND_OFS_Y` | Landing offset Y (m) |
| `PLND_CAM_OFFSET` | Camera offset from CG |
| `PLND_STRICT` | Strict target tracking |
| `PLND_RETRY_MAX` | Max retry attempts |
| `PLND_RETRY_TIMEOUT` | Retry timeout (s) |

### Usage

```cpp
void mode_precland_init() {
    AC_PrecLand *precland = AC_PrecLand::get_singleton();
    precland->init(400);  // 400Hz update rate
}

void mode_precland_run() {
    AC_PrecLand *precland = AC_PrecLand::get_singleton();
    AC_PosControl *pos = AC_PosControl::get_singleton();

    // Update with rangefinder data
    RangeFinder *rf = AP::rangefinder();
    float rf_alt = rf->distance_orient(ROTATION_PITCH_270);
    bool rf_valid = rf->status_orient(ROTATION_PITCH_270) == RangeFinder::Status::Good;

    precland->update(rf_alt, rf_valid);

    // Check target state
    if (precland->target_acquired()) {
        Vector3f target_pos;
        if (precland->get_target_position_m(target_pos)) {
            // Navigate toward target
            pos->input_pos_NED_m(target_pos, 0, 0);
        }
    } else {
        // Hold position while searching
        pos->set_pos_target_to_stopping_point();
    }

    // Run controllers
    pos->update_estimates();
    pos->NE_update_controller();
    pos->D_update_controller();
    attitude_control->input_euler_angle_roll_pitch_yaw(
        pos->get_roll_cd(), pos->get_pitch_cd(), yaw_cd, true);
    attitude_control->rate_controller_run();
}
```

### State Machine Handling

```cpp
void handle_precland_status() {
    AC_PrecLand *precland = AC_PrecLand::get_singleton();

    switch (precland->get_status()) {
        case AC_PrecLand::Status::NOT_STARTED:
            // Initialize landing
            break;

        case AC_PrecLand::Status::SEARCHING:
            // Hold position, look for target
            break;

        case AC_PrecLand::Status::DESCENDING:
            // Target acquired, descending
            break;

        case AC_PrecLand::Status::FINAL_APPROACH:
            // Close to ground, final corrections
            break;

        case AC_PrecLand::Status::RETRYING:
            // Lost target, climb and retry
            break;

        case AC_PrecLand::Status::COMPLETE:
            // Landed successfully
            break;

        case AC_PrecLand::Status::FAILED:
            // Switch to normal land
            break;
    }
}
```

### Integration with Land Mode

```cpp
void mode_land_run() {
    AC_PrecLand *precland = AC_PrecLand::get_singleton();

    // Check if precision landing is enabled and target acquired
    if (precland != nullptr && precland->target_acquired()) {
        // Use precision landing position
        Vector3f target_pos;
        precland->get_target_position_m(target_pos);
        pos_control->input_pos_NE_m(Vector2f(target_pos.x, target_pos.y));
    } else {
        // Normal landing - hold horizontal position
        pos_control->input_pos_NE_m(landing_pos);
    }

    // Continue descent
    pos_control->input_pos_D_m(descent_target, descent_speed, descent_accel);
}
```
