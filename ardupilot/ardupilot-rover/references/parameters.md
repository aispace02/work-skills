# Rover Parameters

## Parameter System

**Files**: `Rover/Parameters.h`, `Rover/Parameters.cpp`

Rover uses two parameter groups:
- `Parameters g` - Original vehicle parameters
- `ParametersG2 g2` - Extended parameters with embedded objects

## Key Vehicle Parameters (g.)

### Speed & Throttle

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `CRUISE_SPEED` | Cruise speed (m/s) | 2.0 | 0-100 |
| `CRUISE_THROTTLE` | Cruise throttle % | 50 | 0-100 |
| `SPEED_MAX` | Max speed (m/s) | 100 | 0-100 |
| `THR_MIN` | Minimum throttle % | 0 | 0-100 |
| `THR_MAX` | Maximum throttle % | 100 | 0-100 |

### Steering

| Parameter | Description | Default |
|-----------|-------------|---------|
| `STEER_TYPE` | 0=angle, 1=rate | 0 |
| `PILOT_STEER_TYPE` | Pilot steering type | 0 |

### Navigation

| Parameter | Description | Default |
|-----------|-------------|---------|
| `WP_SPEED` | Waypoint speed (m/s) | 2.0 |
| `WP_RADIUS` | Waypoint radius (m) | 2.0 |
| `WP_OVERSHOOT` | Max overshoot (m) | 2.0 |
| `WP_PIVOT_ANGLE` | Pivot threshold (deg) | 60 |
| `WP_PIVOT_RATE` | Pivot rate (deg/s) | 60 |
| `RTL_SPEED` | RTL speed (m/s) | 0 (use WP_SPEED) |

### Failsafe

| Parameter | Description | Options |
|-----------|-------------|---------|
| `FS_ACTION` | Radio failsafe action | 0=None, 1=RTL, 2=Hold |
| `FS_TIMEOUT` | Failsafe timeout (s) | 1.5 |
| `FS_THR_ENABLE` | Throttle failsafe | 0=Disabled, 1=Enabled |
| `FS_THR_VALUE` | Throttle failsafe value | 910 |
| `FS_GCS_ENABLE` | GCS failsafe | 0=Disabled, 1=Enabled |
| `FS_CRASH_CHECK` | Crash check | 0=Disabled, 1=Hold |

### Modes

| Parameter | Description |
|-----------|-------------|
| `INITIAL_MODE` | Startup mode |
| `MODE1`-`MODE6` | RC mode switch values |
| `MODE_CH` | Mode switch channel |

## Extended Parameters (g2.)

### Frame

| Parameter | Description | Options |
|-----------|-------------|---------|
| `FRAME_CLASS` | Frame type | 1=Rover, 2=Boat, 3=BalanceBot |
| `FRAME_TYPE` | Motor config | 0=Undefined, 1=Omni3, etc. |

### Turn Radius

| Parameter | Description | Default |
|-----------|-------------|---------|
| `TURN_RADIUS` | Turn radius (m) | 0.9 |
| `TURN_MAX_G` | Max lateral G | 0.6 |

### Loiter

| Parameter | Description | Default |
|-----------|-------------|---------|
| `LOIT_RADIUS` | Loiter radius (m) | 2.0 |
| `LOIT_TYPE` | 0=Stop, 1=Circle | 0 |

### Pivot Turn

| Parameter | Description |
|-----------|-------------|
| `PIVOT_TURN_ANGLE` | Angle to trigger pivot |
| `PIVOT_TURN_RATE` | Pivot turn rate |

### Stick Mixing

| Parameter | Description | Options |
|-----------|-------------|---------|
| `STICK_MIXING` | Allow manual in auto | 0=Disabled, 1=Enabled |

## Embedded Object Parameters

Parameters for embedded objects are defined in `ParametersG2`:

### Motor Parameters (g2.motors)

```cpp
// Defined in AP_MotorsUGV
MOT_PWM_TYPE      // PWM output type
MOT_SAFE_DISARM   // Disarm behavior
MOT_SLEWRATE      // Throttle slew rate
MOT_THST_EXPO     // Thrust curve
```

### Attitude Control (g2.attitude_control)

```cpp
// Defined in AR_AttitudeControl
ATC_STR_ANG_P     // Steering angle P
ATC_STR_RAT_P/I/D // Steering rate PID
ATC_SPEED_P/I/D   // Speed PID
ATC_ACCEL_MAX     // Max acceleration
ATC_DECEL_MAX     // Max deceleration
```

### Waypoint Navigation (g2.wp_nav)

```cpp
// Defined in AR_WPNav
WPNAV_ACCEL       // Waypoint acceleration
WPNAV_TURN_JERK   // Turn jerk limit
```

### SmartRTL (g2.smart_rtl)

```cpp
SRTL_ACCURACY     // Position accuracy
SRTL_POINTS       // Max breadcrumb points
```

