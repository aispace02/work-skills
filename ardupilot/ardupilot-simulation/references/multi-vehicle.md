# Multi-Vehicle Simulation

## Basic Multi-Vehicle

### Count Option

```bash
# 5 vehicles with auto system IDs
sim_vehicle.py -v ArduCopter -n 5 --auto-sysid --console --map
```

### Specific Instances

```bash
# Specific instance numbers
sim_vehicle.py -v ArduCopter -i "0 2 5" --auto-sysid --console --map
```

## Vehicle Spacing

### Automatic Line Spacing

```bash
# Space 10m apart along 90-degree bearing
sim_vehicle.py -v ArduCopter -n 5 --auto-sysid \
    -L CMAC --auto-offset-line 90,10 --console --map
```

### Swarm Init File

Create `swarminit.txt`:
```
# instance=heading_offset,distance_offset,alt_offset,heading
0=0,0,0,0
1=90,10,0,0
2=180,10,0,0
3=270,10,0,0
```

```bash
sim_vehicle.py -v ArduCopter -n 4 --auto-sysid \
    -L CMAC --swarm swarminit.txt --console --map
```

## Communication Methods

### Multicast (Recommended)

```bash
sim_vehicle.py -v ArduCopter -n 3 --auto-sysid --mcast \
    --console --map
```

All vehicles communicate on `239.255.145.50:14550`

### UDP

```bash
sim_vehicle.py -v ArduCopter -n 3 --auto-sysid --udp \
    --console --map
```

Each vehicle on port `5760 + instance*10`

## System IDs

### Auto System ID

```bash
# Automatically assigns SYSID = instance + 1
sim_vehicle.py -v ArduCopter -n 5 --auto-sysid
```

- Instance 0 → SYSID 1
- Instance 1 → SYSID 2
- etc.

### Manual System ID

```bash
# Single vehicle with specific SYSID
sim_vehicle.py -v ArduCopter --sysid 10
```

## MAVProxy with Multiple Vehicles

### Target Specific Vehicle

```bash
# In MAVProxy console
vehicle 1    # Select vehicle 1
vehicle 2    # Select vehicle 2
```

### Send to All

```bash
# Commands go to currently selected vehicle
# Use 'alllinks' for broadcast
alllinks arm throttle
```

## External Ground Station

### Mission Planner

Connect to:
- TCP: `127.0.0.1:5760` (first vehicle)
- UDP: `14550` (forwarded by MAVProxy)

### QGroundControl

Configure multiple UDP endpoints:
- Port 14550 + N for vehicle N

## Mixed Vehicle Types

Run separate sim_vehicle.py instances:

Terminal 1:
```bash
sim_vehicle.py -v ArduCopter -I 0 --sysid 1 --console --map
```

Terminal 2:
```bash
sim_vehicle.py -v Rover -I 1 --sysid 2 --console
```

## Instance Directories

Multiple instances create separate directories:

```
./0/eeprom.bin
./0/logs/
./1/eeprom.bin
./1/logs/
./2/eeprom.bin
./2/logs/
```

### Custom Directory

```bash
sim_vehicle.py -v ArduCopter -n 3 --use-dir my_swarm
```

## Port Assignments

For instance N:
- SITL serial: `5760 + N*10`
- RC input: `5501 + N*10`
- MAVLink output: `14550 + N*10`

## Performance Considerations

### Reduce Graphics
```bash
# No map for better performance
sim_vehicle.py -v ArduCopter -n 10 --auto-sysid --mcast --console
```

### Lower Speedup

```bash
# Slower simulation for many vehicles
sim_vehicle.py -v ArduCopter -n 10 --auto-sysid --mcast -S 1
```

### Separate Machines

Run vehicles on different machines:

Machine 1:
```bash
sim_vehicle.py -v ArduCopter -I 0 --mcast --console
```

Machine 2:
```bash
sim_vehicle.py -v ArduCopter -I 1 --mcast --sim-address 192.168.1.100
```

## Scripted Multi-Vehicle

### Python Control

```python
from pymavlink import mavutil

# Connect to multiple vehicles
vehicles = []
for i in range(5):
    port = 5760 + i * 10
    conn = mavutil.mavlink_connection(f'tcp:127.0.0.1:{port}')
    conn.wait_heartbeat()
    vehicles.append(conn)

# Command all vehicles
for v in vehicles:
    v.mav.command_long_send(
        v.target_system, v.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0, 1, 0, 0, 0, 0, 0, 0
    )
```

### MAVProxy Script

```bash
# Create script.txt
vehicle 1
arm throttle
mode GUIDED
takeoff 10

vehicle 2
arm throttle
mode GUIDED
takeoff 15
```

```bash
# Run with script
sim_vehicle.py -v ArduCopter -n 2 --auto-sysid \
    -m "--cmd='script script.txt'"
```

## Swarm Behaviors

### Formation Flying

Use Lua scripts or external controller to:
1. Set leader vehicle
2. Calculate offsets
3. Send GUIDED mode targets to followers

### Collision Avoidance

Enable ADSB simulation:
```bash
sim_vehicle.py -v ArduCopter -n 3 --auto-sysid \
    -P SIM_ADSB_COUNT=2 --console --map
```
