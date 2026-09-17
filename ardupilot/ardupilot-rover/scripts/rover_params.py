#!/usr/bin/env python3
"""
Find Rover parameters, optionally filtered by prefix or subsystem.

Usage:
    python rover_params.py                    # All parameters
    python rover_params.py WP_                # Waypoint parameters
    python rover_params.py --subsystem motors # Motor parameters
"""

import os
import re
import sys

def parse_parameters(params_file):
    """Parse parameter definitions from Parameters.cpp."""
    params = []

    with open(params_file, 'r') as f:
        content = f.read()

    # Pattern for GSCALAR/GGROUP/AP_GROUPINFO
    patterns = [
        # GSCALAR(var, "NAME", default)
        r'GSCALAR\s*\(\s*(\w+)\s*,\s*"([^"]+)"\s*,\s*([^)]+)\)',
        # AP_GROUPINFO("NAME", idx, class, var, default)
        r'AP_GROUPINFO\s*\(\s*"([^"]+)"\s*,\s*\d+\s*,\s*\w+\s*,\s*(\w+)\s*,\s*([^)]+)\)',
        # AP_SUBGROUPINFO with prefix
        r'AP_SUBGROUPINFO\s*\(\s*(\w+)\s*,\s*"([^"]+)"\s*,'
    ]

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
    params_file = os.path.join(script_dir, '..', '..', '..', '..', 'Rover', 'Parameters.cpp')
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
        'motors': 'MOT_',
        'motor': 'MOT_',
        'wp': 'WP_',
        'waypoint': 'WP_',
        'nav': 'WP_',
        'atc': 'ATC_',
        'attitude': 'ATC_',
        'control': 'ATC_',
        'sail': 'SAIL_',
        'sailboat': 'SAIL_',
        'fs': 'FS_',
        'failsafe': 'FS_',
        'turn': 'TURN_',
        'cruise': 'CRUISE_',
        'loit': 'LOIT_',
        'loiter': 'LOIT_',
        'srtl': 'SRTL_',
        'smartrtl': 'SRTL_',
        'circ': 'CIRC_',
        'circle': 'CIRC_',
        'dock': 'DOCK_',
        'avoid': 'AVOID_',
    }

    if subsystem:
        prefix = subsystem_prefixes.get(subsystem.lower(), subsystem.upper() + '_')

    params = find_subsystem_params(prefix)

    if prefix:
        print(f"Parameters matching '{prefix}':")
    else:
        print("All Rover Parameters:")
    print("=" * 70)

    for param in sorted(params, key=lambda p: p['name']):
        print(f"\n{param['name']}")
        print(f"  {param['display_name']}")
        print(f"  {param['description'][:60]}..." if len(param['description']) > 60 else f"  {param['description']}")

    print(f"\nTotal: {len(params)} parameters")

if __name__ == '__main__':
    main()
