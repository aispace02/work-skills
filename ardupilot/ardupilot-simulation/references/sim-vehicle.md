# sim_vehicle.py Reference

## Location

`Tools/autotest/sim_vehicle.py`

## Basic Usage

```bash
sim_vehicle.py [options]
```

## Vehicle Selection

| Option | Description |
|--------|-------------|
| `-v VEHICLE` | Vehicle type |

**Available vehicles:**
- `ArduCopter` - Multirotor
- `ArduPlane` - Fixed wing
- `Rover` - Ground vehicle
- `ArduSub` - Submarine
- `Blimp` - Lighter than air
- `AntennaTracker` - Antenna tracker
- `Helicopter` - Traditional helicopter

**Aliases:**
- `Copter` = `ArduCopter`
- `Plane` = `ArduPlane`
- `Sub` = `ArduSub`

## Frame Selection

| Option | Description |
|--------|-------------|
| `-f FRAME` | Frame type |

See `references/frames.md` for complete list.

## Build Options

| Option | Description |
|--------|-------------|
| `-N, --no-rebuild` | Don't rebuild before starting |
| `--no-configure` | Skip waf configure |
| `-D, --debug` | Build with debugging symbols |
| `-c, --clean` | Clean before building |
| `-j JOBS` | Number of parallel build jobs |
| `-b TARGET` | Override build target |
| `--coverage` | Build with code coverage |
| `--ubsan` | Build with undefined behavior sanitizer |
| `--force-32bit` | Force 32-bit build |

### Configure Options

| Option | Description |
|--------|-------------|
| `--waf-configure-arg ARG` | Extra waf configure argument |
| `--waf-build-arg ARG` | Extra waf build argument |
| `--enable-ekf2` | Enable EKF2 |
| `--disable-ekf3` | Disable EKF3 |
| `--enable-DDS` | Enable DDS/ROS2 support |

## Simulation Options

### Instance Control

| Option | Description |
|--------|-------------|
| `-I INSTANCE` | Instance number (default: 0) |
| `-n COUNT` | Number of instances |
| `-i "0 1 2"` | Specific instance list |
| `--sysid ID` | Set MAV_SYSID |
| `--auto-sysid` | Auto-assign sysid per instance |

### Location

| Option | Description |
|--------|-------------|
| `-L LOCATION` | Named location from locations.txt |
| `-l LAT,LON,ALT,HDG` | Custom location |
| `--swarm FILE` | Swarm init file for offsets |
| `--auto-offset-line BEARING,DIST` | Auto-space instances |

### Timing

| Option | Description |
|--------|-------------|
| `-S SPEEDUP` | Simulation speedup (default: 1) |
| `-d DELAY` | Delay MAVProxy start (seconds) |
| `--start-time YYYY-MM-DD-HH:MM` | Simulation start time |

### Model

| Option | Description |
|--------|-------------|
| `--model MODEL` | Override simulation model |
| `-A ARGS` | Additional SITL instance args |

### Network

| Option | Description |
|--------|-------------|
| `--mcast` | Use multicast (239.255.145.50:14550) |
| `--udp` | Use UDP on 127.0.0.1:5760 |
| `--sim-address IP` | Simulator IP address |
| `--no-extra-ports` | Disable UDP 14550/14551 output |
| `--no-wsl2-network` | Disable WSL2 network setup |

### Features

| Option | Description |
|--------|-------------|
| `-T, --tracker` | Start antenna tracker |
| `-M, --mavlink-gimbal` | Enable MAVLink gimbal |
| `--osd` | Enable SITL OSD |
| `--tonealarm` | Enable tone alarm |
| `--rgbled` | Enable RGB LED |
| `--enable-fgview` | Enable FlightGear view |
| `--can-peripherals` | Start DroneCAN peripheral |

### Storage

| Option | Description |
|--------|-------------|
| `-w, --wipe-eeprom` | Wipe EEPROM and reload defaults |
| `--flash-storage` | Use flash storage emulation |
| `--fram-storage` | Use FRAM storage emulation |
| `--use-dir DIR` | Store state in named directory |

### Parameters

| Option | Description |
|--------|-------------|
| `-P PARAM=VALUE` | Set parameter |
| `--add-param-file FILE` | Load additional parameter file |
| `--fresh-params` | Generate fresh parameter XML |

## Debug Options

| Option | Description |
|--------|-------------|
| `-G, --gdb` | Run with GDB |
| `-g, --gdb-stopped` | GDB, stopped at start |
| `--lldb` | Run with LLDB |
| `--lldb-stopped` | LLDB, stopped at start |
| `-V, --valgrind` | Run with Valgrind |
| `--callgrind` | Run with Callgrind |
| `--strace` | Run with strace |
| `-B LOCATION` | Add GDB breakpoint |
| `--disable-breakpoints` | Disable all breakpoints initially |

## MAVProxy Options

| Option | Description |
|--------|-------------|
| `--console` | Open console |
| `--map` | Open map |
| `-m ARGS` | Additional MAVProxy arguments |
| `--out DEST` | Additional MAVLink output |
| `--no-mavproxy` | Don't start MAVProxy |
| `--no-rcin` | Disable MAVProxy RC input |
| `--aircraft NAME` | Store logs in named directory |
| `--moddebug N` | MAVProxy module debug level |
| `--mavcesium` | Load Cesium map module |

## Completion Helpers

| Option | Description |
|--------|-------------|
| `--list-vehicle` | List available vehicles |
| `--list-frame VEHICLE` | List frames for vehicle |

## Examples

### Basic Copter
```bash
sim_vehicle.py -v ArduCopter --console --map
```

### QuadPlane at Location
```bash
sim_vehicle.py -v ArduPlane -f quadplane -L CMAC --console --map
```

### Multi-Vehicle Swarm
```bash
sim_vehicle.py -v ArduCopter -n 5 --auto-sysid --mcast \
    -L CMAC --auto-offset-line 90,10 --console --map
```

### Debug with GDB
```bash
sim_vehicle.py -v ArduCopter -G --console --map
```

### Custom Parameters
```bash
sim_vehicle.py -v ArduCopter -P ARMING_CHECK=0 -P GPS_TYPE=0 --console --map
```

### External Simulator
```bash
# Gazebo
sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --console --map

# X-Plane
sim_vehicle.py -v ArduPlane -f xplane --console --map

# RealFlight
sim_vehicle.py -v ArduCopter -f flightaxis:192.168.1.100 --console --map
```

### No MAVProxy (TCP connection)
```bash
sim_vehicle.py -v ArduCopter --no-mavproxy
# Connect via TCP port 5760
```

### Fast Simulation
```bash
sim_vehicle.py -v ArduCopter -S 10 --console --map
```
