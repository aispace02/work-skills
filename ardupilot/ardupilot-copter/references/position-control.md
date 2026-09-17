# Position Control

## Overview

ArduCopter uses several interconnected controllers for position control:
- `AC_PosControl` - Core position/velocity/acceleration control
- `AC_WPNav` - Waypoint navigation
- `AC_Loiter` - Loiter position hold
- `AC_Circle` - Circle navigation

## AC_PosControl

**File**: `libraries/AC_AttitudeControl/AC_PosControl.h`

### Vertical Control (D axis)

```cpp
// Initialize vertical controller
void D_init_controller();

// Set speed and acceleration limits
void D_set_max_speed_accel_m(float speed_down, float speed_up, float accel);

// Set target from climb rate
void D_set_pos_target_from_climb_rate_ms(float climb_rate_ms);

// Update controller
void D_update_controller();

// Relax controller (when landed)
void D_relax_controller(float throttle);
```

### Horizontal Control (NE axes)

```cpp
// Initialize horizontal controller
void NE_init_controller();

// Set speed and acceleration limits
void NE_set_max_speed_accel_m(float speed, float accel);

// Input position/velocity/acceleration
void input_pos_vel_accel_NE_m(
    const Vector2p& pos,
    const Vector2f& vel,
    const Vector2f& accel
);

// Update controller
void NE_update_controller();
```

### 3D Control

```cpp
// Combined position/velocity/acceleration input
void input_pos_vel_accel_NED_m(
    const Vector3p& pos,
    const Vector3f& vel,
    const Vector3f& accel
);

// Get thrust vector for attitude control
Vector3f get_thrust_vector() const;
```

## AC_WPNav

**File**: `libraries/AC_WPNav/AC_WPNav.h`

### Waypoint Navigation

```cpp
// Set destination
bool set_wp_destination(const Location& destination);
bool set_wp_destination(const Vector3f& destination);

// Get destination
const Vector3f& get_wp_destination() const;

// Update navigation
bool update_wpnav();

// Check arrival
bool reached_wp_destination() const;

// Get distance/bearing to waypoint
float get_wp_distance_to_destination_m() const;
float get_wp_bearing_to_destination_rad() const;
```

### Spline Navigation

```cpp
// Set spline destination
bool set_spline_destination(const Location& destination, ...);

// Update spline navigation
bool update_spline();
```

### Speed Control

```cpp
// Get/set horizontal speed
float get_default_speed_NE_ms() const;
void set_speed_NE_ms(float speed_NE_ms);

// Get/set vertical speeds
float get_default_speed_up_ms() const;
float get_default_speed_down_ms() const;
void set_speed_up_ms(float speed_up_ms);
void set_speed_down_ms(float speed_down_ms);
```

### Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `WPNAV_SPEED` | Horizontal speed (cm/s) | 500 |
| `WPNAV_RADIUS` | Waypoint radius (cm) | 200 |
| `WPNAV_SPEED_UP` | Climb speed (cm/s) | 250 |
| `WPNAV_SPEED_DN` | Descent speed (cm/s) | 150 |
| `WPNAV_ACCEL` | Horizontal acceleration | 250 |
| `WPNAV_ACCEL_Z` | Vertical acceleration | 100 |

## AC_Loiter

**File**: `libraries/AC_WPNav/AC_Loiter.h`

### Initialization

```cpp
// Initialize at current position
void init_target();

// Initialize at specific location
void init_target(const Vector2f& position_ne_m);

// Soften target for landing
void soften_for_landing();
```

### Pilot Input

```cpp
// Set pilot desired acceleration (from stick input)
void set_pilot_desired_acceleration_rad(float accel_lat_rad, float accel_lon_rad);

// Clear pilot input
void clear_pilot_desired_acceleration();
```

### Update

```cpp
// Update loiter controller
void update();

// Get thrust vector for attitude control
Vector3f get_thrust_vector() const;
```

### Position Info

```cpp
// Get distance/bearing to target
float get_distance_to_target_m() const;
float get_bearing_to_target_rad() const;

// Get maximum lean angle
float get_angle_max_rad() const;
```

## AC_Circle

**File**: `libraries/AC_WPNav/AC_Circle.h`

### Initialization

```cpp
// Initialize at current position
void init_center();

// Set circle center
void set_center(const Vector2p& center_ne_m);

// Set radius
void set_radius_m(float radius_m);

// Set rate (degrees per second)
void set_rate_rads(float rate_rads);
```

### Update

```cpp
// Update circle navigation
void update();

// Get circle position
float get_yaw_cd() const;  // Current yaw in centidegrees
```

### Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `CIRCLE_RADIUS` | Circle radius (m) | 10 |
| `CIRCLE_RATE` | Circle rate (deg/s) | 20 |
| `CIRCLE_OPTIONS` | Circle options bitmask | 1 |

## Terrain Following

### Surface Tracking

```cpp
class SurfaceTracking {
public:
    enum class Surface {
        NONE = 0,
        GROUND = 1,
        CEILING = 2
    };

    void update_surface_offset();
    void set_surface(Surface new_surface);
};
```

### Rangefinder Integration

```cpp
// Get rangefinder altitude
float rangefinder_alt_ok() const;
float get_rangefinder_height_interpolated_m() const;

// Update terrain offset
void update_rangefinder_terrain_offset();
```

## Usage Examples

### ALT_HOLD Mode

```cpp
void ModeAltHold::run() {
    // Get pilot climb rate
    float target_climb_rate_ms = get_pilot_desired_climb_rate_ms();

    // Set vertical target
    pos_control->D_set_pos_target_from_climb_rate_ms(target_climb_rate_ms);

    // Update controller
    pos_control->D_update_controller();
}
```

### LOITER Mode

```cpp
void ModeLoiter::run() {
    // Set pilot acceleration
    loiter_nav->set_pilot_desired_acceleration_rad(roll, pitch);

    // Update loiter
    loiter_nav->update();

    // Vertical control
    pos_control->D_set_pos_target_from_climb_rate_ms(climb_rate);
    pos_control->D_update_controller();

    // Attitude control with thrust vector
    attitude_control->input_thrust_vector_rate_heading_rads(
        loiter_nav->get_thrust_vector(), yaw_rate, false);
}
```

### AUTO/WP Mode

```cpp
void ModeAuto::wp_run() {
    // Update waypoint navigation
    wp_nav->update_wpnav();

    // Vertical control
    pos_control->D_update_controller();

    // Attitude control
    attitude_control->input_thrust_vector_heading_rads(
        wp_nav->get_thrust_vector(), auto_yaw.yaw_rad());
}
```
