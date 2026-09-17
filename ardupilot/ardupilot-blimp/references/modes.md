# Blimp Flight Modes

## Mode Overview

| Mode | # | GPS | Manual Throttle | Description |
|------|---|-----|-----------------|-------------|
| LAND | 0 | No | Yes | Stop all movement |
| MANUAL | 1 | No | Yes | Direct fin control |
| VELOCITY | 2 | Yes | No | Velocity control |
| LOITER | 3 | Yes | No | Position hold |
| RTL | 4 | Yes | No | Return to launch |

## Manual Mode (1)

Direct pass-through of pilot inputs to fin outputs.

```cpp
void ModeManual::run() {
    // Direct input to fins
    // No stabilization or position control
}
```

Properties:
- `requires_GPS()`: false
- `has_manual_throttle()`: true
- `allows_arming()`: true
- `is_autopilot()`: false

## Velocity Mode (2)

Pilot controls velocity in earth frame.

```cpp
void ModeVelocity::run() {
    Vector3f target_vel;
    float target_vel_yaw;

    // Get pilot input
    get_pilot_input(target_vel, target_vel_yaw);

    // Scale by max velocities
    target_vel.x *= g.max_vel_xy;
    target_vel.y *= g.max_vel_xy;
    target_vel.z *= g.max_vel_z;
    target_vel_yaw *= g.max_vel_yaw;

    // Simple mode: rotate body-frame to earth-frame
    if (g.simple_mode == 0) {
        blimp.rotate_BF_to_NE(target_vel.xy());
    }

    // Run velocity controller
    blimp.loiter->run_vel(target_vel, target_vel_yaw, Vector4b{false,false,false,false});
}
```

Properties:
- `requires_GPS()`: true
- `has_manual_throttle()`: false
- `allows_arming()`: true
- `is_autopilot()`: false

## Loiter Mode (3)

Position hold with pilot input for position offset.

```cpp
bool ModeLoiter::init(bool ignore_checks) {
    // Initialize target to current position
    target_pos = blimp.pos_ned;
    target_yaw = blimp.ahrs.get_yaw_rad();
    return true;
}

void ModeLoiter::run() {
    const float dt = blimp.scheduler.get_last_loop_time_s();

    // Get pilot input
    Vector3f pilot;
    float pilot_yaw;
    get_pilot_input(pilot, pilot_yaw);

    // Scale to position deltas
    pilot.x *= g.max_pos_xy * dt;
    pilot.y *= g.max_pos_xy * dt;
    pilot.z *= g.max_pos_z * dt;
    pilot_yaw *= g.max_pos_yaw * dt;

    // Simple mode: rotate body-frame to earth-frame
    if (g.simple_mode == 0) {
        blimp.rotate_BF_to_NE(pilot.xy());
    }

    // Update target position (with lag limit)
    #define POS_LAG 1  // Max seconds ahead
    if (fabsf(target_pos.x - blimp.pos_ned.x) < (g.max_pos_xy * POS_LAG)) {
        target_pos.x += pilot.x;
    }
    if (fabsf(target_pos.y - blimp.pos_ned.y) < (g.max_pos_xy * POS_LAG)) {
        target_pos.y += pilot.y;
    }
    if (fabsf(target_pos.z - blimp.pos_ned.z) < (g.max_pos_z * POS_LAG)) {
        target_pos.z += pilot.z;
    }
    if (fabsf(wrap_PI(target_yaw - ahrs.get_yaw_rad())) < (g.max_pos_yaw * POS_LAG)) {
        target_yaw = wrap_PI(target_yaw + pilot_yaw);
    }

    // Run position controller
    blimp.loiter->run(target_pos, target_yaw, Vector4b{false,false,false,false});
}
```

Properties:
- `requires_GPS()`: true
- `has_manual_throttle()`: false
- `allows_arming()`: true
- `is_autopilot()`: false

### Position Lag

Target position is limited to be no more than `POS_LAG` seconds of movement ahead of actual position. This prevents the target from getting too far away if the blimp can't keep up.

## Land Mode (0)

Stops all movement. Used as failsafe mode.

```cpp
void ModeLand::run() {
    // Zero all outputs
    // Blimp stops moving
}
```

Properties:
- `requires_GPS()`: false
- `has_manual_throttle()`: true
- `allows_arming()`: false
- `is_autopilot()`: false

## RTL Mode (4)

Return to launch position.

```cpp
bool ModeRTL::init(bool ignore_checks) {
    // Set target to home
    return true;
}

void ModeRTL::run() {
    // Navigate to home position
}
```

Properties:
- `requires_GPS()`: true
- `has_manual_throttle()`: false
- `allows_arming()`: true
- `is_autopilot()`: false

## Mode Transitions

```cpp
bool Blimp::set_mode(Mode::Number mode, ModeReason reason) {
    Mode *new_flightmode = mode_from_mode_num(mode);
    if (new_flightmode == nullptr) {
        return false;
    }

    if (!new_flightmode->init(false)) {
        return false;
    }

    exit_mode(flightmode, new_flightmode);
    flightmode = new_flightmode;
    control_mode = mode;

    return true;
}
```

## Pilot Input

All modes use a common pilot input function:

```cpp
void Mode::get_pilot_input(Vector3f &pilot, float &yaw) {
    // Read RC channels and convert to -1 to +1 range
    pilot.x = channel_front->norm_input_dz();
    pilot.y = channel_right->norm_input_dz();
    pilot.z = channel_up->norm_input_dz();
    yaw = channel_yaw->norm_input_dz();
}
```

## Simple Mode

When `SIMPLE_MODE` parameter is 0 (disabled):
- Pilot input is in body frame
- Forward stick = forward relative to blimp nose

When `SIMPLE_MODE` is 1 (enabled):
- Pilot input is in earth frame
- Forward stick = north direction
