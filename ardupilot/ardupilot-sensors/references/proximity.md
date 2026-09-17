# Proximity Sensors

AP_Proximity provides 360° obstacle detection from lidar scanners and proximity sensors.

## AP_Proximity

**Location**: `libraries/AP_Proximity/`
**Singleton**: `AP::proximity()`

### Status Enum

```cpp
enum class Status {
    NotConnected = 0,
    NoData,
    Good
};
```

### Core Methods

```cpp
// Initialization
void init();

// Update
void update();                                // Update all sensors

// Multi-instance
uint8_t num_sensors();                        // Sensor count

// Status
Status get_status();                          // Overall status
Status get_instance_status(uint8_t i);        // Instance status
bool prearm_healthy(char *msg, uint8_t len);

// Range
float distance_max_m();                       // Max detection range
float distance_min_m();                       // Min detection range

// Horizontal obstacles
bool get_horizontal_distances(Proximity_Distance_Array &prx_dist_array);

// Obstacle access
uint8_t get_obstacle_count();                 // Total obstacles
bool get_obstacle(uint8_t num, Vector3f &vec);  // Vector to obstacle
uint8_t get_object_count();
bool get_object_angle_and_distance(uint8_t num, float &angle_deg, float &distance);

// Closest object
bool get_closest_object(float &angle_deg, float &distance);

// Upward distance
bool get_upward_distance(float &distance_m);
bool get_upward_distance(uint8_t instance, float &distance_m);

// 3D boundary access
AP_Proximity_Boundary_3D boundary;            // Direct access to 3D boundary
```

### Parameters (PRX_)

| Parameter | Description |
|-----------|-------------|
| `PRXn_TYPE` | Sensor type |
| `PRXn_ORIENT` | Orientation |
| `PRXn_YAW_CORR` | Yaw correction |
| `PRXn_IGN_ANG1/2/3/4` | Ignore angle zones |
| `PRXn_IGN_WID1/2/3/4` | Ignore zone widths |
| `PRXn_MIN/MAX` | Min/Max range |
| `PRX_FILT` | Filter frequency |
| `PRX_LOG_RAW` | Log raw data |
| `PRX_IGN_GND` | Ignore ground |
| `PRX_ALT_MIN` | Min operating altitude |

### Supported Backends

**2D Lidar**: RPLidar A2, LightWare SF40C/SF45B, TeraRanger Tower/Evo, LD06, Cygbot D1

**Other**: RangeFinder (converts multiple rangefinders to proximity), MAVLink, DroneCAN, MR72 CAN radar, Scripting, SITL

### Usage Example

```cpp
#include <AP_Proximity/AP_Proximity.h>

void check_obstacles() {
    AP_Proximity *prx = AP::proximity();
    if (prx == nullptr) return;

    prx->update();

    if (prx->get_status() != AP_Proximity::Status::Good) {
        return;
    }

    // Get closest obstacle
    float angle_deg, distance;
    if (prx->get_closest_object(angle_deg, distance)) {
        if (distance < 2.0f) {  // Within 2m
            // Obstacle avoidance action
        }
    }
}
```

### Obstacle Iteration

```cpp
void scan_all_obstacles() {
    AP_Proximity *prx = AP::proximity();
    if (prx == nullptr) return;

    uint8_t count = prx->get_object_count();
    for (uint8_t i = 0; i < count; i++) {
        float angle_deg, distance;
        if (prx->get_object_angle_and_distance(i, angle_deg, distance)) {
            // angle_deg: 0=forward, 90=right, 180=back, 270=left
            // distance in meters
        }
    }
}
```

### 3D Obstacle Access

```cpp
void get_3d_obstacles() {
    AP_Proximity *prx = AP::proximity();
    if (prx == nullptr) return;

    uint8_t count = prx->get_obstacle_count();
    for (uint8_t i = 0; i < count; i++) {
        Vector3f vec;
        if (prx->get_obstacle(i, vec)) {
            // vec is NED offset from vehicle to obstacle
            float horiz_dist = vec.xy().length();
            float vert_dist = -vec.z;  // Positive up
        }
    }
}
```

### Integration with AC_Avoid

Proximity data is automatically used by AC_Avoid for obstacle avoidance when enabled. Configure via `AVOID_ENABLE` parameter.