### Sailboat (g2.sailboat)

```cpp
SAIL_ENABLE       // Enable sailboat
SAIL_ANGLE_MIN    // Min sail angle
SAIL_ANGLE_MAX    // Max sail angle
SAIL_HEEL_MAX     // Max heel angle
```

## Parameter Definition Pattern

```cpp
// In Parameters.h
class Parameters {
public:
    static const AP_Param::Info var_info[];

    AP_Int8     initial_mode;
    AP_Float    speed_cruise;
    AP_Int16    throttle_cruise;
    // ...
};

class ParametersG2 {
public:
    ParametersG2();

    static const AP_Param::GroupInfo var_info[];

    AP_Float turn_radius;
    AP_Int8  frame_class;

    // Embedded objects with their own parameters
    AP_MotorsUGV motors;
    AR_AttitudeControl attitude_control;
    AR_WPNav_OA wp_nav;
    // ...
};
```

```cpp
// In Parameters.cpp
const AP_Param::Info Parameters::var_info[] = {
    // @Param: CRUISE_SPEED
    // @DisplayName: Cruise speed
    // @Description: Default speed for the vehicle
    // @Units: m/s
    // @Range: 0 100
    // @User: Standard
    GSCALAR(speed_cruise, "CRUISE_SPEED", 2.0f),

    // @Param: CRUISE_THROTTLE
    // @DisplayName: Cruise throttle
    // @Description: Throttle at cruise speed
    // @Range: 0 100
    // @User: Standard
    GSCALAR(throttle_cruise, "CRUISE_THROTTLE", 50),

    // ...
    AP_VAREND
};

const AP_Param::GroupInfo ParametersG2::var_info[] = {
    // @Param: TURN_RADIUS
    // @DisplayName: Turn radius
    // @Description: Vehicle turn radius in meters
    // @Units: m
    // @Range: 0 10
    // @User: Standard
    AP_GROUPINFO("TURN_RADIUS", 1, ParametersG2, turn_radius, 0.9f),

    // @Group: MOT_
    // @Path: ../libraries/AP_Motors/AP_MotorsUGV.cpp
    AP_SUBGROUPINFO(motors, "MOT_", 2, ParametersG2, AP_MotorsUGV),

    // ...
    AP_GROUPEND
};
```

## Adding New Parameters

### Simple Parameter

```cpp
// 1. Add to Parameters.h
class Parameters {
    AP_Float my_param;
};

// 2. Add to var_info in Parameters.cpp
// @Param: MY_PARAM
// @DisplayName: My Parameter
// @Description: Description here
// @Range: 0 100
// @User: Standard
GSCALAR(my_param, "MY_PARAM", 10.0f),

// 3. Access
g.my_param.get();
```

### Group 2 Parameter

```cpp
// 1. Add to ParametersG2 in Parameters.h
class ParametersG2 {
    AP_Float my_g2_param;
};

// 2. Add to var_info in Parameters.cpp
AP_GROUPINFO("MY_G2_PARAM", XX, ParametersG2, my_g2_param, 5.0f),

// 3. Access
g2.my_g2_param.get();
```

## Parameter Access Patterns

```cpp
// Read parameter value
float speed = g.speed_cruise.get();

// Set parameter (only for testing, normally via GCS)
g.speed_cruise.set(3.0f);
g.speed_cruise.save();

// Check if parameter was modified
if (g.speed_cruise.configured()) {
    // Parameter was explicitly set
}

// Set and save with notification
g.speed_cruise.set_and_save(3.0f);
```

## Mode-Specific Parameters

Some modes have their own parameter subgroups:

### Circle Mode

| Parameter | Description |
|-----------|-------------|
| `CIRC_RADIUS` | Circle radius (m) |
| `CIRC_SPEED` | Circle speed (m/s) |

### Dock Mode

| Parameter | Description |
|-----------|-------------|
| `DOCK_SPEED` | Docking approach speed |
| `DOCK_HDG_CORR_EN` | Heading correction enable |
| `DOCK_HDG_CORR_WT` | Heading correction weight |

### Simple Mode

| Parameter | Description |
|-----------|-------------|
| `SIMPLE_TYPE` | Simple mode type |

## Parameter Prefixes Reference

| Prefix | Subsystem |
|--------|-----------|
| `CRUISE_` | Cruise settings |
| `WP_` | Waypoints |
| `ATC_` | Attitude control |
| `MOT_` | Motors |
| `TURN_` | Turning |
| `FS_` | Failsafe |
| `SAIL_` | Sailboat |
| `SRTL_` | SmartRTL |
| `LOIT_` | Loiter |
| `CIRC_` | Circle |
| `DOCK_` | Dock |
| `AVOID_` | Avoidance |
| `FLOW_` | Optical flow |
| `PRX_` | Proximity |
