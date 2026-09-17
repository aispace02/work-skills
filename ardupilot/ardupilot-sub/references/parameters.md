# ArduSub Parameters

## Parameter System

**Files**: `ArduSub/Parameters.h`, `ArduSub/Parameters.cpp`

## Key Parameters by Category

### Frame Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `FRAME_CONFIG` | Frame type (0-7) | 1 |

### Depth Control

| Parameter | Description | Default |
|-----------|-------------|---------|
| `SURFACE_DEPTH` | Surface detection depth (cm) | -10 |
| `SURFACE_MAX_THR` | Max throttle at surface | 0.2 |
| `PILOT_SPEED_UP` | Max ascent rate (cm/s) | 100 |
| `PILOT_SPEED_DN` | Max descent rate (cm/s) | 100 |
| `PILOT_ACCEL_Z` | Vertical acceleration (cm/s/s) | 100 |
| `PILOT_SPEED` | Horizontal speed (cm/s) | 100 |

### Surface Tracking

| Parameter | Description | Default |
|-----------|-------------|---------|
| `SURFTRAK_DEPTH` | Max depth for terrain following (cm) | -50 |
| `RNGFND_SIGNAL_MIN` | Min rangefinder signal quality | 0 |

### Joystick Gain

| Parameter | Description | Default |
|-----------|-------------|---------|
| `JS_GAIN_DEFAULT` | Default gain | 0.5 |
| `JS_GAIN_MIN` | Minimum gain | 0.25 |
| `JS_GAIN_MAX` | Maximum gain | 1.0 |
| `JS_GAIN_STEPS` | Number of gain steps | 4 |
| `JS_THR_GAIN` | Throttle gain multiplier | 1.0 |

### Joystick Buttons

| Parameter | Description | Default |
|-----------|-------------|---------|
| `BTN0_FUNCTION` | Button 0 function | 0 |
| `BTN0_SFUNCTION` | Button 0 shift function | 0 |
| `BTN1_FUNCTION` | Button 1 function | 5 (Manual) |
| ... | ... | ... |
| `BTN31_FUNCTION` | Button 31 function | 0 |

### Lights

| Parameter | Description | Default |
|-----------|-------------|---------|
| `JS_LIGHTS_STEPS` | Light brightness steps | 8 |

### Failsafe

| Parameter | Description | Default |
|-----------|-------------|---------|
| `FS_LEAK_ENABLE` | Leak failsafe action | 1 |
| `FS_GCS_ENABLE` | GCS failsafe action | 0 |
| `FS_GCS_TIMEOUT` | GCS timeout (seconds) | 5.0 |
| `FS_PRESS_ENABLE` | Pressure failsafe | 0 |
| `FS_PRESS_MAX` | Max pressure (Pa) | 105000 |
| `FS_TEMP_ENABLE` | Temperature failsafe | 0 |
| `FS_TEMP_MAX` | Max temperature (C) | 62 |
| `FS_PILOT_INPUT` | Pilot input failsafe | 0 |
| `FS_PILOT_TIMEOUT` | Pilot input timeout (s) | 3.0 |
| `FS_EKF_ACTION` | EKF failsafe action | 0 |
| `FS_EKF_THRESH` | EKF variance threshold | 0.8 |
| `FS_CRASH_CHECK` | Crash failsafe action | 0 |
| `FS_TERRAIN` | Terrain failsafe action | 0 |

### Motor Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `MOT_PWM_MIN` | Minimum PWM | 1100 |
| `MOT_PWM_MAX` | Maximum PWM | 1900 |
| `MOT_1_DIRECTION` | Motor 1 direction | 1 |
| `MOT_2_DIRECTION` | Motor 2 direction | 1 |
| `MOT_FV_CPLNG_K` | Forward/vertical coupling | 1.0 |

### Acro Mode

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ACRO_RP_P` | Roll/pitch P gain | 4.5 |
| `ACRO_YAW_P` | Yaw P gain | 4.5 |
| `ACRO_BAL_ROLL` | Roll balance | 1.0 |
| `ACRO_BAL_PITCH` | Pitch balance | 1.0 |
| `ACRO_TRAINER` | Trainer mode | 2 |
| `ACRO_EXPO` | Expo curve | 0.3 |

### Auto Mode

| Parameter | Description | Default |
|-----------|-------------|---------|
| `WP_YAW_BEHAVIOR` | Auto yaw behavior | 1 |
| `XTRACK_ANG_LIM` | Crosstrack angle limit | 45 |

### Attitude Control

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ATC_ACCEL_Y_MAX` | Max yaw acceleration | 110000 |
| `ATC_RATE_Y_MAX` | Max yaw rate (deg/s) | 180 |

