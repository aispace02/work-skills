#!/usr/bin/env python3
"""
Find all ArduPlane flight modes and their properties.

Usage: python find_plane_modes.py [--verbose]
"""

import os
import re
import sys

def find_modes(plane_dir):
    """Find all mode classes in the ArduPlane directory."""
    modes = []

    mode_h = os.path.join(plane_dir, 'mode.h')
    if not os.path.exists(mode_h):
        print(f"Error: {mode_h} not found")
        return modes

    with open(mode_h, 'r') as f:
        content = f.read()

    # Find mode number enum
    enum_match = re.search(r'enum Number\s*:\s*uint8_t\s*\{([^}]+)\}', content, re.DOTALL)
    if enum_match:
        enum_content = enum_match.group(1)
        for line in enum_content.split('\n'):
            # Match patterns like "MANUAL = 0," or "FLY_BY_WIRE_A = 5,"
            match = re.match(r'\s*(\w+)\s*=\s*(\d+)', line)
            if match:
                modes.append({
                    'name': match.group(1),
                    'number': int(match.group(2)),
                    'class': None,
                    'file': None,
                    'properties': {}
                })

    # Find mode classes
    class_pattern = r'class\s+(Mode\w*)\s*:\s*public\s+Mode\s*\{'
    for match in re.finditer(class_pattern, content):
        class_name = match.group(1)

        # Find mode number for this class
        # Look for "mode_number() const override { return Number::XXX; }"
        mode_num_pattern = rf'class\s+{class_name}.*?Number::(\w+)'
        mode_match = re.search(mode_num_pattern, content, re.DOTALL)
        if mode_match:
            mode_name = mode_match.group(1)
            for mode in modes:
                if mode['name'] == mode_name:
                    mode['class'] = class_name
                    break

    # Find mode files
    for mode in modes:
        if mode['class']:
            # Convert class name to file name
            # ModeManual -> mode_manual.cpp
            # ModeFBWA -> mode_fbwa.cpp
            class_lower = mode['class'].replace('Mode', '').lower()
            potential_files = [
                f"mode_{class_lower}.cpp",
                f"mode_{mode['name'].lower()}.cpp",
            ]
            for potential_file in potential_files:
                if os.path.exists(os.path.join(plane_dir, potential_file)):
                    mode['file'] = potential_file
                    break

    return modes

def main():
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    # Find ArduPlane directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plane_dir = os.path.join(script_dir, '..', '..', '..', '..', 'ArduPlane')
    plane_dir = os.path.normpath(plane_dir)

    if not os.path.exists(plane_dir):
        print(f"Error: ArduPlane directory not found at {plane_dir}")
        sys.exit(1)

    modes = find_modes(plane_dir)

    # Sort by mode number
    modes.sort(key=lambda m: m['number'])

    print("ArduPlane Flight Modes")
    print("=" * 70)
    print(f"{'Name':<20} {'#':>3} {'Class':<20} {'File':<25}")
    print("-" * 70)

    for mode in modes:
        file_str = mode['file'] or '-'
        class_str = mode['class'] or '-'
        print(f"{mode['name']:<20} {mode['number']:>3} {class_str:<20} {file_str:<25}")

    print(f"\nTotal: {len(modes)} modes")

    if verbose:
        print("\nMode Categories:")
        print("-" * 40)

        vtol_modes = [m for m in modes if 'Q' in m['name']]
        auto_modes = [m for m in modes if m['name'] in ['AUTO', 'RTL', 'LOITER', 'GUIDED', 'CIRCLE']]
        manual_modes = [m for m in modes if m['name'] in ['MANUAL', 'ACRO', 'TRAINING']]
        assisted_modes = [m for m in modes if m['name'] in ['STABILIZE', 'FLY_BY_WIRE_A', 'FLY_BY_WIRE_B', 'CRUISE']]

        print(f"Manual: {', '.join(m['name'] for m in manual_modes)}")
        print(f"Assisted: {', '.join(m['name'] for m in assisted_modes)}")
        print(f"Autonomous: {', '.join(m['name'] for m in auto_modes)}")
        print(f"VTOL: {', '.join(m['name'] for m in vtol_modes)}")

if __name__ == '__main__':
    main()
