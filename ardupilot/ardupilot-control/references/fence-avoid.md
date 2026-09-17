# Geofencing & Avoidance

Safety systems for boundary enforcement and obstacle avoidance.

## AC_Fence

**Location**: `libraries/AC_Fence/AC_Fence.h`

**Singleton**: `AC_Fence::get_singleton()`

### Fence Types

```cpp
enum AC_FENCE_TYPE {
    AC_FENCE_TYPE_ALT_MAX  = 1,   // Maximum altitude
    AC_FENCE_TYPE_CIRCLE   = 2,   // Circular boundary
    AC_FENCE_TYPE_POLYGON  = 4,   // Polygon boundary
    AC_FENCE_TYPE_ALT_MIN  = 8,   // Minimum altitude
};
```

### Breach Actions

```cpp
enum AC_FENCE_ACTION {
    AC_FENCE_ACTION_REPORT_ONLY     = 0,
    AC_FENCE_ACTION_RTL_AND_LAND    = 1,
    AC_FENCE_ACTION_ALWAYS_LAND     = 2,
    AC_FENCE_ACTION_SMART_RTL       = 3,
    AC_FENCE_ACTION_BRAKE           = 4,
    AC_FENCE_ACTION_GUIDED          = 5,
    AC_FENCE_ACTION_GUIDED_THR_PASS = 6,
};
```

### Core Methods

```cpp
// Enable/disable
void enable(bool enable);
bool enabled() const;

// Breach detection (call at 10Hz)
uint8_t check();                              // Returns bitmask of breaches
uint8_t get_breaches() const;

// Fence info
uint8_t get_enabled_fences() const;
float get_safe_alt_max() const;               // meters
float get_safe_alt_min() const;
float get_radius() const;                     // Circular fence radius
float get_margin() const;                     // Warning margin

// Polygon
bool polygon_fence_is_in_area(Location &loc) const;
uint8_t polyfence_points() const;

// Pre-arm
bool pre_arm_check(char *failure_msg, uint8_t failure_msg_len);

// Auto enable/disable
void auto_enable_fence_after_takeoff();
void auto_disable_fence_for_landing();
```

### Parameters (FENCE_)

| Parameter | Description |
|-----------|-------------|
| `FENCE_ENABLE` | Enable fence (bitmask) |
| `FENCE_TYPE` | Fence types (1=Alt, 2=Circle, 4=Poly, 8=AltMin) |
| `FENCE_ACTION` | Breach action (0-6) |
| `FENCE_ALT_MAX` | Maximum altitude (m) |
| `FENCE_ALT_MIN` | Minimum altitude (m) |
| `FENCE_RADIUS` | Circular fence radius (m) |
| `FENCE_MARGIN` | Warning margin (m) |
| `FENCE_RET_RALLY` | RTL to rally point |
| `FENCE_OPTIONS` | Options bitmask |

### Usage

```cpp
void check_fence() {
    AC_Fence *fence = AC_Fence::get_singleton();

    uint8_t breaches = fence->check();
    if (breaches != 0) {
        if (breaches & AC_FENCE_TYPE_ALT_MAX) {
            gcs().send_text(MAV_SEVERITY_WARNING, "Altitude fence breach");
        }
        if (breaches & AC_FENCE_TYPE_CIRCLE) {
            gcs().send_text(MAV_SEVERITY_WARNING, "Circular fence breach");
        }
        if (breaches & AC_FENCE_TYPE_POLYGON) {
            gcs().send_text(MAV_SEVERITY_WARNING, "Polygon fence breach");
        }

        // Trigger failsafe action
        trigger_fence_failsafe();
    }
}

bool pre_arm_fence_check(char *msg, uint8_t len) {
    AC_Fence *fence = AC_Fence::get_singleton();
    return fence->pre_arm_check(msg, len);
}
```

---

## AC_Avoid

**Location**: `libraries/AC_Avoidance/AC_Avoid.h`

**Singleton**: `AC_Avoid::get_singleton()`

### Avoidance Sources

