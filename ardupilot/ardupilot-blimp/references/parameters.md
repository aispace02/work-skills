# Blimp Parameters

## Parameter System

**Files**: `Blimp/Parameters.h`, `Blimp/Parameters.cpp`

## Key Parameters by Category

### Fin Control

| Parameter | Description | Default |
|-----------|-------------|---------|
| `FINS_FREQ_HZ` | Fin oscillation frequency (Hz) | 3 |
| `FINS_TURBO_MODE` | Enable double frequency mode | 0 |

### Velocity Limits

| Parameter | Description | Default |
|-----------|-------------|---------|
| `MAX_VEL_XY` | Max horizontal velocity (m/s) | - |
| `MAX_VEL_Z` | Max vertical velocity (m/s) | - |
| `MAX_VEL_YAW` | Max yaw rate (rad/s) | - |

### Position Limits

| Parameter | Description | Default |
|-----------|-------------|---------|
| `MAX_POS_XY` | Max horizontal position offset (m) | - |
| `MAX_POS_Z` | Max vertical position offset (m) | - |
| `MAX_POS_YAW` | Max yaw offset (rad) | - |

### Control Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `SIMPLE_MODE` | Enable simple mode (earth-frame input) | 0 |
| `DIS_MASK` | Axis disable bitmask | 0 |
| `PID_DZ` | PID deadzone (m) | - |

### Flight Modes

| Parameter | Description | Default |
|-----------|-------------|---------|
| `FLTMODE1` | Flight mode 1 | - |
| `FLTMODE2` | Flight mode 2 | - |
| `FLTMODE3` | Flight mode 3 | - |
| `FLTMODE4` | Flight mode 4 | - |
| `FLTMODE5` | Flight mode 5 | - |
| `FLTMODE6` | Flight mode 6 | - |
| `FLTMODE_CH` | Mode switch channel | - |
| `INITIAL_MODE` | Initial flight mode | - |

### Failsafe

| Parameter | Description | Default |
|-----------|-------------|---------|
| `FS_THR_ENABLE` | Throttle failsafe action | - |
| `FS_THR_VALUE` | Throttle failsafe PWM | - |
| `FS_GCS_ENABLE` | GCS failsafe action | - |
| `FS_EKF_ACTION` | EKF failsafe action | - |
| `FS_EKF_THRESH` | EKF variance threshold | - |
| `FS_CRASH_CHECK` | Crash check enable | - |

### RC Input

| Parameter | Description | Default |
|-----------|-------------|---------|
| `RC_SPEED` | RC update rate (Hz) | - |
| `THROTTLE_DZ` | Throttle deadzone | - |

### PID Controllers

PID parameters are managed by AC_PID library:

| Prefix | Controller |
|--------|------------|
| `PSC_VELXY_*` | Velocity XY PID |
| `PSC_VELZ_*` | Velocity Z PID |
| `PSC_POSXY_*` | Position XY PID |
| `PSC_POSZ_*` | Position Z PID |

### RTL

| Parameter | Description | Default |
|-----------|-------------|---------|
| `RTL_ALTITUDE` | RTL altitude (cm) | - |
| `RTL_LOIT_TIME` | Loiter time at home (ms) | - |
| `RTL_ALT_FINAL` | Final RTL altitude (cm) | - |
| `RTL_SPEED` | RTL speed (cm/s) | - |
| `RTL_ALT_TYPE` | RTL altitude type | - |

### Miscellaneous

| Parameter | Description | Default |
|-----------|-------------|---------|
| `DISARM_DELAY` | Auto disarm delay (s) | - |
| `LOG_BITMASK` | Logging enable mask | - |
| `GCS_PID_MASK` | GCS PID streaming mask | - |
| `GPS_HDOP_GOOD` | Good HDOP threshold | - |

## Parameter Groups

### g (Parameters)

Primary parameters:

```cpp
g.max_vel_xy.get();
g.max_pos_z.get();
g.simple_mode.get();
g.dis_mask.get();
```

### g2 (ParametersG2)

Extended parameters:

```cpp
g2.fs_options.get();
g2.fs_gcs_timeout.get();
g2.frame_class.get();
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

## Disable Mask (DIS_MASK)

Bitmask to disable individual control axes:

| Bit | Value | Axis |
|-----|-------|------|
| 0 | 1 | Y (right/left) |
| 1 | 2 | X (front/back) |
| 2 | 4 | Z (up/down) |
| 3 | 8 | Yaw |

Examples:
- `DIS_MASK = 0`: All axes enabled
- `DIS_MASK = 1`: Y axis disabled
- `DIS_MASK = 8`: Yaw disabled
- `DIS_MASK = 15`: All axes disabled

## Failsafe Actions

### Throttle Failsafe (FS_THR_ENABLE)

| Value | Action |
|-------|--------|
| 0 | Disabled |
| 1 | Land |

### EKF Failsafe (FS_EKF_ACTION)

| Value | Action |
|-------|--------|
| 0 | None |
| 1 | Land |

### GCS Failsafe (FS_GCS_ENABLE)

| Value | Action |
|-------|--------|
| 0 | Disabled |
| 1 | Land |

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
