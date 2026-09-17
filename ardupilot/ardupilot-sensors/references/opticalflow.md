# Optical Flow

AP_OpticalFlow provides velocity measurements relative to the ground.

## AP_OpticalFlow

**Location**: `libraries/AP_OpticalFlow/`
**Singleton**: `AP::opticalflow()`

### Core Methods

```cpp
// Initialization
void init(uint32_t log_bit);

// Update
void update();                                // Update readings

// Status
bool enabled();                               // Flow enabled
bool healthy();                               // Sensor healthy

// Quality (0-255, higher is better)
uint8_t quality();                            // Surface quality

// Flow rates (rad/s)
const Vector2f& flowRate();                   // Raw flow
const Vector2f& bodyRate();                   // IMU-corrected flow

// Timing
uint32_t last_update();                       // Last update time (ms)

// Position offset
const Vector3f& get_pos_offset();             // Sensor offset from CG
```

### Parameters (FLOW_)

| Parameter | Description |
|-----------|-------------|
| `FLOW_TYPE` | Sensor type |
| `FLOW_FXSCALER` | X-axis scale factor |
| `FLOW_FYSCALER` | Y-axis scale factor |
| `FLOW_ORIENT_YAW` | Yaw orientation (cdeg) |
| `FLOW_POS_X/Y/Z` | Position offset |
| `FLOW_ADDR` | I2C address |
| `FLOW_HGT_OVR` | Height override for scaling |

### Supported Backends

PX4Flow, PMW3901, CXOF (Cheerson CX-OF), HereFlow, UPFLOW, MAVLink, SITL

### Usage Example

```cpp
#include <AP_OpticalFlow/AP_OpticalFlow.h>

void read_optical_flow() {
    AP_OpticalFlow *flow = AP::opticalflow();
    if (flow == nullptr) return;

    flow->update();

    if (!flow->enabled() || !flow->healthy()) {
        return;
    }

    // Check surface quality
    uint8_t qual = flow->quality();
    if (qual < 50) {
        // Poor surface quality, don't trust data
        return;
    }

    // Get flow rates
    Vector2f raw_flow = flow->flowRate();     // Raw sensor output
    Vector2f body_flow = flow->bodyRate();    // Corrected for IMU rotation

    // body_flow.x = forward/backward velocity (rad/s)
    // body_flow.y = left/right velocity (rad/s)
}
```

### Converting to Velocity

Optical flow measures angular rate of features. To get velocity:

```cpp
void get_velocity_from_flow() {
    AP_OpticalFlow *flow = AP::opticalflow();
    RangeFinder *rf = AP::rangefinder();

    if (!flow->healthy() || flow->quality() < 50) {
        return;
    }

    // Get height above ground
    float height = rf->distance_orient(ROTATION_PITCH_270);

    // Convert angular rate to velocity
    // velocity = angular_rate * height
    Vector2f body_flow = flow->bodyRate();
    float vel_x = body_flow.x * height;  // Forward velocity (m/s)
    float vel_y = body_flow.y * height;  // Right velocity (m/s)
}
```

### EKF Integration

Optical flow is used by the EKF for position estimation when GPS is unavailable:

1. EKF fuses flow with rangefinder height
2. Provides velocity estimate in body frame
3. Integrates for position when in FLOW modes

### Quality Considerations

- Quality < 50: Unreliable (poor surface texture, too high, etc.)
- Quality 50-100: Marginal
- Quality > 100: Good
- Quality > 200: Excellent

Surface requirements:
- Good texture (not uniform surfaces)
- Adequate lighting
- Height within sensor range (typically 0.1-3m)

### Position Offset

```cpp
// Flow sensor position relative to vehicle CG
// Important for accurate velocity estimation
Vector3f offset = flow->get_pos_offset();
// offset.x = forward of CG (positive)
// offset.y = right of CG (positive)
// offset.z = below CG (positive)
```
