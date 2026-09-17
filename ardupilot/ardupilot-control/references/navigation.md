# Navigation Libraries

Waypoint navigation, loiter, and circle control for multicopters.

## AC_WPNav

**Location**: `libraries/AC_WPNav/AC_WPNav.h`

### Core Methods

```cpp
// Waypoint setting
bool set_wp_destination(const Location& dest);
bool set_wp_destination_NED_m(const Vector3f& dest_NED_m);
bool set_wp_destination_next(const Location& dest);
void shift_wp_origin_and_destination_to_current_pos_NEU_m();

// Main update (call each loop)
bool update_wpnav();                          // Returns true when WP reached

// Speed/accel configuration
void set_speed_xy_m(float speed_m);
void set_speed_up_m(float speed_m);
void set_speed_down_m(float speed_m);
void set_wp_acceleration_m(float accel_m);
float get_wp_speed_m() const;

// State queries
bool reached_wp_destination() const;
float get_wp_distance_to_destination_m() const;
int32_t get_wp_bearing_to_destination() const;  // Centidegrees
Vector3f get_wp_destination_m() const;

// Spline navigation
bool set_spline_destination(const Location& dest, bool stopped_at_start,
                            bool stopped_at_end, bool fast_waypoint);
bool update_spline();
```

### Parameters (WPNAV_)

| Parameter | Description |
|-----------|-------------|
| `WPNAV_SPEED` | Horizontal speed (cm/s) |
| `WPNAV_SPEED_UP` | Climb speed (cm/s) |
| `WPNAV_SPEED_DN` | Descent speed (cm/s) |
| `WPNAV_ACCEL` | Horizontal accel (cm/s²) |
| `WPNAV_ACCEL_Z` | Vertical accel |
| `WPNAV_RADIUS` | Waypoint acceptance radius (cm) |
| `WPNAV_RFND_USE` | Use rangefinder |

---

## AC_Loiter

**Location**: `libraries/AC_WPNav/AC_Loiter.h`

### Core Methods

```cpp
// Initialize
void init_target_m();                         // At current position
void init_target_m(const Vector2f& pos_m);    // At specified position

// Main update
void update();

// Pilot input
void set_pilot_desired_acceleration(float accel_lat, float accel_lon);

// State
Vector2f get_target_m() const;
bool reached_destination() const;
void get_stopping_point_xy_m(Vector2f& stopping_point) const;

// Landing prep
void soften_for_landing();
```

### Parameters (LOITER_)

| Parameter | Description |
|-----------|-------------|
| `LOITER_ACC_MAX` | Max horizontal accel (cm/s²) |
| `LOITER_ANGLE_MAX` | Max lean angle (cdeg) |
| `LOITER_BRK_ACCEL` | Brake acceleration |
| `LOITER_BRK_DELAY` | Brake start delay (s) |
| `LOITER_BRK_JERK` | Brake jerk limit |
| `LOITER_SPEED` | Max horizontal speed |

---

## AC_Circle

**Location**: `libraries/AC_WPNav/AC_Circle.h`

### Core Methods

```cpp
// Initialize
void init(const Location& center, bool terrain_alt);
void init_start_angle();

// Update
bool update(float climb_rate_m);

// Configuration
void set_radius_m(float radius_m);
void set_rate(float deg_per_sec);
void set_direction(int8_t direction);         // 1=CW, -1=CCW

// State
float get_radius_m() const;
float get_angle() const;                      // Current angle (rad)
float get_angle_total() const;                // Total traveled
const Vector3p& get_center() const;
bool get_is_clockwise() const;
```

### Parameters (CIRCLE_)

| Parameter | Description |
|-----------|-------------|
| `CIRCLE_RADIUS` | Default radius (m) |
| `CIRCLE_RATE` | Angular rate (deg/s) |
| `CIRCLE_OPTIONS` | Options bitmask |

---

## Usage Patterns

### Waypoint Navigation

```cpp
void mode_auto_wp_run() {
    AC_WPNav *wp_nav = copter.wp_nav;
    AC_PosControl *pos = AC_PosControl::get_singleton();
    AC_AttitudeControl *att = AC_AttitudeControl::get_singleton();

    // Set destination (once per waypoint)
    // wp_nav->set_wp_destination(next_wp);

    // Update navigation
    bool wp_complete = wp_nav->update_wpnav();

    if (wp_complete) {
        advance_to_next_waypoint();
    }

    // Vertical control
    pos->update_estimates();
    pos->D_update_controller();

    // Attitude control
    att->input_euler_angle_roll_pitch_yaw(
        pos->get_roll_cd(), pos->get_pitch_cd(),
        wp_nav->get_yaw_cd(), true);
    att->attitude_controller_run_quat();
    att->rate_controller_run();
}
```

### Loiter Mode

```cpp
void mode_loiter_run() {
    AC_Loiter *loiter = copter.loiter_nav;
    AC_PosControl *pos = AC_PosControl::get_singleton();
    AC_AttitudeControl *att = AC_AttitudeControl::get_singleton();

    // Initialize once
    if (!initialized) {
        loiter->init_target_m();
        pos->D_init_controller();
        initialized = true;
    }

    // Apply pilot input as acceleration
    float accel_lat = channel_roll->get_control_in() * accel_max;
    float accel_lon = channel_pitch->get_control_in() * accel_max;
    loiter->set_pilot_desired_acceleration(accel_lat, accel_lon);

    // Update
    loiter->update();
    pos->update_estimates();
    pos->D_update_controller();

    // Attitude
    att->input_euler_angle_roll_pitch_euler_rate_yaw(
        pos->get_roll_cd(), pos->get_pitch_cd(), yaw_rate_cds);
    att->attitude_controller_run_quat();
    att->rate_controller_run();
}
```

### Circle Mode

```cpp
void mode_circle_run() {
    AC_Circle *circle = copter.circle_nav;
    AC_AttitudeControl *att = AC_AttitudeControl::get_singleton();

    // Initialize once
    if (!initialized) {
        circle->init(current_loc, false);
        circle->set_radius_m(10.0f);
        circle->set_rate(5.0f);  // 5 deg/s
        initialized = true;
    }

    // Update circle navigation
    float climb_rate = get_pilot_climb_rate();
    circle->update(climb_rate);

    // Attitude control handled internally by circle->update()
    att->rate_controller_run();
}
```

## Spline Navigation

For smooth paths through multiple waypoints:

```cpp
// Set spline waypoints
wp_nav->set_spline_destination(wp1, true, false, false);   // Start
wp_nav->set_spline_destination_next(wp2);
wp_nav->set_spline_destination_next(wp3);
wp_nav->set_spline_destination(wp4, false, true, false);   // End

// Update
wp_nav->update_spline();
```
