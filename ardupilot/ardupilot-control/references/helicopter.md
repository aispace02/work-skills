# Helicopter Control

Helicopter-specific control libraries.

## AC_Autorotation

**Location**: `libraries/AC_Autorotation/AC_Autorotation.h`

Emergency autorotation descent for helicopters.

### Phases

1. **Entry**: Initial collective drop, recover rotor speed
2. **Glide**: Controlled descent using rotor inertia
3. **Flare/Landing**: Vehicle-specific (not in this library)

### Core Methods

```cpp
// Entry phase
void init_entry();
void run_entry(float &collective_out, float &collective_acro);

// Glide phase
void init_glide();
void run_glide(float &collective_out, float &collective_acro);

// State
bool check_landed();
float get_head_speed() const;                 // Current rotor RPM
float get_target_head_speed() const;          // Target RPM
```

### Parameters (AROT_)

| Parameter | Description |
|-----------|-------------|
| `AROT_ENABLE` | Enable autorotation |
| `AROT_HS_P` | Head speed P gain |
| `AROT_HS_SET_PT` | Target head speed (RPM) |
| `AROT_FWD_SP_TARG` | Target forward speed (m/s) |
| `AROT_COL_FILT_E` | Entry collective filter |
| `AROT_COL_FILT_G` | Glide collective filter |
| `AROT_XY_ACC_MAX` | Max XY acceleration (m/s²) |

### Usage

```cpp
class ModeAutorotate : public Mode {
    AC_Autorotation autorotation;

    enum class Phase {
        ENTRY,
        GLIDE,
        FLARE,
        TOUCHDOWN
    } phase;

    bool init(bool ignore_checks) override {
        phase = Phase::ENTRY;
        autorotation.init_entry();
        return true;
    }

    void run() override {
        float collective_out, collective_acro;

        switch (phase) {
            case Phase::ENTRY:
                autorotation.run_entry(collective_out, collective_acro);
                // Transition to glide when rotor speed recovered
                if (autorotation.get_head_speed() >= target_speed) {
                    phase = Phase::GLIDE;
                    autorotation.init_glide();
                }
                break;

            case Phase::GLIDE:
                autorotation.run_glide(collective_out, collective_acro);
                // Check for flare altitude
                if (get_altitude_agl() < flare_altitude) {
                    phase = Phase::FLARE;
                }
                break;

            case Phase::FLARE:
                // Vehicle-specific flare logic
                break;

            case Phase::TOUCHDOWN:
                if (autorotation.check_landed()) {
                    // Landed
                }
                break;
        }

        // Apply collective
        motors->set_collective(collective_out);

        // Attitude control still runs
        attitude_control->rate_controller_run();
    }
};
```

---

## AC_InputManager_Heli

**Location**: `libraries/AC_InputManager/AC_InputManager_Heli.h`

Helicopter collective/throttle input scaling.

### Purpose

Rescales pilot collective input between:
- **Stabilize mode**: Uses stability collective curve (soft limits)
- **Acro mode**: Uses full collective range

### Core Methods

```cpp
// Get scaled collective output
float get_pilot_desired_collective(int16_t control_in);

// Mode switching
void set_use_stab_col(bool use);              // true = stabilize curve
void set_stab_col_ramp(float ramp);           // Ramp rate

// Pre-arm check
bool parameter_check(char *fail_msg, uint8_t fail_msg_len);
```

### Collective Curves

```
Pilot Input:    0% ─────────────────────────────── 100%
                │                                   │
Acro Output:    │←───────── Full Range ───────────→│
                │                                   │
Stabilize:      ├─MIN─┬─LOW──────HIGH─┬─MAX─┤
                      │   (hover zone)  │
```

### Parameters (IM_/H_)

| Parameter | Description |
|-----------|-------------|
| `IM_STAB_COL_1` | Stabilize collective min (%) |
| `IM_STAB_COL_2` | Stabilize collective low (%) |
| `IM_STAB_COL_3` | Stabilize collective high (%) |
| `IM_STAB_COL_4` | Stabilize collective max (%) |
| `IM_ACRO_COL_EXP` | Acro collective expo |

### Usage

```cpp
void mode_stabilize_heli_run() {
    AC_InputManager_Heli *input_mgr = &copter.input_manager;

    // Set stabilize collective curve
    input_mgr->set_use_stab_col(true);

    // Get scaled collective
    int16_t pilot_input = channel_throttle->get_control_in();
    float collective = input_mgr->get_pilot_desired_collective(pilot_input);

    // Apply to motors
    motors->set_collective(collective);
}

void mode_acro_heli_run() {
    AC_InputManager_Heli *input_mgr = &copter.input_manager;

    // Use full collective range
    input_mgr->set_use_stab_col(false);

    int16_t pilot_input = channel_throttle->get_control_in();
    float collective = input_mgr->get_pilot_desired_collective(pilot_input);

    motors->set_collective(collective);
}
```

---

## Helicopter Attitude Control

**Location**: `libraries/AC_AttitudeControl/AC_AttitudeControl_Heli.h`

Helicopter-specific variant of AC_AttitudeControl.

### Key Differences from Multi

- Supports flybar and flybarless configurations
- Different rate controller for main rotor
- Tail rotor/DDVP support
- Autorotation collective management

### Additional Methods

```cpp
// Helicopter-specific
void set_hover_roll_trim_scalar(float scalar);
void set_inverted_flight(bool inverted);
bool get_inverted_flight() const;

// Rate feedforward
void rate_bf_roll_pitch_feedforward(float roll_rate_bf, float pitch_rate_bf);
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `ATC_HOVR_ROL_TRM` | Hover roll trim |
| `ATC_RAT_*_FF` | Rate feedforward gains |

---

## Helicopter Motor Control

**Location**: `libraries/AP_Motors/AP_MotorsHeli*.h`

### Variants

- `AP_MotorsHeli_Single` - Single main rotor
- `AP_MotorsHeli_Dual` - Dual rotor (tandem, coaxial)
- `AP_MotorsHeli_Quad` - Quad rotor helicopter

### Key Methods

```cpp
// Collective
void set_collective(float collective);
float get_collective() const;

// Rotor speed
void set_desired_rotor_speed(float rpm);
float get_rotor_speed() const;

// Swashplate
void set_roll(float roll);
void set_pitch(float pitch);
void set_yaw(float yaw);
```
