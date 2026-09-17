#!/usr/bin/env python3
"""
Find all Rover modes and their properties.

Usage: python find_rover_modes.py [--verbose]
"""

import os
import re
import sys

def find_modes(rover_dir):
    """Find all mode classes in the Rover directory."""
    modes = []

    mode_h = os.path.join(rover_dir, 'mode.h')
    if not os.path.exists(mode_h):
        print(f"Error: {mode_h} not found")
        return modes

    with open(mode_h, 'r') as f:
        content = f.read()

    # Find mode number enum
    enum_match = re.search(r'enum class Number[^{]*\{([^}]+)\}', content, re.DOTALL)
    if enum_match:
        enum_content = enum_match.group(1)
        for line in enum_content.split('\n'):
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
        mode_num_pattern = rf'{class_name}.*?mode_number\(\).*?Number::(\w+)'
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
            # Look for mode_xxx.cpp
            potential_file = f"mode_{mode['name'].lower()}.cpp"
            if os.path.exists(os.path.join(rover_dir, potential_file)):
                mode['file'] = potential_file

    # Parse mode properties from class definitions
    for mode in modes:
        if not mode['class']:
            continue

        class_pattern = rf'class\s+{mode["class"]}\s*:\s*public\s+Mode\s*\{{([^}}]+)\}}'
        class_match = re.search(class_pattern, content, re.DOTALL)
        if class_match:
            class_content = class_match.group(1)

            # Check for is_autopilot_mode
            if 'is_autopilot_mode' in class_content:
                if 'return true' in class_content.split('is_autopilot_mode')[1].split(';')[0]:
                    mode['properties']['autopilot'] = True
                else:
                    mode['properties']['autopilot'] = False

            # Check for requires_position
            if 'requires_position' in class_content:
                if 'return true' in class_content.split('requires_position')[1].split(';')[0]:
                    mode['properties']['requires_position'] = True

    return modes

def main():
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    # Find Rover directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    rover_dir = os.path.join(script_dir, '..', '..', '..', '..', 'Rover')
    rover_dir = os.path.normpath(rover_dir)

    if not os.path.exists(rover_dir):
        print(f"Error: Rover directory not found at {rover_dir}")
        sys.exit(1)

    modes = find_modes(rover_dir)

    # Sort by mode number
    modes.sort(key=lambda m: m['number'])

    print("Rover Flight Modes")
    print("=" * 60)
    print(f"{'Name':<15} {'#':>3} {'Class':<20} {'File':<25}")
    print("-" * 60)

    for mode in modes:
        file_str = mode['file'] or '-'
        class_str = mode['class'] or '-'
        print(f"{mode['name']:<15} {mode['number']:>3} {class_str:<20} {file_str:<25}")

    if verbose:
        print("\nMode Properties:")
        print("-" * 60)
        for mode in modes:
            if mode['properties']:
                props = ', '.join(f"{k}={v}" for k, v in mode['properties'].items())
                print(f"{mode['name']}: {props}")

    print(f"\nTotal: {len(modes)} modes")

if __name__ == '__main__':
    main()