```cpp
enum AVOID_ENABLE {
    AVOID_ENABLE_PROXIMITY = 1,   // Proximity sensors
    AVOID_ENABLE_FENCE     = 2,   // Fence boundaries
    AVOID_ENABLE_BEACON    = 4,   // Beacon boundaries
};
```

### Core Methods

```cpp
// Main velocity adjustment (modifies vel in-place)
void adjust_velocity(Vector3f &vel_cms, float kP, float accel_cmss,
                     AC_PosControl *pos_control, float dt);

// Component-specific
void adjust_velocity_fence(Vector3f &vel_cms, float kP, float accel_cmss,
                           float dt, float &margin);
void adjust_velocity_proximity(Vector3f &vel_cms, float kP, float accel_cmss,
                               float dt, bool horizontal_only);
void adjust_velocity_beacon(Vector3f &vel_cms, float kP, float accel_cmss,
                            float dt, float &margin);

// Vertical avoidance
void adjust_velocity_z(float &vel_z_cms, float dt);

// Angle-based avoidance (for attitude modes)
void adjust_roll_pitch_rad(float &roll, float &pitch, float veh_angle_max);

// Speed limiting
void adjust_speed(float &speed, float dt);

// State
bool limits_active() const;
```

### Parameters (AVOID_)

| Parameter | Description |
|-----------|-------------|
| `AVOID_ENABLE` | What to avoid (1=Prox, 2=Fence, 4=Beacon) |
| `AVOID_ANGLE_MAX` | Max lean angle for avoidance (deg) |
| `AVOID_DIST_MAX` | Max distance to start avoiding (m) |
| `AVOID_MARGIN` | Minimum margin from obstacles (m) |
| `AVOID_BEHAVE` | Behavior (0=Slide, 1=Stop) |
| `AVOID_BACKUP_SPD` | Backup speed when stopping (m/s) |
| `AVOID_ALT_MIN` | Minimum altitude for avoidance (m) |
| `AVOID_ACCEL_MAX` | Max avoidance accel (m/s²) |

### Usage

```cpp
void apply_avoidance() {
    AC_Avoid *avoid = AC_Avoid::get_singleton();
    AC_PosControl *pos = AC_PosControl::get_singleton();

    // Get desired velocity from navigation
    Vector3f desired_vel = wp_nav->get_velocity();

    // Apply avoidance (modifies desired_vel in-place)
    avoid->adjust_velocity(desired_vel, pos_kP, accel_max, pos, dt);

    // Feed modified velocity to position controller
    pos->input_vel_NE_m(Vector2f(desired_vel.x, desired_vel.y));
    pos->input_vel_D_m(desired_vel.z);
}

// For attitude-based modes (no position controller)
void apply_avoidance_attitude() {
    AC_Avoid *avoid = AC_Avoid::get_singleton();

    float roll_rad = target_roll_rad;
    float pitch_rad = target_pitch_rad;

    // Modify roll/pitch to avoid obstacles
    avoid->adjust_roll_pitch_rad(roll_rad, pitch_rad, angle_max_rad);

    // Apply modified attitude
    attitude_control->input_euler_angle_roll_pitch_yaw(
        degrees(roll_rad) * 100, degrees(pitch_rad) * 100, yaw_cd, true);
}
```

---

## Integration Example

```cpp
void mode_auto_run() {
    AC_Fence *fence = AC_Fence::get_singleton();
    AC_Avoid *avoid = AC_Avoid::get_singleton();
    AC_PosControl *pos = AC_PosControl::get_singleton();

    // Check fence breaches first
    if (fence->check() != 0) {
        // Fence breached - failsafe will handle mode change
        return;
    }

    // Get navigation velocity target
    Vector3f vel = wp_nav->get_velocity();

    // Apply avoidance (fence margins + proximity sensors)
    avoid->adjust_velocity(vel, pos_kP, accel_max, pos, dt);

    // Feed to position controller
    pos->input_vel_NE_m(Vector2f(vel.x, vel.y));
    pos->input_vel_D_m(vel.z);

    // Run controllers
    pos->NE_update_controller();
    pos->D_update_controller();
    attitude_control->input_euler_angle_roll_pitch_yaw(...);
    attitude_control->rate_controller_run();
}
```
