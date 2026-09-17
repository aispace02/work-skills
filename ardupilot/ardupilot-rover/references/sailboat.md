# Sailboat Support

## Sailboat Class

**Location**: `Rover/sailboat.h`, `Rover/sailboat.cpp`

Sailboat-specific control features for boats with sails.

## Enabling Sailboat Mode

```cpp
// Set FRAME_CLASS = 2 (Boat)
// Set SAIL_ENABLE = 1
```

## Core Features

### Sail Types

- **Mainsail**: Traditional sail controlled by sheet tension (0-100%)
- **Wingsail**: Rigid wing sail with angle control (-100 to +100)
- **Mast Rotation**: Rotating mast for optimal sail angle

### Tacking

Sailboats cannot sail directly into the wind. Tacking is the maneuver of zigzagging to make progress upwind.

```cpp
// Tacking parameters
SAIL_ANGLE_IDEAL   // Optimal angle to apparent wind
SAIL_NO_GO_ANGLE   // Minimum angle to wind (no-go zone)
```

## Class API

### Initialization

```cpp
void Sailboat::init() {
    if (!_sail_enabled) {
        return;
    }
    // Setup sail output channels
}
```

### Sail Control

```cpp
// Get mainsail position (0-100)
float get_mainsail() const;

// Get wingsail position (-100 to +100)
float get_wingsail() const;

// Output sail positions to servos
void output_mainsail();
```

### Tacking

```cpp
// Check if currently tacking
bool tacking() const;

// Get tacking state
Tack get_tack() const;  // TACK_PORT, TACK_STARBOARD

// Clear tack request
void clear_tack();

// Handle tacking in auto modes
bool handle_tacking();
```

### Wind Calculations

```cpp
// Get apparent wind angle (radians)
float get_apparent_wind_direction_rad() const;

// Check if target is upwind (in no-go zone)
bool target_is_upwind(const Location &loc) const;

// Get velocity made good toward target
float get_VMG() const;
```

### Motor Assist

```cpp
// Check if motor should assist
bool motor_assist_needed() const;

// Get motor assist throttle
float motor_assist_throttle() const;
```

## Sail Output Calculation

```cpp
void Sailboat::output_mainsail() {
    // Get apparent wind angle
    float wind_angle = get_apparent_wind_direction_rad();

    // Calculate ideal sail angle based on wind
    float sail_angle = calc_ideal_sail_angle(wind_angle);

    // Apply limits
    sail_angle = constrain_float(sail_angle, _sail_angle_min, _sail_angle_max);

    // Output
    g2.motors.set_mainsail(sail_angle);
}
```

## Tacking Logic

```cpp
bool Sailboat::handle_tacking() {
    if (!tacking()) {
        // Check if we need to tack
        if (target_is_upwind(target_loc)) {
            // Initiate tack
            _tacking = true;
            _tack = (wind_on_port_side()) ? TACK_STARBOARD : TACK_PORT;
        }
        return false;
    }

    // Currently tacking
    // Calculate intermediate heading
    float tack_heading = calc_tack_heading();

    // Check if tack complete
    if (heading_matches(tack_heading)) {
        _tacking = false;
        return true;
    }

    // Continue tacking
    set_heading_target(tack_heading);
    return true;
}
```

## Parameters (SAIL_)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `SAIL_ENABLE` | Enable sailboat | 0 |
| `SAIL_ANGLE_MIN` | Min sail angle (deg) | 0 |
| `SAIL_ANGLE_MAX` | Max sail angle (deg) | 90 |
| `SAIL_ANGLE_IDEAL` | Ideal sail angle to wind | 25 |
| `SAIL_HEEL_MAX` | Max heel angle (deg) | 15 |
| `SAIL_NO_GO_ANGLE` | No-go zone angle (deg) | 45 |
| `SAIL_MOTOR_THR` | Motor assist throttle % | 0 |

## Sail Servo Functions

| Function | Number | Description |
|----------|--------|-------------|
| MAINSAIL | 89 | Mainsail sheet |
| WINGSAIL | 90 | Wingsail angle |
| MAST_ROTATION | 91 | Mast rotation |

## Integration with Modes

### Auto Mode with Sailboat

```cpp
void ModeAuto::update() {
    // Check for tacking need
    if (g2.sailboat.handle_tacking()) {
        // Use tack heading instead of direct heading
        float heading = g2.sailboat.get_tack_heading();
        calc_steering_to_heading(heading, ...);
    } else {
        // Normal navigation
        navigate_to_waypoint();
    }

    // Always update sail output
    g2.sailboat.output_mainsail();

    // Motor assist if needed
    if (g2.sailboat.motor_assist_needed()) {
        float motor_throttle = g2.sailboat.motor_assist_throttle();
        g2.motors.set_throttle(motor_throttle);
    }
}
```

### Manual Mode with Sailboat

```cpp
void ModeManual::update() {
    float steering, throttle;
    get_pilot_desired_steering_and_throttle(steering, throttle);

    g2.motors.set_steering(steering);
    g2.motors.set_throttle(throttle);

    // Sailboat: manual sail control or auto
    if (g2.sailboat.enabled()) {
        // Automatic sail positioning based on wind
        g2.sailboat.output_mainsail();
    }
}
```

## Wind Vane Integration

Sailboats use `AP_WindVane` for wind sensing:

```cpp
// Get apparent wind direction
float wind_dir = AP::windvane()->get_apparent_wind_direction_rad();

// Get true wind speed
float wind_speed = AP::windvane()->get_true_wind_speed();
```

### Wind Vane Parameters

| Parameter | Description |
|-----------|-------------|
| `WNDVN_TYPE` | Wind vane type |
| `WNDVN_DIR_OFS` | Direction offset |
| `WNDVN_CAL` | Calibration |
| `WNDVN_SPEED_TYPE` | Speed sensor type |

## Heel Control

Excessive heel (leaning) is controlled by easing the sail:

```cpp
float Sailboat::get_heel_limited_sail() {
    // Get current heel angle
    float heel = fabsf(ahrs.get_roll());

    // If over limit, ease sail
    if (heel > radians(_heel_max)) {
        float ease = (heel - radians(_heel_max)) * _heel_gain;
        return _current_sail - ease;
    }
    return _current_sail;
}
```

## Velocity Made Good (VMG)

VMG is the component of velocity toward the destination:

```cpp
float Sailboat::get_VMG() const {
    // Get bearing to destination
    float bearing_to_dest = current_loc.get_bearing_to(destination);

    // Get current course
    float course = ahrs.get_groundspeed_vector().angle();

    // Calculate VMG
    float speed = ahrs.get_groundspeed();
    float angle_diff = bearing_to_dest - course;

    return speed * cosf(angle_diff);
}
```

## Best Practices

1. **Tune SAIL_NO_GO_ANGLE** based on your boat's pointing ability
2. **Set SAIL_HEEL_MAX** conservatively to prevent capsizing
3. **Enable SAIL_MOTOR_THR** for light wind or tight maneuvering
4. **Calibrate wind vane** carefully for accurate tacking
5. **Test tacking** in open water before missions
