#!/usr/bin/env python3
"""
Find AntennaTracker parameters, optionally filtered by prefix.

Usage:
    python tracker_params.py                    # All parameters
    python tracker_params.py YAW                # YAW parameters
    python tracker_params.py --subsystem servo  # Servo parameters
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
    params_file = os.path.join(script_dir, '..', '..', '..', '..', 'AntennaTracker', 'Parameters.cpp')
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
        'servo': 'SERVO',
        'yaw': 'YAW',
        'pitch': 'PITCH',
        'scan': 'SCAN',
        'onoff': 'ONOFF',
        'pid': '2SRV',
        'log': 'LOG',
        'gcs': 'GCS',
        'gps': 'GPS',
        'start': 'START',
        'alt': 'ALT',
        'distance': 'DISTANCE',
        'mav': 'MAV',
        'auto': 'AUTO',
        'initial': 'INITIAL',
        'safe': 'SAFE',
        'sysid': 'SYSID',
    }

    if subsystem:
        prefix = subsystem_prefixes.get(subsystem.lower(), subsystem.upper())

    params = find_subsystem_params(prefix)

    if prefix:
        print(f"Parameters matching '{prefix}':")
    else:
        print("All AntennaTracker Parameters:")
    print("=" * 70)

    for param in sorted(params, key=lambda p: p['name']):
        print(f"\n{param['name']}")
        print(f"  {param['display_name']}")
        desc = param['description']
        print(f"  {desc[:60]}..." if len(desc) > 60 else f"  {desc}")

    print(f"\nTotal: {len(params)} parameters")

if __name__ == '__main__':
    main()
