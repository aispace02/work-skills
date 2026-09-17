# Vehicle Frames

## Overview

Frames define the vehicle configuration, including:
- Motor layout
- Default parameters
- Physics model

## Listing Frames

```bash
# List frames for a vehicle
sim_vehicle.py --list-frame ArduCopter
sim_vehicle.py --list-frame ArduPlane
sim_vehicle.py --list-frame Rover
```

## ArduCopter Frames

### Multirotor Configurations

| Frame | Motors | Description |
|-------|--------|-------------|
| `quad` / `+` | 4 | Quadcopter + configuration |
| `X` | 4 | Quadcopter X configuration |
| `hexa` | 6 | Hexacopter |
| `hexax` | 6 | Hexacopter X |
| `octa` | 8 | Octocopter |
| `octa-quad` | 8 | OctaQuad (stacked) |
| `deca` | 10 | Decacopter |
| `dodeca-hexa` | 12 | DodecaHexa |
| `tri` | 3 | Tricopter |
| `y6` | 6 | Y6 (stacked) |

### Motor Patterns

| Suffix | Description |
|--------|-------------|
| `-cwx` | Clockwise X pattern |
| `-dji` | DJI motor pattern |
| `-cor` | Corotating motors |

### Helicopters

| Frame | Description |
|-------|-------------|
| `heli` | Traditional helicopter |
| `heli-dual` | Dual rotor helicopter |
| `heli-gas` | Gas helicopter |
| `heli-blade360` | Blade 360 CFX |

### Special

| Frame | Description |
|-------|-------------|
| `singlecopter` | Single motor copter |
| `coaxcopter` | Coaxial copter |

### External Simulators

| Frame | Simulator |
|-------|-----------|
| `gazebo-iris` | Gazebo Iris quadcopter |
| `airsim-copter` | AirSim multirotor |
| `scrimmage-copter` | SCRIMMAGE |
| `IrisRos` | ROS integration |

### Custom Models

| Frame | Description |
|-------|-------------|
| `Callisto` | Callisto model |
| `freestyle` | Freestyle quad |
| `quad-can` | CAN-enabled quad |

## ArduPlane Frames

### Fixed Wing

| Frame | Description |
|-------|-------------|
| `plane` | Standard airplane |
| `plane-elevon` | Elevon (flying wing) |
| `plane-vtail` | V-tail |
| `plane-jet` | Jet aircraft |
| `plane-3d` | 3D aerobatic |
| `plane-dspoilers` | Differential spoilers |
| `plane-soaring` | Soaring/glider |
| `glider` | Pure glider |

### QuadPlane (VTOL)

| Frame | Description |
|-------|-------------|
| `quadplane` | Standard quadplane |
| `quadplane-tri` | Tri-motor quadplane |
| `quadplane-tilt` | Tiltrotor |
| `quadplane-tilttri` | Tilt tricopter |
| `quadplane-tilttrivec` | Tilt tri vectored |
| `quadplane-tilthvec` | Tilt H vectored |
| `quadplane-cl84` | CL-84 style |
| `firefly` | FireFly configuration |

### Tailsitters

| Frame | Description |
|-------|-------------|
| `plane-tailsitter` | Tailsitter |
| `quadplane-copter_tailsitter` | Copter-style tailsitter |

### Special

| Frame | Description |
|-------|-------------|
| `plane-ice` | Internal combustion engine |
| `stratoblimp` | Stratospheric blimp |

### External Simulators

| Frame | Simulator |
|-------|-----------|
| `gazebo-zephyr` | Gazebo Zephyr |
| `jsbsim` | JSBSim |
| `last_letter` | Last Letter |
| `CRRCSim` | CRRCSim |
| `xplane` | X-Plane |

## Rover Frames

### Ground Vehicles

| Frame | Description |
|-------|-------------|
| `rover` | Standard rover |
| `rover-skid` | Skid steering |
| `rover-vectored` | Vectored thrust |
| `rover-omni3mecanum` | Omni wheels |
| `balancebot` | Self-balancing |

### Boats

| Frame | Description |
|-------|-------------|
| `motorboat` | Motor boat |
| `motorboat-skid` | Skid steering boat |
| `sailboat` | Sailboat |
| `sailboat-motor` | Sailboat with motor |

### External Simulators

| Frame | Simulator |
|-------|-----------|
| `gazebo-rover` | Gazebo rover |
| `airsim-rover` | AirSim rover |

## ArduSub Frames

| Frame | Description |
|-------|-------------|
| `vectored` | Vectored 6-thruster (default) |
| `vectored_6dof` | 6-DOF vectored |
| `gazebo-bluerov2` | Gazebo BlueROV2 |

## Blimp Frames

| Frame | Description |
|-------|-------------|
| `Blimp` | Standard blimp |

## AntennaTracker Frames

| Frame | Description |
|-------|-------------|
| `tracker` | Standard tracker |

## Using Frames

### Basic Usage

```bash
sim_vehicle.py -v ArduCopter -f hexa --console --map
sim_vehicle.py -v ArduPlane -f quadplane --console --map
sim_vehicle.py -v Rover -f sailboat --console --map
```

### Frame Parameters

Each frame loads default parameters from:
`Tools/autotest/default_params/<frame>.parm`

### Custom Frame Parameters

```bash
# Add custom parameters
sim_vehicle.py -v ArduCopter -f quad \
    --add-param-file my_params.parm --console --map
```

## Frame Configuration

Frames are defined in `Tools/autotest/pysim/vehicleinfo.py`:

```python
"ArduCopter": {
    "default_frame": "quad",
    "frames": {
        "quad": {
            "waf_target": "bin/arducopter",
            "default_params_filename": "default_params/copter.parm",
        },
        "hexa": {
            "waf_target": "bin/arducopter",
            "default_params_filename": [
                "default_params/copter.parm",
                "default_params/copter-hexa.parm"
            ],
        },
        # ...
    }
}
```

### External Frames

Frames marked `"external": True` require an external simulator:

```python
"gazebo-iris": {
    "waf_target": "bin/arducopter",
    "default_params_filename": [
        "default_params/copter.parm",
        "default_params/gazebo-iris.parm"
    ],
    "external": True,
},
```
