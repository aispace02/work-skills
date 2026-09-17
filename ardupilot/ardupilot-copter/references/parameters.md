# ArduCopter Parameters

## Parameter System

**Files**: `ArduCopter/Parameters.h`, `ArduCopter/Parameters.cpp`

## Key Parameters by Category

### Pilot Input

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ANGLE_MAX` | Max lean angle (centideg) | 3000 |
| `PILOT_SPEED_UP` | Max climb rate (cm/s) | 250 |
| `PILOT_SPEED_DN` | Max descent rate (cm/s) | 0 (auto) |
| `PILOT_ACCEL_Z` | Vertical acceleration (cm/s/s) | 250 |
| `PILOT_TKOFF_ALT` | Auto takeoff altitude (cm) | 0 |
| `PILOT_THR_FILT` | Throttle filter cutoff (Hz) | 0 |
| `PILOT_THR_BHV` | Throttle behavior bitmask | 0 |

### Acro Mode

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ACRO_RP_RATE` | Roll/pitch rate (deg/s) | 360 |
| `ACRO_YAW_RATE` | Yaw rate (deg/s) | 180 |
| `ACRO_BAL_ROLL` | Balance roll point | 1.0 |
| `ACRO_BAL_PITCH` | Balance pitch point | 1.0 |
| `ACRO_TRAINER` | Trainer mode (0-2) | 2 |
| `ACRO_RP_EXPO` | Roll/pitch expo | 0.3 |
| `ACRO_Y_EXPO` | Yaw expo | 0 |
| `ACRO_OPTIONS` | Options bitmask | 0 |

### Waypoint Navigation

| Parameter | Description | Default |
|-----------|-------------|---------|
| `WPNAV_SPEED` | Horizontal speed (cm/s) | 500 |
| `WPNAV_RADIUS` | Waypoint radius (cm) | 200 |
| `WPNAV_SPEED_UP` | Climb speed (cm/s) | 250 |
| `WPNAV_SPEED_DN` | Descent speed (cm/s) | 150 |
| `WPNAV_ACCEL` | Horizontal accel (cm/s/s) | 250 |
| `WPNAV_ACCEL_Z` | Vertical accel (cm/s/s) | 100 |
| `WPNAV_RFND_USE` | Use rangefinder | 1 |

### Loiter

| Parameter | Description | Default |
|-----------|-------------|---------|
| `LOIT_SPEED` | Max loiter speed (cm/s) | 1250 |
| `LOIT_ACC_MAX` | Max acceleration (cm/s/s) | 500 |
| `LOIT_BRK_ACCEL` | Brake acceleration | 250 |
| `LOIT_BRK_DELAY` | Brake start delay (s) | 1 |
| `LOIT_BRK_JERK` | Brake jerk limit | 500 |
| `LOIT_ANG_MAX` | Max lean angle (centideg) | 0 |

### RTL

| Parameter | Description | Default |
|-----------|-------------|---------|
| `RTL_ALT` | RTL altitude (cm) | 1500 |
| `RTL_CONE_SLOPE` | RTL cone slope | 3 |
| `RTL_SPEED` | RTL speed (cm/s) | 0 (auto) |
| `RTL_ALT_FINAL` | Final altitude (cm) | 0 |
| `RTL_CLIMB_MIN` | Minimum climb (cm) | 0 |
| `RTL_LOIT_TIME` | Loiter time (ms) | 5000 |
| `RTL_ALT_TYPE` | Altitude type | 0 |
| `RTL_OPTIONS` | RTL options | 0 |

### Circle

| Parameter | Description | Default |
|-----------|-------------|---------|
| `CIRCLE_RADIUS` | Circle radius (m) | 10 |
| `CIRCLE_RATE` | Circle rate (deg/s) | 20 |
| `CIRCLE_OPTIONS` | Circle options | 1 |

### Land

| Parameter | Description | Default |
|-----------|-------------|---------|
| `LAND_SPEED` | Final descent (cm/s) | 50 |
| `LAND_SPEED_HIGH` | Initial descent (cm/s) | 0 (auto) |
| `LAND_ALT_LOW` | Low alt threshold (cm) | 1000 |
| `LAND_REPOSITION` | Allow repositioning | 1 |

### Failsafe

| Parameter | Description | Default |
|-----------|-------------|---------|
| `FS_THR_ENABLE` | Throttle FS action | 1 |
| `FS_THR_VALUE` | Throttle FS PWM | 975 |
| `FS_GCS_ENABLE` | GCS FS action | 0 |
| `FS_EKF_ACTION` | EKF FS action | 1 |
| `FS_EKF_THRESH` | EKF variance thresh | 0.8 |
| `FS_CRASH_CHECK` | Crash check action | 1 |
| `FS_OPTIONS` | FS options bitmask | 0 |

