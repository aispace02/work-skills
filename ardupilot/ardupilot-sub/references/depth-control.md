# Depth Control System

## Overview

ArduSub uses pressure-based depth sensing with the barometer configured for underwater operation. Depth control is managed by `AC_PosControl` with Sub-specific modifications.

## Depth Sensor

### Configuration

The barometer is used as a depth sensor:
- Detected at boot: `ap.depth_sensor_present`
- Health monitored: `sensor_health.depth`
- Stored in: `depth_sensor_idx`

### Reading Depth

```cpp
// Get altitude (negative = below surface)
float depth = barometer.get_altitude();

// Get relative position from EKF
float posD;
ahrs.get_relative_position_D_origin_float(posD);
```

### Depth in Control Modes

```cpp
bool control_check_barometer() {
    if (!ap.depth_sensor_present) {
        gcs().send_text(MAV_SEVERITY_WARNING, "Depth sensor is not connected.");
        return false;
    } else if (failsafe.sensor_health) {
        gcs().send_text(MAV_SEVERITY_WARNING, "Depth sensor error.");
        return false;
    }
    return true;
}
```

## Position Controller

### Initialization

```cpp
// Set speed and acceleration limits
position_control->D_set_max_speed_accel_cm(speed_dn, speed_up, accel_z);
position_control->D_set_correction_speed_accel_cm(speed_dn, speed_up, accel_z);

// Initialize controller
position_control->D_init_controller();
```

### Depth Hold Logic (ALT_HOLD)

```cpp
void ModeAlthold::control_depth() {
    // Limit throttle near surface to prevent breaching
    float distance_to_surface = (g.surface_depth - inertial_nav.get_position_z_up_cm()) * 0.01f;
    distance_to_surface = constrain_float(distance_to_surface, 0.0f, 1.0f);
    motors.set_max_throttle(g.surface_max_throttle + (1.0f - g.surface_max_throttle) * distance_to_surface);

    // Get pilot desired climb rate
    float target_climb_rate_cms = sub.get_pilot_desired_climb_rate(channel_throttle->get_control_in());
    target_climb_rate_cms = constrain_float(target_climb_rate_cms, -sub.get_pilot_speed_dn(), g.pilot_speed_up);

    // Handle surface and bottom boundaries
    if (fabsf(target_climb_rate_cms) < 0.05f) {
        if (sub.ap.at_surface) {
            // Keep target below surface
            position_control->set_pos_desired_U_cm(MIN(position_control->get_pos_desired_U_cm(), g.surface_depth));
        } else if (sub.ap.at_bottom) {
            // Keep target above bottom
            position_control->set_pos_desired_U_cm(MAX(inertial_nav.get_position_z_up_cm() + 10.0f, position_control->get_pos_desired_U_cm()));
        }
    }

    // Update position controller
    position_control->D_set_pos_target_from_climb_rate_cms(target_climb_rate_cms);
    position_control->D_update_controller();
}
```

## Surface/Bottom Detection

### Detection Algorithm

```cpp
void Sub::update_surface_and_bottom_detector() {
    if (!motors.armed()) {
        set_surfaced(false);
        set_bottomed(false);
        return;
    }

    Vector3f velocity;
    ahrs.get_velocity_NED(velocity);
    bool vel_stationary = velocity.z > -0.05 && velocity.z < 0.05;

    if (ap.depth_sensor_present && sensor_health.depth) {
        float current_depth = barometer.get_altitude();

        // Surface detection (above SURFACE_DEPTH)
        if (ap.at_surface) {
            set_surfaced(current_depth > g.surface_depth * 0.01 - 0.05);  // 5cm hysteresis
        } else {
            set_surfaced(current_depth > g.surface_depth * 0.01);
        }

        // Bottom detection (throttle limit + stationary)
        if (motors.limit.throttle_lower && vel_stationary) {
            if (bottom_detector_count < BOTTOM_DETECTOR_TRIGGER_SEC * MAIN_LOOP_RATE) {
                bottom_detector_count++;
            } else {
                set_bottomed(true);
            }
        } else {
            set_bottomed(false);
        }
    } else {
        // Without depth sensor, use throttle limits only
        if (vel_stationary) {
            if (motors.limit.throttle_upper) {
                // Surface detection
                if (surface_detector_count++ >= SURFACE_DETECTOR_TRIGGER_SEC * MAIN_LOOP_RATE) {
                    set_surfaced(true);
                }
            } else if (motors.limit.throttle_lower) {
                // Bottom detection
                if (bottom_detector_count++ >= BOTTOM_DETECTOR_TRIGGER_SEC * MAIN_LOOP_RATE) {
                    set_bottomed(true);
                }
            } else {
                set_surfaced(false);
                set_bottomed(false);
            }
        }
    }
}
```