### Position Control

| Parameter | Description | Default |
|-----------|-------------|---------|
| `PSC_JERK_D` | Position controller jerk | 50 |
| `PSC_NE_VEL_P` | Horizontal velocity P gain | 6.0 |

### Navigation

| Parameter | Description | Default |
|-----------|-------------|---------|
| `WPNAV_SPEED` | Waypoint speed (cm/s) | 100 |
| `CIRCLE_RATE` | Circle rate (deg/s) | 2.0 |

### Logging

| Parameter | Description | Default |
|-----------|-------------|---------|
| `LOG_BITMASK` | Log enable bitmask | 176126 |

### RC Input

| Parameter | Description | Default |
|-----------|-------------|---------|
| `RCMAP_ROLL` | Roll channel | 2 |
| `RCMAP_PITCH` | Pitch channel | 1 |
| `RCMAP_FORWARD` | Forward channel | 5 |
| `RCMAP_LATERAL` | Lateral channel | 6 |
| `RC3_TRIM` | Throttle trim | 1500 |

### Origin (for GPS-denied operation)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ORIGIN_LAT` | Backup origin latitude | 0 |
| `ORIGIN_LNG` | Backup origin longitude | 0 |
| `ORIGIN_ALT` | Backup origin altitude | 0 |

## Parameter Groups

### g (Parameters)

Primary parameters accessed via `g.`:

```cpp
g.surface_depth.get();
g.pilot_speed_up.get();
g.failsafe_leak.get();
```

### g2 (ParametersG2)

Extended parameters accessed via `g2.`:

```cpp
g2.backup_origin_lat.get();
g2.surface_nobaro_thrust.get();
g2.actuators.update_actuators();
```

## Adding New Parameters

### Simple Parameter

```cpp
// In Parameters.h
class Parameters {
    AP_Float my_param;
};

// In Parameters.cpp
// @Param: MY_PARAM
// @DisplayName: My Parameter
// @Description: Description of my parameter
// @Range: 0 100
// @User: Standard
GSCALAR(my_param, "MY_PARAM", 50.0f),

// Usage
float val = g.my_param.get();
g.my_param.set_and_save(new_value);
```

### Group 2 Parameter

```cpp
// In Parameters.h
class ParametersG2 {
    AP_Float my_g2_param;
};

// In Parameters.cpp
AP_GROUPINFO("MY_G2", XX, ParametersG2, my_g2_param, 5.0f),

// Usage
float val = g2.my_g2_param.get();
```

### Parameter Enum Entry

```cpp
enum {
    k_param_format_version = 0,
    // ...
    k_param_my_new_param = 250,  // Pick unused number
};
```

## Default Parameter Table

Sub-specific defaults that override library defaults:

```cpp
static const struct AP_Param::defaults_table_struct defaults_table[] = {
    { "BRD_SAFETY_DEFLT",    0 },
    { "CIRCLE_RATE",         2.0f},
    { "ATC_ACCEL_Y_MAX",     110000.0f},
    { "ATC_RATE_Y_MAX",      180.0f},
    { "RC3_TRIM",            1500},
    { "COMPASS_OFFS_MAX",    1000},
    { "INS_GYR_CAL",         0},
    { "RCMAP_ROLL",          2},
    { "RCMAP_PITCH",         1},
    { "RCMAP_FORWARD",       5},
    { "RCMAP_LATERAL",       6},
    { "MOT_PWM_MIN",         1100},
    { "MOT_PWM_MAX",         1900},
    { "PSC_JERK_D",          50.0f},
    { "WPNAV_SPEED",         100.0f},
    { "PILOT_SPEED_UP",      100.0f},
    { "PSC_NE_VEL_P",        6.0f},
    { "EK3_SRC1_VELZ",       0},
};
```

## Parameter Documentation Format

```cpp
// @Param: PARAM_NAME
// @DisplayName: Human-readable name
// @Description: Detailed description
// @Values: 0:Disabled,1:Enabled  (for enums)
// @Range: min max                 (for numeric)
// @Units: m/s                     (standard units)
// @Increment: 0.1                 (UI step)
// @User: Standard/Advanced
// @RebootRequired: True           (if needed)
```

## Common Parameter Operations

```cpp
// Get value
float val = g.my_param.get();

// Set value (RAM only)
g.my_param.set(new_value);

// Set and save to EEPROM
g.my_param.set_and_save(new_value);

// Check if modified
if (g.my_param.configured()) { ... }

// Reset to default
g.my_param.set_default(default_value);
```
