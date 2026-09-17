# AutoTune

Automatic PID gain tuning through axis testing.

## AC_AutoTune

**Location**: `libraries/AC_AutoTune/AC_AutoTune.h`

### Class Hierarchy

```cpp
AC_AutoTune                  // Base class
├── AC_AutoTune_Multi        // Multicopter
└── AC_AutoTune_Heli         // Helicopter
```

### Tuning Process

1. Pilot enters AUTOTUNE flight mode
2. System tests each axis (Roll → Pitch → Yaw)
3. For each axis: applies twitches, measures response
4. Iteratively adjusts PID gains
5. On completion, gains can be saved or discarded

### Tuning Axes

```cpp
enum TuneType {
    TUNE_ROLL  = 0,
    TUNE_PITCH = 1,
    TUNE_YAW   = 2,
};
```

### Core Methods

```cpp
// Lifecycle
void init();
void run();                                   // Call at ≥100Hz
bool complete() const;

// Gain management
void save_tuning_gains();                     // Save to EEPROM
void load_orig_gains();                       // Restore original
void load_tuned_gains();                      // Apply tuned
void load_intra_test_gains();                 // During testing

// State
TuneType get_current_axis() const;
bool is_testing() const;
```

### Usage

```cpp
class ModeAutoTune : public Mode {
    AC_AutoTune_Multi autotune;

    bool init(bool ignore_checks) override {
        if (!copter.flightmode->has_manual_throttle()) {
            // Need altitude hold capability
            return false;
        }
        autotune.init();
        return true;
    }

    void run() override {
        // AutoTune handles attitude control internally
        autotune.run();

        // Rate control still needed
        attitude_control->rate_controller_run();
    }

    void exit() override {
        // Option to save on clean exit
        if (autotune.complete()) {
            autotune.save_tuning_gains();
        }
    }
};
```

### Pilot Control

- **Stick centered**: AutoTune performs twitches
- **Stick moved**: Normal flight (pauses tuning)
- **Mode switch**: Exit and optionally save
- **Aux switch**: Toggle axis selection

### Parameters Affected

AutoTune modifies these parameters:

**Roll Axis**:
- `ATC_RAT_RLL_P`, `ATC_RAT_RLL_I`, `ATC_RAT_RLL_D`
- `ATC_ANG_RLL_P`

**Pitch Axis**:
- `ATC_RAT_PIT_P`, `ATC_RAT_PIT_I`, `ATC_RAT_PIT_D`
- `ATC_ANG_PIT_P`

**Yaw Axis**:
- `ATC_RAT_YAW_P`, `ATC_RAT_YAW_I`, `ATC_RAT_YAW_D`
- `ATC_ANG_YAW_P`

### Tuning Aggressiveness

Controlled by `AUTOTUNE_AGGR` parameter:
- 0.05 = Very soft
- 0.075 = Soft
- 0.1 = Default
- 0.15 = Aggressive
- 0.2 = Very aggressive

### Best Practices

1. **Calm conditions**: Tune in low wind
2. **Hover throttle**: Set `MOT_HOVER_LEARN` = 2
3. **Battery**: Use fresh battery, consistent weight
4. **Space**: Need room for unexpected movements
5. **One axis at a time**: Can use aux switch to select
6. **Test after**: Verify gains in manual flight

### Saving Gains

```cpp
// After successful tune
if (autotune.complete()) {
    // Land and disarm to auto-save
    // OR explicitly call:
    autotune.save_tuning_gains();
}

// To discard and restore original
autotune.load_orig_gains();
```