### Arming

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ARMING_CHECK` | Arming checks bitmask | 1 |
| `DISARM_DELAY` | Auto disarm delay (s) | 10 |

### Motor

| Parameter | Description | Default |
|-----------|-------------|---------|
| `MOT_SPIN_ARM` | Spin when armed | 0.1 |
| `MOT_SPIN_MIN` | Minimum spin | 0.15 |
| `MOT_SPIN_MAX` | Maximum spin | 0.95 |
| `MOT_THST_EXPO` | Thrust expo | 0.65 |
| `MOT_THST_HOVER` | Hover throttle | 0.35 |
| `MOT_PWM_TYPE` | PWM type | 0 |
| `MOT_YAW_HEADROOM` | Yaw headroom | 200 |

### Attitude Control

| Parameter | Description |
|-----------|-------------|
| `ATC_ACCEL_R_MAX` | Max roll accel |
| `ATC_ACCEL_P_MAX` | Max pitch accel |
| `ATC_ACCEL_Y_MAX` | Max yaw accel |
| `ATC_RATE_R_MAX` | Max roll rate |
| `ATC_RATE_P_MAX` | Max pitch rate |
| `ATC_RATE_Y_MAX` | Max yaw rate |
| `ATC_ANG_RLL_P` | Roll angle P |
| `ATC_ANG_PIT_P` | Pitch angle P |
| `ATC_ANG_YAW_P` | Yaw angle P |

### Position Control

| Parameter | Description |
|-----------|-------------|
| `PSC_POSXY_P` | XY position P |
| `PSC_VELXY_P` | XY velocity P |
| `PSC_VELXY_I` | XY velocity I |
| `PSC_VELXY_D` | XY velocity D |
| `PSC_POSZ_P` | Z position P |
| `PSC_VELZ_P` | Z velocity P |
| `PSC_ACCZ_P` | Z accel P |
| `PSC_ACCZ_I` | Z accel I |
| `PSC_ACCZ_D` | Z accel D |

### Simple Mode

| Parameter | Description | Default |
|-----------|-------------|---------|
| `SIMPLE` | Simple mode | 0 |
| `SUPER_SIMPLE` | Super simple mask | 0 |

## Parameter Groups

### g (Parameters)

Primary parameters:

```cpp
g.angle_max.get();
g.pilot_speed_up_cms.get();
g.failsafe_throttle.get();
```

### g2 (ParametersG2)

Extended parameters:

```cpp
g2.fs_options.get();
g2.throw_motor_start.get();
```

## Adding New Parameters

### Simple Parameter

```cpp
// 1. Add enum in Parameters.h
enum {
    k_param_my_param = 250,
};

// 2. Add variable in Parameters class
class Parameters {
    AP_Float my_param;
};

// 3. Add definition in Parameters.cpp
// @Param: MY_PARAM
// @DisplayName: My Parameter
// @Description: Description here
// @Range: 0 100
// @User: Standard
GSCALAR(my_param, "MY_PARAM", 50.0f),

// 4. Use in code
float val = g.my_param.get();
```

### Group 2 Parameter

```cpp
// In ParametersG2 class
AP_Float my_g2_param;

// In Parameters.cpp
AP_GROUPINFO("MY_G2", XX, ParametersG2, my_g2_param, 5.0f),

// Usage
float val = g2.my_g2_param.get();
```

## Default Parameter Table

```cpp
static const struct AP_Param::defaults_table_struct defaults_table[] = {
    { "SYSID_THISMAV",       MAV_TYPE_QUADROTOR },
    { "ANGLE_MAX",           3000 },
    { "PILOT_SPEED_UP",      250 },
    { "WPNAV_SPEED",         500 },
    { "RTL_ALT",             1500 },
    { "LAND_SPEED",          50 },
    // ... more defaults
};
```

## Parameter Documentation

```cpp
// @Param: PARAM_NAME
// @DisplayName: Human-readable name
// @Description: Detailed description
// @Values: 0:Disabled,1:Enabled
// @Range: min max
// @Units: cm/s
// @Increment: 10
// @User: Standard/Advanced
// @RebootRequired: True
```

## Common Operations

```cpp
// Get value
float val = g.my_param.get();

// Set value (RAM only)
g.my_param.set(new_value);

// Set and save to EEPROM
g.my_param.set_and_save(new_value);

// Check if configured
if (g.my_param.configured()) { ... }
```
