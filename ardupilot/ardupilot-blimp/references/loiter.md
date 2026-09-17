# Position/Velocity Control (Loiter)

## Overview

The `Loiter` class implements cascaded PID control for position and velocity in all 4 axes (X, Y, Z, Yaw).

**Files**: `Blimp/Loiter.h`, `Blimp/Loiter.cpp`

## Controller Structure

### Cascaded PIDs

```
Position Target → Position PID → Velocity Target → Velocity PID → Fin Output
```

### PID Controllers

```cpp
// Velocity PIDs (inner loop)
AC_PID_2D pid_vel_xy;    // X/Y velocity
AC_PID_Basic pid_vel_z;   // Z velocity
AC_PID_Basic pid_vel_yaw; // Yaw rate

// Position PIDs (outer loop)
AC_PID_2D pid_pos_xy;    // X/Y position
AC_PID_Basic pid_pos_z;   // Z position
AC_PID pid_pos_yaw;       // Yaw angle
```

### Default Gains

```cpp
// Velocity PIDs: P, I, D, FF, IMAX, FiltHz, FiltDHz
pid_vel_xy{3, 0.2, 0, 0, 0.2, 3, 3};
pid_vel_z{7, 1.5, 0, 0, 1, 3, 3};
pid_vel_yaw{3, 0.4, 0, 0, 0.2, 3, 3};

// Position PIDs
pid_pos_xy{1, 0.05, 0, 0, 0.1, 3, 3};
pid_pos_z{0.7, 0, 0, 0, 0, 3, 3};
pid_pos_yaw{1.2, 0.5, 0, 0, 2, 3, 3, 3};
```

## Vector4b Axis Control

```cpp
class Vector4b {
    bool x;    // Front/back
    bool y;    // Right/left
    bool z;    // Up/down
    bool yaw;  // Rotation
};
```

Used to:
- Zero specific axes (`zero`)
- Disable specific axes (`axes_disabled`)

## Position Control (run)

```cpp
void Loiter::run(Vector3f& target_pos, float& target_yaw, Vector4b axes_disabled);
```

### Algorithm

1. **Output Scaling**: Scale outputs to prevent saturation

```cpp
float xz_out = fabsf(motors->front_out) + fabsf(motors->down_out);
if (xz_out > 1) {
    scaler_xz = 1 / xz_out;
}
scaler_xz = scaler_xz * 0.99 + scaler_xz_n * 0.01;  // Smoothing
```

2. **Position Error**: Calculate error in each axis

```cpp
Vector3f err_xyz = target_pos - blimp.pos_ned;
float err_yaw = wrap_PI(target_yaw - yaw_ef);
```

3. **Deadzone Check**: Zero output if within deadzone

```cpp
if (fabsf(err_xyz.x) < blimp.g.pid_dz) {
    zero.x = true;
}
```

4. **Position PID**: Generate velocity targets

```cpp
target_vel_ef = pid_pos_xy.update_all(target_pos, pos_ned, dt, limit);
target_vel_ef.z = pid_pos_z.update_all(target_pos.z, pos_ned.z, dt, limit.z);
target_vel_yaw = pid_pos_yaw.update_error(err_yaw, dt, limit.yaw);
```

5. **Velocity Limiting**

```cpp
target_vel_ef_c = {
    constrain_float(target_vel_ef.x, -max_vel_xy, max_vel_xy),
    constrain_float(target_vel_ef.y, -max_vel_xy, max_vel_xy),
    constrain_float(target_vel_ef.z, -max_vel_z, max_vel_z)
};
```

6. **Velocity PID**: Generate fin outputs

```cpp
actuator = pid_vel_xy.update_all(target_vel_scaled, vel_ned_filtd_scaled, dt, limit);
act_down = pid_vel_z.update_all(target_vel_z_scaled, vel_z_filtd_scaled, dt, limit.z);
act_yaw = pid_vel_yaw.update_all(target_vel_yaw_scaled, vel_yaw_filtd_scaled, dt, limit.yaw);
```

7. **Frame Rotation**: Rotate XY from earth to body frame

```cpp
blimp.rotate_NE_to_BF(actuator);
```

8. **Output Assignment**

```cpp
motors->front_out = actuator.x;
motors->right_out = actuator.y;
motors->down_out = act_down;
motors->yaw_out = act_yaw;
```

## Velocity Control (run_vel)

```cpp
void Loiter::run_vel(Vector3f& target_vel_ef, float& target_vel_yaw, Vector4b axes_disabled);
```

Simpler version that skips the position PID:

1. Constrain velocity targets
2. Scale for output saturation
3. Run velocity PIDs
4. Rotate to body frame
5. Output to fins

## Output Scaling

To prevent saturation when multiple axes are active:

```cpp
// X/Z share the same fins (front/back + up/down)
scaler_xz = min(1, 1 / (|front_out| + |down_out|))

// Y/Yaw share the same fins (left/right + rotation)
scaler_yyaw = min(1, 1 / (|right_out| + |yaw_out|))
```

Scalers are smoothed with a moving average (99%/1%) to prevent abrupt changes.

## Disable Mask

Individual axes can be disabled via `DIS_MASK` parameter:

```cpp
if (blimp.g.dis_mask & (1 << (axis - 1))) {
    // Axis is disabled
}
```

| Bit | Axis |
|-----|------|
| 0 | Y (right/left) |
| 1 | X (front/back) |
| 2 | Z (up/down) |
| 3 | Yaw |

## Integrator Reset

When disarmed, all integrators are cleared:

```cpp
if (!blimp.motors->armed()) {
    pid_pos_xy.set_integrator(Vector2f(0,0));
    pid_pos_z.set_integrator(0);
    pid_pos_yaw.set_integrator(0);
    pid_vel_xy.set_integrator(Vector2f(0,0));
    pid_vel_z.set_integrator(0);
    pid_vel_yaw.set_integrator(0);

    // Also reset targets to current position
    target_pos = blimp.pos_ned;
    target_yaw = blimp.ahrs.get_yaw_rad();
}
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| `MAX_VEL_XY` | Max horizontal velocity (m/s) |
| `MAX_VEL_Z` | Max vertical velocity (m/s) |
| `MAX_VEL_YAW` | Max yaw rate (rad/s) |
| `MAX_POS_XY` | Max position offset (m) |
| `MAX_POS_Z` | Max vertical offset (m) |
| `MAX_POS_YAW` | Max yaw offset (rad) |
| `PID_DZ` | Position deadzone (m) |
| `DIS_MASK` | Axis disable bitmask |

## Logging

Position/velocity data logged to PSCN, PSCE, PSCD messages:

```cpp
AC_PosControl::Write_PSCN(offset, target_x, actual_x, offset, target_vx, actual_vx, ...);
AC_PosControl::Write_PSCE(offset, target_y, actual_y, offset, target_vy, actual_vy, ...);
AC_PosControl::Write_PSCD(offset, -target_z, -actual_z, offset, -target_vz, -actual_vz, ...);
```
