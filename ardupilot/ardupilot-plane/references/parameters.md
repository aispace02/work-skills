# Plane Parameters

## Parameter System

**Files**: `ArduPlane/Parameters.h`, `ArduPlane/Parameters.cpp`

## Key Vehicle Parameters

### Flight Limits (LIM_)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `LIM_ROLL_CD` | Max roll angle (centideg) | 4500 |
| `LIM_PITCH_MAX` | Max pitch up (centideg) | 2000 |
| `LIM_PITCH_MIN` | Max pitch down (centideg) | -2500 |

### Airspeed (ARSPD_)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ARSPD_FBW_MIN` | Min airspeed (m/s) | 9 |
| `ARSPD_FBW_MAX` | Max airspeed (m/s) | 22 |
| `ARSPD_USE` | Use airspeed sensor | 1 |
| `ARSPD_RATIO` | Airspeed ratio | 2.0 |
| `ARSPD_AUTOCAL` | Auto calibration | 0 |

### Throttle (THR_)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `THR_MIN` | Minimum throttle % | 0 |
| `THR_MAX` | Maximum throttle % | 75 |
| `THR_SLEWRATE` | Throttle slew rate | 100 |
| `THR_SUPP_MAN` | Suppress manual throttle | 0 |
| `THR_PASS_STAB` | Throttle passthrough in STAB | 0 |
| `THR_FAILSAFE` | Throttle failsafe value | 950 |

### Trim (TRIM_)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `TRIM_THROTTLE` | Cruise throttle % | 45 |
| `TRIM_ARSPD_CM` | Cruise airspeed (cm/s) | 1200 |
| `TRIM_PITCH_CD` | Trim pitch (centideg) | 0 |

### Navigation (NAV_)

| Parameter | Description |
|-----------|-------------|
| `NAVL1_PERIOD` | L1 navigation period |
| `NAVL1_DAMPING` | L1 damping |

### Failsafe (FS_)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `FS_SHORT_ACTN` | Short failsafe action | 0 |
| `FS_LONG_ACTN` | Long failsafe action | 0 |
| `FS_SHORT_TIMEOUT` | Short FS timeout (s) | 1.5 |
| `FS_LONG_TIMEOUT` | Long FS timeout (s) | 5 |
| `FS_GCS_ENABL` | GCS failsafe enable | 0 |

### Flight Modes (FLTMODE)

| Parameter | Description |
|-----------|-------------|
| `FLTMODE1` - `FLTMODE6` | Mode for each switch position |
| `FLTMODE_CH` | Mode switch channel |
| `INITIAL_MODE` | Mode after boot |

## Controller Parameters

### Roll (RLL2SRV_)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `RLL2SRV_P` | P gain | 1.0 |
| `RLL2SRV_I` | I gain | 0.3 |
| `RLL2SRV_D` | D gain | 0.08 |
| `RLL2SRV_FF` | Feed forward | 0.4 |
| `RLL2SRV_RMAX` | Max roll rate (deg/s) | 75 |
| `RLL2SRV_IMAX` | Max integrator | 3000 |
| `RLL2SRV_TCONST` | Time constant | 0.45 |

### Pitch (PTCH2SRV_)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `PTCH2SRV_P` | P gain | 1.0 |
| `PTCH2SRV_I` | I gain | 0.3 |
| `PTCH2SRV_D` | D gain | 0.08 |
| `PTCH2SRV_FF` | Feed forward | 0.4 |
| `PTCH2SRV_RMAX_UP` | Max pitch up rate | 75 |
| `PTCH2SRV_RMAX_DN` | Max pitch down rate | 75 |
| `PTCH2SRV_IMAX` | Max integrator | 3000 |
| `PTCH2SRV_TCONST` | Time constant | 0.45 |

### Yaw (YAW2SRV_)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `YAW2SRV_SLIP` | Sideslip gain | 0 |
| `YAW2SRV_INT` | Integrator gain | 0 |
| `YAW2SRV_DAMP` | Damping gain | 0 |
| `YAW2SRV_RLL` | Roll coordination | 1.0 |
| `YAW2SRV_IMAX` | Max integrator | 1500 |

### TECS (TECS_)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `TECS_CLMB_MAX` | Max climb rate (m/s) | 5 |
| `TECS_SINK_MIN` | Min sink rate (m/s) | 2 |
| `TECS_SINK_MAX` | Max sink rate (m/s) | 5 |
| `TECS_TIME_CONST` | Time constant | 5 |
| `TECS_THR_DAMP` | Throttle damping | 0.5 |
| `TECS_INTEG_GAIN` | Integrator gain | 0.3 |
| `TECS_SPDWEIGHT` | Speed/height weighting | 1 |

## Takeoff/Landing Parameters

### Takeoff (TKOFF_)

| Parameter | Description |
|-----------|-------------|
| `TKOFF_ALT` | Target altitude (m) |
| `TKOFF_THR_MAX` | Max throttle % |
| `TKOFF_ROTATE_SPD` | Rotation speed (m/s) |
| `TKOFF_LVL_PITCH` | Level-off pitch |

### Landing (LAND_)

| Parameter | Description |
|-----------|-------------|
| `LAND_FLARE_ALT` | Flare altitude (m) |
| `LAND_FLARE_SEC` | Flare time (s) |
| `LAND_DISARMDELAY` | Disarm delay (s) |
| `LAND_ABORT_THR` | Abort throttle |

### RTL (RTL_)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `RTL_ALTITUDE` | RTL altitude (cm) | 10000 |
| `RTL_AUTOLAND` | Auto land after RTL | 0 |
| `RTL_RADIUS` | Loiter radius at home | 0 |

## QuadPlane Parameters (Q_)

| Prefix | Subsystem |
|--------|-----------|
| `Q_ENABLE` | Enable QuadPlane |
| `Q_FRAME_*` | Frame config |
| `Q_A_*` | Attitude control |
| `Q_P_*` | Position control |
| `Q_ASSIST_*` | VTOL assist |
| `Q_TILT_*` | Tiltrotor |
| `Q_TAILSIT_*` | Tailsitter |
| `Q_TRANSITION_*` | Transition |

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
// @Description: Description here
// @Range: 0 100
// @User: Standard
GSCALAR(my_param, "MY_PARAM", 10.0f),

// Usage
float val = g.my_param.get();
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

## Parameter File Locations

```
ArduPlane/
├── Parameters.h        # Parameter declarations
├── Parameters.cpp      # Parameter definitions + var_info
└── Plane.h            # Uses g. and g2. prefixes
```
