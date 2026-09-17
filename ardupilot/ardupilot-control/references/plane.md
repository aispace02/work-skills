# Fixed-Wing Control

Control libraries for ArduPlane.

## AP_L1_Control

**Location**: `libraries/AP_L1_Control/AP_L1_Control.h`

L1 navigation algorithm for path following.

### Constructor

```cpp
AP_L1_Control(AP_AHRS &ahrs, const AP_TECS *tecs);
```

### Core Methods

```cpp
// Navigation updates
void update_waypoint(const Location& prev_WP, const Location& next_WP, float dist_min = 0.0f);
void update_loiter(const Location& center_WP, float radius, int8_t loiter_direction);
void update_heading_hold(int32_t navigation_heading_cd);
void update_level_flight();

// Outputs
int32_t nav_roll_cd() const;                  // Desired roll (centidegrees)
float lateral_acceleration() const;           // Lateral accel (m/s²)
int32_t nav_bearing_cd() const;               // Track bearing
int32_t bearing_error_cd() const;             // Bearing error
float crosstrack_error() const;               // CTE (meters)

// State
bool reached_loiter_target();
float turn_distance(float wp_radius) const;

// Configuration
void set_default_period(float period);
void set_reverse(bool reverse);
```

### Parameters (NAVL1_)

| Parameter | Description |
|-----------|-------------|
| `NAVL1_PERIOD` | L1 tracking period (s) |
| `NAVL1_DAMPING` | L1 damping ratio |
| `NAVL1_XTRACK_I` | Crosstrack integrator gain |

---

## AP_TECS

**Location**: `libraries/AP_TECS/AP_TECS.h`

Total Energy Control System - coordinates altitude and airspeed.

### Constructor

```cpp
AP_TECS(AP_AHRS &ahrs, const AP_FixedWing &parms,
        const AP_Landing &landing, const uint32_t log_bitmask);
```

### Core Methods

```cpp
// Updates (call at 50Hz)
void update_50hz();

// Main control (call after update_50hz)
void update_pitch_throttle(
    int32_t hgt_dem_cm,                       // Height demand
    int32_t EAS_dem_cm,                       // Airspeed demand
    enum AP_FixedWing::FlightStage flight_stage,
    float distance_beyond_land_wp,
    int32_t ptchMinCO_cd,                     // Min pitch for climb-out
    int16_t throttle_nudge,
    float hgt_afe,                            // Height above field elevation
    float load_factor,
    float pitch_trim_deg
);

// Outputs
float get_throttle_demand();                  // -100 to +100
int32_t get_pitch_demand();                   // Centidegrees
float get_VXdot();                            // X-axis accel

// State queries
float get_target_airspeed() const;
float get_max_climbrate() const;
float get_max_sinkrate() const;
float get_height_rate_demand() const;

// Configuration
void set_throttle_min(float thr_min, bool reset_output = false);
void set_throttle_max(float thr_max);
void set_pitch_min(float pitch_min);
void set_pitch_max(float pitch_max);
void reset();
void reset_pitch_I();
void reset_throttle_I();
```

### Parameters (TECS_)

| Parameter | Description |
|-----------|-------------|
| `TECS_CLMB_MAX` | Max climb rate (m/s) |
| `TECS_SINK_MIN` | Min sink rate (m/s) |
| `TECS_SINK_MAX` | Max sink rate (m/s) |
| `TECS_TIME_CONST` | Control time constant |
| `TECS_PTCH_DAMP` | Pitch damping |
| `TECS_INTEG_GAIN` | Integrator gain |
| `TECS_LAND_TCONST` | Landing time constant |
| `TECS_ROLL_COMP` | Roll compensation |

---

## APM_Control (Roll/Pitch/Yaw)

**Location**: `libraries/APM_Control/`

### AP_RollController

```cpp
int32_t get_servo_out(float speed_scaler, bool disable_integrator);
void reset_I();
float get_kP() const;
float get_kD() const;
```

### AP_PitchController

```cpp
int32_t get_servo_out(float speed_scaler, bool disable_integrator);
void reset_I();
float get_kP() const;
float get_kD() const;
```

### AP_YawController

```cpp
int32_t get_servo_out(float speed_scaler, bool disable_integrator, bool ground_mode);
void reset_I();
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `RLL_RATE_P/I/D` | Roll rate PID |
| `PTCH_RATE_P/I/D` | Pitch rate PID |
| `YAW_RATE_P/I/D` | Yaw rate PID |

---

## Usage Pattern

```cpp
void plane_auto_run() {
    // 1. Update L1 navigation
    L1_controller.update_waypoint(prev_WP_loc, next_WP_loc);
    int32_t nav_roll_cd = L1_controller.nav_roll_cd();

    // 2. Update TECS
    TECS_controller.update_50hz();
    TECS_controller.update_pitch_throttle(
        target_altitude_cm,
        target_airspeed_cm,
        flight_stage,
        dist_beyond_land_wp,
        pitch_min_cd,
        throttle_nudge,
        height_above_field,
        load_factor,
        pitch_trim_deg
    );

    float throttle = TECS_controller.get_throttle_demand();
    int32_t pitch_cd = TECS_controller.get_pitch_demand();

    // 3. Apply roll/pitch/yaw controllers
    float speed_scaler = get_speed_scaler();

    int32_t aileron = rollController.get_servo_out(speed_scaler, false);
    int32_t elevator = pitchController.get_servo_out(speed_scaler, false);
    int32_t rudder = yawController.get_servo_out(speed_scaler, false, false);

    // 4. Output to servos
    SRV_Channels::set_output_scaled(SRV_Channel::k_aileron, aileron);
    SRV_Channels::set_output_scaled(SRV_Channel::k_elevator, elevator);
    SRV_Channels::set_output_scaled(SRV_Channel::k_rudder, rudder);
    SRV_Channels::set_output_scaled(SRV_Channel::k_throttle, throttle * 100);
}
```

## Loiter Mode

```cpp
void plane_loiter_run() {
    // Update L1 for loiter
    L1_controller.update_loiter(
        loiter_center,
        loiter_radius_m,
        loiter_direction  // 1 = CW, -1 = CCW
    );

    // Check loiter status
    if (L1_controller.reached_loiter_target()) {
        // Stable in loiter pattern
    }

    // Continue with TECS and servo outputs...
}
```

## Control Hierarchy (Plane)

```
L1 Navigation → nav_roll_cd
    ↓
TECS → pitch_demand, throttle_demand
    ↓
Roll/Pitch/Yaw Controllers
    ↓
Servo Outputs (aileron, elevator, rudder, throttle)
```