### Detection Timing

```cpp
#define BOTTOM_DETECTOR_TRIGGER_SEC 1.0
#define SURFACE_DETECTOR_TRIGGER_SEC 1.0
```

### State Change Handling

```cpp
void Sub::set_surfaced(bool at_surface) {
    if (ap.at_surface == at_surface) return;

    ap.at_surface = at_surface;
    surface_detector_count = 0;

    if (ap.at_surface) {
        LOGGER_WRITE_EVENT(LogEvent::SURFACED);
    } else {
        LOGGER_WRITE_EVENT(LogEvent::NOT_SURFACED);
    }
}

void Sub::set_bottomed(bool at_bottom) {
    if (ap.at_bottom == at_bottom) return;

    ap.at_bottom = at_bottom;
    bottom_detector_count = 0;

    if (ap.at_bottom) {
        LOGGER_WRITE_EVENT(LogEvent::BOTTOMED);
    } else {
        LOGGER_WRITE_EVENT(LogEvent::NOT_BOTTOMED);
    }
}
```

## Surface Tracking (SURFTRAK)

Uses rangefinder to maintain constant height above seafloor.

### Operation

```cpp
void ModeSurftrak::update_surface_offset() {
    if (sub.rangefinder_alt_ok()) {
        float rangefinder_terrain_offset_cm = sub.rangefinder_state.rangefinder_terrain_offset_cm;

        // Initialize target on first good reading
        if (!HAS_VALID_TARGET && sub.rangefinder_state.inertial_alt_cm < sub.g.surftrak_depth) {
            set_rangefinder_target_cm(sub.rangefinder_state.inertial_alt_cm - rangefinder_terrain_offset_cm);
        }

        if (HAS_VALID_TARGET) {
            // Prevent ascending above SURFTRAK_DEPTH
            float desired_z_cm = rangefinder_terrain_offset_cm + rangefinder_target_cm;
            if (desired_z_cm >= sub.g.surftrak_depth) {
                rangefinder_terrain_offset_cm += sub.g.surftrak_depth - desired_z_cm;
            }

            // Set terrain offset for position controller
            sub.pos_control.set_pos_terrain_target_U_cm(rangefinder_terrain_offset_cm);
        }
    }
}
```

### Pilot Override

```cpp
void ModeSurftrak::control_range() {
    float target_climb_rate_cms = sub.get_pilot_desired_climb_rate(throttle_in);

    if (fabsf(target_climb_rate_cms) < 0.05f) {
        if (pilot_in_control) {
            // Pilot released - apply delta to rangefinder target
            set_rangefinder_target_cm(rangefinder_target_cm + inertial_nav.get_position_z_up_cm() - pilot_control_start_z_cm);
            pilot_in_control = false;
        }
        update_surface_offset();
    } else if (HAS_VALID_TARGET && !pilot_in_control) {
        // Pilot taking control - note starting position
        pilot_control_start_z_cm = inertial_nav.get_position_z_up_cm();
        pilot_in_control = true;
    }
}
```

## Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `SURFACE_DEPTH` | Surface detection depth (cm) | -10 |
| `SURFACE_MAX_THROTTLE` | Max throttle at surface | 0.2 |
| `PILOT_SPEED_UP` | Max ascent rate (cm/s) | 100 |
| `PILOT_SPEED_DN` | Max descent rate (cm/s) | 100 |
| `PILOT_ACCEL_Z` | Vertical acceleration (cm/s/s) | 100 |
| `SURFTRAK_DEPTH` | Max depth for terrain tracking (cm) | -50 |

## Pilot Input

### Climb Rate Calculation

```cpp
float Sub::get_pilot_desired_climb_rate(float throttle_control) {
    // throttle_control ranges from -1000 to 1000
    // Returns climb rate in cm/s

    // Apply deadzone
    float throttle_deadzone = g.throttle_deadzone;
    if (fabsf(throttle_control) < throttle_deadzone) {
        return 0;
    }

    // Scale to climb rate
    float climb_rate;
    if (throttle_control > 0) {
        climb_rate = (throttle_control - throttle_deadzone) / (1000 - throttle_deadzone) * g.pilot_speed_up;
    } else {
        climb_rate = (throttle_control + throttle_deadzone) / (1000 - throttle_deadzone) * get_pilot_speed_dn();
    }

    return climb_rate;
}
```

## Logging

Depth control data logged in CTUN (Control Tuning) message:
- `ThI`: Throttle input
- `Alt`: Altitude
- `BAlt`: Barometer altitude
- `DSAlt`: Desired altitude
- `TAlt`: Target altitude
- `DCRt`: Desired climb rate
- `CRt`: Climb rate
