# Getting Started with SITL

## Prerequisites

### Linux (Ubuntu/Debian)

Install build dependencies:

```bash
# Clone ArduPilot (if not already done)
git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git
cd ardupilot

# Run setup script
Tools/environment_install/install-prereqs-ubuntu.sh -y

# Reload profile
. ~/.profile
```

### Required Python Packages

```bash
pip install --user pymavlink MAVProxy future lxml
```

### Optional: FlightGear (3D Visualization)

```bash
sudo apt-get install flightgear
```

## Building SITL

### Automatic Build (Recommended)

sim_vehicle.py handles building automatically:

```bash
cd Tools/autotest
sim_vehicle.py -v ArduCopter --console --map
```

### Manual Build

```bash
# Configure for SITL
./waf configure --board sitl

# Build specific vehicle
./waf copter
./waf plane
./waf rover
./waf sub
./waf blimp

# Or build all
./waf
```

## First Run

### Basic Simulation

```bash
# Navigate to autotest directory
cd Tools/autotest

# Start Copter simulation
sim_vehicle.py -v ArduCopter --console --map
```

### Wipe Parameters

On first run or to reset to defaults:

```bash
sim_vehicle.py -v ArduCopter --console --map -w
```

The `-w` flag wipes `eeprom.bin` and loads default parameters.

## Understanding the Output

When sim_vehicle.py starts, it will:

1. **Configure waf** - Set up build for SITL board
2. **Build firmware** - Compile the vehicle binary
3. **Start SITL** - Launch the ArduPilot executable
4. **Start MAVProxy** - Launch ground control software

### Console Window

Shows MAVProxy output:
- Vehicle status messages
- Parameter changes
- Command responses

### Map Window

Shows:
- Vehicle position
- Waypoints
- Geofence
- Terrain

## Basic Flight Test (Copter)

In the MAVProxy console:

```bash
# Arm the vehicle
arm throttle

# Take off to 10 meters
mode GUIDED
takeoff 10

# Switch to Loiter
mode LOITER

# Land
mode LAND

# Disarm
disarm
```

## Basic Flight Test (Plane)

```bash
# Arm
arm throttle

# Set throttle
rc 3 1700

# Take off happens automatically with airspeed

# Set mode
mode FBWA

# Land
mode AUTO  # if mission has landing
```

## Basic Test (Rover)

```bash
# Arm
arm throttle

# Set mode
mode GUIDED

# Drive to location
guided LAT LON

# Or manual
mode MANUAL
rc 3 1600  # throttle
rc 1 1500  # steering
```

## File Locations

| File | Purpose |
|------|---------|
| `eeprom.bin` | Stored parameters |
| `mav.tlog` | Telemetry log |
| `logs/` | Dataflash logs |
| `terrain/` | Terrain data cache |

## Stopping Simulation

- Press `Ctrl+C` in MAVProxy console
- Or type `quit` in console

## Common Issues

### "No module named pymavlink"

```bash
pip install --user pymavlink
```

### "MAVProxy not found"

```bash
pip install --user MAVProxy
```

### Build errors

```bash
# Update submodules
git submodule update --init --recursive

# Clean and retry
./waf distclean
sim_vehicle.py -v ArduCopter -c --console --map
```

### Map tiles not loading

```bash
# Try different map service
export MAP_SERVICE="MicrosoftHyb"
# Or: "MicrosoftSat", "OviSat", "OviHyb"
```
