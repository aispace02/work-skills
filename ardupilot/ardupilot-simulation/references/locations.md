# Simulation Locations

## Location File

Predefined locations are in `Tools/autotest/locations.txt`

Format:
```
NAME=latitude,longitude,altitude,heading
```

## Using Locations

### Named Location

```bash
sim_vehicle.py -v ArduCopter -L CMAC --console --map
```

### Custom Location

```bash
# lat, lon, alt (m), heading (deg)
sim_vehicle.py -v ArduCopter -l 37.6256,-122.3324,10,90 --console --map
```

## Common Locations

### Australia

| Name | Description | Coordinates |
|------|-------------|-------------|
| `CMAC` | Canberra Model Aircraft Club (Default) | -35.363261, 149.165230 |
| `CMAC2` | CMAC alternate | -35.362889, 149.165221 |
| `CMAC_PILOTSBOX` | CMAC pilot box | -35.362734, 149.165300 |
| `Ballarat` | Ballarat, Victoria | -37.598705, 143.881744 |
| `Kingaroy` | Kingaroy, Queensland | -26.583528, 151.840440 |
| `SpringValley` | Spring Valley | -35.280252, 149.005821 |

### United States

| Name | Description | Coordinates |
|------|-------------|-------------|
| `AVC` | SparkFun AVC | 40.0713749, -105.2297889 |
| `AVC_copter` | AVC copter start | 40.072842, -105.230575 |
| `3DRBerkeley` | 3DR Berkeley | 37.872991, -122.302348 |
| `KSFO` | San Francisco airport | 37.619373, -122.376637 |
| `SFO_Bay` | San Francisco Bay | 37.62561973, -122.33235387 |

### Europe

| Name | Description | Coordinates |
|------|-------------|-------------|
| `BHV` | Germany | 53.547767, 8.626440 |
| `LGAT` | Greece | 37.889063, 23.731863 |
| `Rotherham` | UK | 53.275131, -1.19404 |

### Japan

| Name | Description | Coordinates |
|------|-------------|-------------|
| `Karuizawa` | Karuizawa | 36.323203, 138.618215 |
| `Hata` | Hata | 35.671497, 140.083934 |
| `KawaguchiLake` | Lake Kawaguchi | 35.4712023, 138.7450261 |

### Special Locations

| Name | Description | Use Case |
|------|-------------|----------|
| `GrandCanyon` | Grand Canyon | Terrain testing |
| `Pyramid` | Giza Pyramids | Visual reference |
| `KalaupapaCliffs` | Hawaii cliffs | Coastal testing |

## User Locations

Create custom locations in:
- `~/.config/ardupilot/locations.txt`
- Or set `ARDUPILOT_LOCATIONS` environment variable

Format same as main locations.txt:
```
MyHome=37.1234,-122.4567,50,180
TestField=40.5678,-105.1234,1500,90
```

## Location Selection by Vehicle

### Copter Locations
Prefer open areas with GPS coverage:
```bash
sim_vehicle.py -v ArduCopter -L CMAC
```

### Plane Locations
Need runway or suitable takeoff area:
```bash
sim_vehicle.py -v ArduPlane -L KSFO
```

### Rover Locations
Ground-based, moderate terrain:
```bash
sim_vehicle.py -v Rover -L CMAC
```

### Sub Locations
Water areas:
```bash
sim_vehicle.py -v ArduSub -L SFO_Bay
```

## Geocoder Fallback

If location not found, sim_vehicle.py attempts geocoding:

```bash
# Try city name (requires geocoder package)
sim_vehicle.py -v ArduCopter -L "San Francisco"
```

Requires:
```bash
pip install geocoder
```

## Multi-Vehicle Spacing

### Swarm Init File

Create `swarminit.txt`:
```
0=0,0,0,0
1=0,10,0,0
2=0,20,0,0
```

Format: `instance=x_offset,y_offset,z_offset,heading`

```bash
sim_vehicle.py -v ArduCopter -n 3 --swarm swarminit.txt -L CMAC
```

### Auto Offset Line

Space vehicles automatically:

```bash
# 10m apart along 90-degree bearing
sim_vehicle.py -v ArduCopter -n 5 --auto-offset-line 90,10 -L CMAC
```

## Altitude Reference

The altitude in location is:
- **Absolute altitude** (meters above sea level)
- Used as `HOME_ALT`
- Vehicle spawns at this altitude

For terrain following, actual ground level may differ.

## Heading Reference

Heading is in degrees:
- 0 = North
- 90 = East
- 180 = South
- 270 = West

Vehicle initial yaw matches this heading.
