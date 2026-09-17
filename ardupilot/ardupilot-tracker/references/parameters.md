# AntennaTracker Parameters

## Parameter System

**Files**: `Parameters.h`, `Parameters.cpp`

## Key Parameters by Category

### Target Selection

| Parameter | Description | Default |
|-----------|-------------|---------|
| `SYSID_TARGET` | Vehicle MAVLink system ID (0=auto) | 0 |

### Servo Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `SERVO_YAW_TYPE` | Yaw servo type (0=Pos, 1=OnOff, 2=CR) | 0 |
| `SERVO_PITCH_TYPE` | Pitch servo type | 0 |
| `YAW_RANGE` | Total yaw range (deg) | 360 |
| `PITCH_MIN` | Minimum pitch (deg) | -90 |
| `PITCH_MAX` | Maximum pitch (deg) | 90 |

### Slew Rate Limiting

| Parameter | Description | Default |
|-----------|-------------|---------|
| `YAW_SLEW_TIME` | Time for full yaw sweep (s) | 2 |
| `PITCH_SLEW_TIME` | Time for full pitch sweep (s) | 2 |
| `MIN_REVERSE_TIME` | Minimum yaw reversal time (s) | 1 |

### On/Off Servo Control

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ONOFF_YAW_RATE` | On/off yaw rate (deg/s) | 9 |
| `ONOFF_PITCH_RATE` | On/off pitch rate (deg/s) | 1 |
| `ONOFF_YAW_MINT` | On/off yaw minimum time (s) | 0.1 |
| `ONOFF_PITCH_MINT` | On/off pitch minimum time (s) | 0.1 |

### Trim/Offset

| Parameter | Description | Default |
|-----------|-------------|---------|
| `YAW_TRIM` | Yaw offset (deg) | 0 |
| `PITCH_TRIM` | Pitch offset (deg) | 0 |

### Position/Location

| Parameter | Description | Default |
|-----------|-------------|---------|
| `START_LATITUDE` | Initial latitude (deg) | 0 |
| `START_LONGITUDE` | Initial longitude (deg) | 0 |
| `DISTANCE_MIN` | Minimum tracking distance (m) | - |
| `ALT_SOURCE` | Altitude source (0=Baro, 1=GPS, 2=GPS veh only) | 0 |

### Scanning

| Parameter | Description | Default |
|-----------|-------------|---------|
| `SCAN_SPEED_YAW` | Yaw scan speed (deg/s) | 2 |
| `SCAN_SPEED_PIT` | Pitch scan speed (deg/s) | 5 |

### Mode

| Parameter | Description | Default |
|-----------|-------------|---------|
| `INITIAL_MODE` | Startup mode (0=Manual, 1=Stop, 2=Scan, 10=Auto) | 10 |
| `AUTO_OPTIONS` | Auto mode options bitmask | 0 |
| `SAFE_DISARM_PWM` | Disarm PWM (0=zero, 1=trim) | 0 |

### Communication

| Parameter | Description | Default |
|-----------|-------------|---------|
| `MAV_UPDATE_RATE` | MAVLink update rate (Hz) | 1 |
| `STARTUP_DELAY` | Delay before servo movement (s) | 0 |

### PID Controllers

#### Pitch PID (PITCH2SRV_*)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `PITCH2SRV_P` | Proportional gain | 0.2 |
| `PITCH2SRV_I` | Integral gain | 0.0 |
| `PITCH2SRV_D` | Derivative gain | 0.05 |
| `PITCH2SRV_FF` | Feed forward | 0.02 |
| `PITCH2SRV_IMAX` | Integrator maximum | 4000 |
| `PITCH2SRV_FLTT` | Target filter frequency (Hz) | 0 |
| `PITCH2SRV_FLTE` | Error filter frequency (Hz) | 0 |
| `PITCH2SRV_FLTD` | Derivative filter frequency (Hz) | 0 |
| `PITCH2SRV_SMAX` | Slew rate limit | 0.1 |

#### Yaw PID (YAW2SRV_*)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `YAW2SRV_P` | Proportional gain | 0.2 |
| `YAW2SRV_I` | Integral gain | 0.0 |
| `YAW2SRV_D` | Derivative gain | 0.05 |
| `YAW2SRV_FF` | Feed forward | 0.02 |
| `YAW2SRV_IMAX` | Integrator maximum | 4000 |
| `YAW2SRV_FLTT` | Target filter frequency (Hz) | 0 |
| `YAW2SRV_FLTE` | Error filter frequency (Hz) | 0 |
| `YAW2SRV_FLTD` | Derivative filter frequency (Hz) | 0 |
| `YAW2SRV_SMAX` | Slew rate limit | 0.1 |

### Logging

| Parameter | Description | Default |
|-----------|-------------|---------|
| `LOG_BITMASK` | Log type bitmask | - |
| `GCS_PID_MASK` | PID tuning output mask | 0 |

## LOG_BITMASK Values

| Bit | Value | Type |
|-----|-------|------|
| 0 | 1 | ATTITUDE |
| 1 | 2 | GPS |
| 2 | 4 | RCIN |
| 3 | 8 | IMU |
| 4 | 16 | RCOUT |
| 5 | 32 | COMPASS |
| 6 | 64 | Battery |

## GCS_PID_MASK Values

| Bit | Value | Type |
|-----|-------|------|
| 0 | 1 | Pitch |
| 1 | 2 | Yaw |

## AUTO_OPTIONS Values

| Bit | Value | Description |
|-----|-------|-------------|
| 0 | 1 | Scan for unknown target |

## Parameter Access in Code

### Reading Parameters

```cpp
// Get parameter value
float yaw_range = g.yaw_range.get();
int servo_type = g.servo_yaw_type.get();
```

### Setting Parameters

```cpp
// Set in RAM only
g.yaw_trim.set(5.0f);

// Set and save to EEPROM
g.yaw_trim.set_and_save(5.0f);
```

## Adding New Parameters

### Step 1: Add Enum

In `Parameters.h`:

```cpp
enum {
    // ... existing params
    k_param_my_new_param = 250,  // Pick unused number
};
```

### Step 2: Declare Variable

In `Parameters.h`:

```cpp
class Parameters {
    // ... existing members
    AP_Float my_new_param;
};
```

### Step 3: Define Parameter

In `Parameters.cpp`:

```cpp
// @Param: MY_NEW_PARAM
// @DisplayName: My New Parameter
// @Description: Description of what this parameter does
// @Range: 0 100
// @User: Standard
GSCALAR(my_new_param, "MY_NEW_PARAM", 50.0f),
```

### Step 4: Use Parameter

```cpp
float value = g.my_new_param.get();
```

## Parameter File Format

Parameters are stored in the format:
```
PARAM_NAME VALUE
```

Example `tracker.parm`:
```
SYSID_TARGET 0
YAW_RANGE 360
PITCH_MIN -90
PITCH_MAX 90
SERVO_YAW_TYPE 0
SERVO_PITCH_TYPE 0
YAW2SRV_P 0.2
PITCH2SRV_P 0.2
INITIAL_MODE 10
```

## Loading Parameters

```bash
# Via MAVProxy
param load tracker.parm

# Via Mission Planner
Config/Tuning > Full Parameter List > Load from file
```
