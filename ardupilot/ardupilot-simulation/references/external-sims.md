# External Simulators

## Overview

ArduPilot SITL can connect to external flight simulators for:
- Realistic physics
- 3D visualization
- Sensor simulation
- Multi-vehicle scenarios

## Gazebo

### Overview
Open-source robotics simulator, excellent for ROS integration.

### Installation

```bash
# Install Gazebo Garden or Harmonic
# See: https://gazebosim.org/docs

# Install ArduPilot Gazebo plugin
git clone https://github.com/ArduPilot/ardupilot_gazebo
cd ardupilot_gazebo
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j4

# Set environment
export GZ_SIM_SYSTEM_PLUGIN_PATH=$HOME/ardupilot_gazebo/build
export GZ_SIM_RESOURCE_PATH=$HOME/ardupilot_gazebo/models:$HOME/ardupilot_gazebo/worlds
```

### Running

Terminal 1 - Gazebo:
```bash
gz sim -v4 -r iris_runway.sdf
```

Terminal 2 - SITL:
```bash
sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --console --map
```

### Available Models

| Model | World File | Vehicle |
|-------|------------|---------|
| Iris | `iris_runway.sdf` | Quadcopter |
| Zephyr | `zephyr_runway.sdf` | Fixed wing |

## X-Plane

### Overview
Commercial flight simulator with realistic aircraft.

### Setup (X-Plane 11)

1. Settings → Data Output
2. Enable "Network via UDP"
3. Set UDP Rate: 50.0
4. Enable "Send network data output"
5. Enter SITL computer IP
6. Set Port: 49001

### Running

```bash
sim_vehicle.py -v ArduPlane -f xplane --console --map
```

For helicopters:
```bash
sim_vehicle.py -v ArduCopter -f xplane-heli --console --map
```

### WSL2

```bash
# Get Windows IP
WINDOWS_IP=$(ip route show default | awk '{print $3}')
sim_vehicle.py -v ArduPlane -f xplane --console --map
```

## RealFlight

### Overview
Windows-only RC flight simulator with ArduPilot models.

### Requirements
- RealFlight 8, 9, 9.5S, or Evolution
- Windows only

### Setup

1. Settings → Physics → Enable "RealFlight Link"
2. Set "Pause Sim When in Background" → No
3. Set "Automatic Reset Delay" → 2.0 seconds
4. Reduce graphics for better physics rate (>200Hz)

### Running

WSL1:
```bash
sim_vehicle.py -v ArduCopter -f flightaxis:127.0.0.1 --console --map
```

WSL2:
```bash
WINDOWS_IP=$(ip route show default | awk '{print $3}')
sim_vehicle.py -v ArduCopter -f flightaxis:$WINDOWS_IP --console --map
```

Separate machine:
```bash
sim_vehicle.py -v ArduCopter -f flightaxis:192.168.1.100 --console --map
```

### Models

Download from: https://github.com/ArduPilot/SITL_Models

Import via: Simulation → Import → RealFlight Archive

## AirSim

### Overview
Microsoft simulator using Unreal Engine.

### Installation

Download binaries from: https://github.com/Microsoft/AirSim/releases

Or build from source.

### Configuration

Edit `~/Documents/AirSim/settings.json`:

```json
{
  "SettingsVersion": 1.2,
  "SimMode": "Multirotor",
  "Vehicles": {
    "Copter": {
      "VehicleType": "ArduCopter",
      "UseSerial": false,
      "LocalHostIp": "127.0.0.1",
      "UdpIp": "127.0.0.1",
      "UdpPort": 9003,
      "ControlPort": 9002
    }
  }
}
```

### Running

```bash
# Copter
sim_vehicle.py -v ArduCopter -f airsim-copter --console --map

# Rover
sim_vehicle.py -v Rover -f airsim-rover --console --map
```

### Remote Operation

On SITL machine:
```bash
sim_vehicle.py -v ArduCopter -f airsim-copter \
    --sim-address 192.168.1.100 --console --map
```

## JSBSim

### Overview
Open-source flight dynamics model.

### Installation

```bash
sudo apt-get install libjsbsim-dev
```

### Running

```bash
sim_vehicle.py -v ArduPlane -f jsbsim --console --map
```

## FlightGear

### Overview
Open-source flight simulator for visualization.

### Installation

```bash
sudo apt-get install flightgear
```

### Running

```bash
sim_vehicle.py -v ArduPlane --enable-fgview --console --map
```

## Morse

### Overview
Blender-based robotics simulator.

### Running

```bash
sim_vehicle.py -v ArduCopter -f morse --console --map
```

## JSON Interface

### Custom Simulators

SITL supports a JSON interface for custom simulators:

```bash
sim_vehicle.py -v ArduCopter --model JSON --console --map
```

The simulator connects via UDP and exchanges JSON messages with position, attitude, and sensor data.

### Protocol

SITL listens on port 9002 for:
```json
{
    "timestamp": 1234567890.123,
    "imu": {
        "gyro": [0, 0, 0],
        "accel_body": [0, 0, -9.81]
    },
    "position": [lat, lon, alt],
    "velocity": [vn, ve, vd]
}
```

SITL sends servo outputs on port 9003.

## Comparison

| Simulator | Platform | Best For | License |
|-----------|----------|----------|---------|
| Gazebo | Linux/Mac | ROS, Robotics | Open source |
| X-Plane | All | Realistic flight | Commercial |
| RealFlight | Windows | RC models | Commercial |
| AirSim | All | AI/ML, Drones | MIT |
| JSBSim | All | Physics accuracy | Open source |
| FlightGear | All | Visualization | Open source |

## Performance Tips

1. **Lower graphics** - Higher physics rate is more important
2. **Speedup** - Match SITL speedup to simulator capability
3. **Network** - Use localhost when possible
4. **Resources** - Allocate more CPU to simulator
