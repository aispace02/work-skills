#!/usr/bin/env python3
"""
Find ArduCopter parameters, optionally filtered by prefix or subsystem.

Usage:
    python copter_params.py                    # All parameters
    python copter_params.py WPNAV_             # Waypoint nav parameters
    python copter_params.py --subsystem loiter # Loiter parameters
"""

import os
import re
import sys

def parse_parameters(params_file):
    """Parse parameter definitions from Parameters.cpp."""
    params = []

    with open(params_file, 'r') as f:
        content = f.read()

    # Find @Param comments
    param_comment_pattern = r'// @Param:\s*(\S+)\s*\n\s*// @DisplayName:\s*([^\n]+)\s*\n\s*// @Description:\s*([^\n]+)'

    for match in re.finditer(param_comment_pattern, content):
        param_name = match.group(1)
        display_name = match.group(2).strip()
        description = match.group(3).strip()

        params.append({
            'name': param_name,
            'display_name': display_name,
            'description': description
        })

    return params

def find_subsystem_params(prefix):
    """Find parameters for a specific subsystem by prefix."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    params_file = os.path.join(script_dir, '..', '..', '..', '..', 'ArduCopter', 'Parameters.cpp')
    params_file = os.path.normpath(params_file)

    if not os.path.exists(params_file):
        print(f"Error: {params_file} not found")
        return []

    params = parse_parameters(params_file)

    if prefix:
        prefix_upper = prefix.upper()
        params = [p for p in params if p['name'].upper().startswith(prefix_upper)]

    return params

def main():
    prefix = None
    subsystem = None

    # Parse arguments
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--subsystem' and i + 1 < len(args):
            subsystem = args[i + 1]
            i += 2
        elif not args[i].startswith('-'):
            prefix = args[i]
            i += 1
        else:
            i += 1

    # Map subsystems to prefixes
    subsystem_prefixes = {
        'pilot': 'PILOT_',
        'acro': 'ACRO_',
        'wpnav': 'WPNAV_',
        'wp': 'WPNAV_',
        'loiter': 'LOIT_',
        'loit': 'LOIT_',
        'rtl': 'RTL_',
        'land': 'LAND_',
        'circle': 'CIRCLE_',
        'failsafe': 'FS_',
        'fs': 'FS_',
        'motor': 'MOT_',
        'mot': 'MOT_',
        'attitude': 'ATC_',
        'atc': 'ATC_',
        'position': 'PSC_',
        'psc': 'PSC_',
        'angle': 'ANGLE',
        'simple': 'SIMPLE',
        'arming': 'ARMING_',
        'arm': 'ARMING_',
        'disarm': 'DISARM',
        'throw': 'THROW_',
        'brake': 'BRAKE_',
        'poshold': 'PHLD_',
        'phld': 'PHLD_',
        'autotune': 'AUTOTUNE_',
        'atune': 'AUTOTUNE_',
        'zigzag': 'ZIGZ_',
        'flowhold': 'FHLD_',
        'fhld': 'FHLD_',
        'surftrak': 'SURFTRAK_',
        'terrain': 'TERRAIN_',
        'avoid': 'AVOID_',
        'fence': 'FENCE_',
        'log': 'LOG_',
        'rc': 'RC',
        'servo': 'SERVO',
        'batt': 'BATT_',
        'battery': 'BATT_',
    }

    if subsystem:
        prefix = subsystem_prefixes.get(subsystem.lower(), subsystem.upper() + '_')

    params = find_subsystem_params(prefix)

    if prefix:
        print(f"Parameters matching '{prefix}':")
    else:
        print("All ArduCopter Parameters:")
    print("=" * 70)

    for param in sorted(params, key=lambda p: p['name']):
        print(f"\n{param['name']}")
        print(f"  {param['display_name']}")
        desc = param['description']
        print(f"  {desc[:60]}..." if len(desc) > 60 else f"  {desc}")

    print(f"\nTotal: {len(params)} parameters")

if __name__ == '__main__':
    main()
