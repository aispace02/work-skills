# Indoor/External Positioning

Non-GPS positioning systems for indoor and precision applications.

## AP_Beacon (Indoor Positioning)

**Location**: `libraries/AP_Beacon/`
**Singleton**: `AP::beacon()`

Provides indoor positioning using fixed beacon infrastructure.

### Beacon State

```cpp
struct BeaconState {
    uint16_t id;                    // Beacon ID
    bool     healthy;               // Beacon healthy
    float    distance;              // Distance to beacon (m)
    uint32_t distance_update_ms;    // Last update time
    Vector3f position;              // Beacon position (NED from origin)
};
```

### Core Methods

```cpp
// Initialization
void init();

// Status
bool enabled();
bool healthy();

// Update
void update();

// Vehicle position (NED from beacon origin)
bool get_vehicle_position_ned(Vector3f &pos, float &accuracy);

// Origin
bool get_origin(Location &origin);

// Beacon access
uint8_t count();                              // Number of beacons
bool get_beacon_data(uint8_t i, BeaconState &state);
uint8_t beacon_id(uint8_t i);
bool beacon_healthy(uint8_t i);
float beacon_distance(uint8_t i);             // meters
Vector3f beacon_position(uint8_t i);          // NED from origin
uint32_t beacon_last_update_ms(uint8_t i);

// Fence boundary from beacons
const Vector2f* get_boundary_points(uint16_t &num_points);
```

### Parameters (BCN_)

| Parameter | Description |
|-----------|-------------|
| `BCN_TYPE` | Beacon type (1=Pozyx, 2=Marvelmind, 3=Nooploop) |
| `BCN_LATITUDE` | Origin latitude |
| `BCN_LONGITUDE` | Origin longitude |
| `BCN_ALT` | Origin altitude |
| `BCN_ORIENT_YAW` | Yaw offset |

### Supported Backends

Pozyx, Marvelmind, Nooploop, SITL

### Usage Example

```cpp
#include <AP_Beacon/AP_Beacon.h>

void read_beacon_position() {
    AP_Beacon *beacon = AP::beacon();
    if (beacon == nullptr || !beacon->enabled()) return;

    beacon->update();

    if (!beacon->healthy()) return;

    Vector3f pos;
    float accuracy;
    if (beacon->get_vehicle_position_ned(pos, accuracy)) {
        // pos.x = north, pos.y = east, pos.z = down (m)
        // accuracy in meters
    }

    // Check individual beacons
    for (uint8_t i = 0; i < beacon->count(); i++) {
        if (beacon->beacon_healthy(i)) {
            float dist = beacon->beacon_distance(i);
        }
    }
}
```

---

## AP_VisualOdom (Visual Odometry)

**Location**: `libraries/AP_VisualOdom/`
**Singleton**: `AP::visualodom()`

Provides position/velocity from visual-inertial odometry systems (T265, VOXL, etc.).

### Core Methods

```cpp
// Initialization
void init();

// Status
bool enabled();
bool healthy();
int8_t quality();  // -1=failed, 0=unknown, 1-100=quality

// Configuration
enum Rotation get_orientation();
float get_pos_scale();
const Vector3f &get_pos_offset();
uint16_t get_delay_ms();
float get_vel_noise();
float get_pos_noise();
float get_yaw_noise();

// Alignment
void request_align_yaw_to_ahrs();
void align_position_to_ahrs(bool align_xy, bool align_z);

// Pre-arm
bool pre_arm_check(char *msg, uint8_t len);
```

### Parameters (VISO_)

| Parameter | Description |
|-----------|-------------|
| `VISO_TYPE` | Sensor type (1=MAV, 2=IntelT265, 3=VOXL) |
| `VISO_POS_X/Y/Z` | Position offset from CG |
| `VISO_ORIENT` | Sensor orientation |
| `VISO_SCALE` | Position scale factor |
| `VISO_DELAY_MS` | Measurement delay |
| `VISO_VEL_M_NSE` | Velocity noise |
| `VISO_POS_M_NSE` | Position noise |
| `VISO_YAW_M_NSE` | Yaw noise |
| `VISO_QUAL_MIN` | Minimum quality threshold |

### Supported Backends

Intel RealSense T265, Qualcomm VOXL, MAVLink VISION_POSITION_ESTIMATE

### MAVLink Interface

VisualOdom receives data via MAVLink messages:
- `VISION_POSITION_ESTIMATE` - Position and attitude
- `VISION_SPEED_ESTIMATE` - Velocity
- `VISION_POSITION_DELTA` - Incremental updates

### Usage Example

```cpp
#include <AP_VisualOdom/AP_VisualOdom.h>

void check_visual_odom() {
    AP_VisualOdom *viso = AP::visualodom();
    if (viso == nullptr || !viso->enabled()) return;

    if (!viso->healthy()) {
        return;
    }

    int8_t qual = viso->quality();
    if (qual < viso->get_quality_min()) {
        // Quality too low
        return;
    }

    // Data is automatically sent to EKF via backends
    // Configure EK3_SRC1_POSXY=6 (ExternalNav) to use
}
```

### EKF Integration

To use visual odometry as position source:

1. Set `VISO_TYPE` to match your sensor
2. Configure EKF3 sources:
   - `EK3_SRC1_POSXY = 6` (ExternalNav)
   - `EK3_SRC1_VELXY = 6` (ExternalNav)
   - `EK3_SRC1_POSZ = 6` (ExternalNav) or 1 (Baro)
3. Set `EK3_SRC1_YAW = 6` if using external yaw

### Position Alignment

```cpp
// Align visual odom origin to current AHRS position
// Useful when starting in a known location
AP_VisualOdom *viso = AP::visualodom();
if (viso != nullptr) {
    viso->align_position_to_ahrs(true, true);  // Align XY and Z
    viso->request_align_yaw_to_ahrs();         // Align yaw
}
```
