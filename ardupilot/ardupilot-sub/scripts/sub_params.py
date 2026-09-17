#!/usr/bin/env python3
"""
Find ArduSub parameters, optionally filtered by prefix or subsystem.

Usage:
    python sub_params.py                    # All parameters
    python sub_params.py FS_               # Failsafe parameters
    python sub_params.py --subsystem depth  # Depth-related parameters
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
    params_file = os.path.join(script_dir, '..', '..', '..', '..', 'ArduSub', 'Parameters.cpp')
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
        'depth': 'SURFACE',
        'surface': 'SURFACE',
        'pilot': 'PILOT_',
        'speed': 'PILOT_SPEED',
        'gain': 'JS_GAIN',
        'joystick': 'JS_',
        'js': 'JS_',
        'button': 'BTN',
        'btn': 'BTN',
        'failsafe': 'FS_',
        'fs': 'FS_',
        'leak': 'LEAK',
        'motor': 'MOT_',
        'mot': 'MOT_',
        'frame': 'FRAME',
        'acro': 'ACRO_',
        'attitude': 'ATC_',
        'atc': 'ATC_',
        'position': 'PSC_',
        'psc': 'PSC_',
        'wpnav': 'WPNAV_',
        'wp': 'WPNAV_',
        'circle': 'CIRCLE_',
        'surftrak': 'SURFTRAK',
        'terrain': 'TERRAIN',
        'log': 'LOG_',
        'rc': 'RC',
        'rcmap': 'RCMAP_',
    }

    if subsystem:
        prefix = subsystem_prefixes.get(subsystem.lower(), subsystem.upper() + '_')

    params = find_subsystem_params(prefix)

    if prefix:
        print(f"Parameters matching '{prefix}':")
    else:
        print("All ArduSub Parameters:")
    print("=" * 70)

    for param in sorted(params, key=lambda p: p['name']):
        print(f"\n{param['name']}")
        print(f"  {param['display_name']}")
        desc = param['description']
        print(f"  {desc[:60]}..." if len(desc) > 60 else f"  {desc}")

    print(f"\nTotal: {len(params)} parameters")

if __name__ == '__main__':
    main()
