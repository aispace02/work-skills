#!/usr/bin/env python3
"""
List available SITL locations.

Usage:
    python list_locations.py              # All locations
    python list_locations.py CMAC         # Search for location
    python list_locations.py --region US  # Filter by region (approximate)
"""

import os
import sys
import re

def load_locations():
    """Load locations from locations.txt."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    locations_file = os.path.join(script_dir, '..', '..', '..', '..',
                                   'Tools', 'autotest', 'locations.txt')
    locations_file = os.path.normpath(locations_file)

    if not os.path.exists(locations_file):
        print(f"Error: {locations_file} not found")
        return []

    locations = []
    comment_regex = re.compile(r'\s*#.*')

    with open(locations_file, 'r') as f:
        for line in f:
            # Skip header
            if line.startswith('#NAME'):
                continue

            # Remove comments
            line = re.sub(comment_regex, '', line).strip()
            if not line:
                continue

            try:
                name, coords = line.split('=', 1)
                parts = coords.split(',')
                if len(parts) >= 4:
                    lat = float(parts[0])
                    lon = float(parts[1])
                    alt = float(parts[2])
                    hdg = float(parts[3])
                    locations.append({
                        'name': name.strip(),
                        'lat': lat,
                        'lon': lon,
                        'alt': alt,
                        'hdg': hdg
                    })
            except (ValueError, IndexError):
                continue

    return locations

def get_region(lat, lon):
    """Approximate region from coordinates."""
    if lat > 20 and lat < 50 and lon > -130 and lon < -60:
        return "US"
    elif lat > -45 and lat < -10 and lon > 110 and lon < 160:
        return "AU"
    elif lat > 35 and lat < 72 and lon > -15 and lon < 45:
        return "EU"
    elif lat > 25 and lat < 50 and lon > 120 and lon < 150:
        return "JP"
    else:
        return "Other"

def list_locations(search=None, region=None):
    """List available locations."""
    locations = load_locations()

    if not locations:
        return

    # Filter by search term
    if search:
        search_lower = search.lower()
        locations = [l for l in locations if search_lower in l['name'].lower()]

    # Filter by region
    if region:
        region_upper = region.upper()
        locations = [l for l in locations if get_region(l['lat'], l['lon']) == region_upper]

    if not locations:
        print("No matching locations found")
        return

    print("SITL Locations")
    print("=" * 80)
    print(f"{'Name':<25} {'Lat':>12} {'Lon':>12} {'Alt':>8} {'Hdg':>6} {'Region':<6}")
    print("-" * 80)

    for loc in sorted(locations, key=lambda x: x['name']):
        region_str = get_region(loc['lat'], loc['lon'])
        print(f"{loc['name']:<25} {loc['lat']:>12.6f} {loc['lon']:>12.6f} "
              f"{loc['alt']:>8.1f} {loc['hdg']:>6.0f} {region_str:<6}")

    print(f"\nTotal: {len(locations)} locations")

    print("\nUsage:")
    print("  sim_vehicle.py -v ArduCopter -L LOCATION_NAME --console --map")

def main():
    search = None
    region = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--region' and i + 1 < len(args):
            region = args[i + 1]
            i += 2
        elif not args[i].startswith('-'):
            search = args[i]
            i += 1
        else:
            i += 1

    list_locations(search, region)

if __name__ == '__main__':
    main()
