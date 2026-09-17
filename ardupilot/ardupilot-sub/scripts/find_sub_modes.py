#!/usr/bin/env python3
"""
Find all ArduSub flight modes and their properties.

Usage: python find_sub_modes.py [--verbose]
"""

import os
import re
import sys

def find_modes(sub_dir):
    """Find all mode classes in the ArduSub directory."""
    modes = []

    mode_h = os.path.join(sub_dir, 'mode.h')
    if not os.path.exists(mode_h):
        print(f"Error: {mode_h} not found")
        return modes

    with open(mode_h, 'r') as f:
        content = f.read()

    # Find mode number enum
    enum_match = re.search(r'enum class Number\s*:\s*uint8_t\s*\{([^}]+)\}', content, re.DOTALL)
    if enum_match:
        enum_content = enum_match.group(1)
        for line in enum_content.split('\n'):
            # Match patterns like "STABILIZE = 0," or "ALT_HOLD = 2,"
            match = re.match(r'\s*(\w+)\s*=\s*(\d+)', line)
            if match:
                modes.append({
                    'name': match.group(1),
                    'number': int(match.group(2)),
                    'class': None,
                    'file': None,
                    'requires_gps': None,
                    'requires_altitude': None,
                    'is_autopilot': None
                })

    # Find mode classes and their properties
    class_pattern = r'class\s+(Mode\w*)\s*:\s*public\s+(?:Mode|ModeAlthold|ModeGuided)\s*\{'
    for match in re.finditer(class_pattern, content):
        class_name = match.group(1)

        # Get the class content
        start = match.end()
        brace_count = 1
        end = start
        while brace_count > 0 and end < len(content):
            if content[end] == '{':
                brace_count += 1
            elif content[end] == '}':
                brace_count -= 1
            end += 1
        class_content = content[start:end]

        # Find mode number
        mode_num_match = re.search(r'Number::(\w+)', class_content)
        if mode_num_match:
            mode_name = mode_num_match.group(1)
            for mode in modes:
                if mode['name'] == mode_name:
                    mode['class'] = class_name

                    # Find requires_GPS
                    gps_match = re.search(r'requires_GPS\(\)\s*const\s*override\s*\{\s*return\s*(true|false)', class_content)
                    if gps_match:
                        mode['requires_gps'] = gps_match.group(1) == 'true'

                    # Find requires_altitude
                    alt_match = re.search(r'requires_altitude\(\)\s*const\s*override\s*\{\s*return\s*(true|false)', class_content)
                    if alt_match:
                        mode['requires_altitude'] = alt_match.group(1) == 'true'

                    # Find is_autopilot
                    auto_match = re.search(r'is_autopilot\(\)\s*const\s*override\s*\{\s*return\s*(true|false)', class_content)
                    if auto_match:
                        mode['is_autopilot'] = auto_match.group(1) == 'true'
                    break

    # Find mode files
    for mode in modes:
        if mode['class']:
            # Convert class name to file name
            class_lower = mode['class'].replace('Mode', '').lower()
            potential_files = [
                f"mode_{class_lower}.cpp",
                f"mode_{mode['name'].lower()}.cpp",
            ]
            for potential_file in potential_files:
                if os.path.exists(os.path.join(sub_dir, potential_file)):
                    mode['file'] = potential_file
                    break

    return modes

def main():
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    # Find ArduSub directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sub_dir = os.path.join(script_dir, '..', '..', '..', '..', 'ArduSub')
    sub_dir = os.path.normpath(sub_dir)

    if not os.path.exists(sub_dir):
        print(f"Error: ArduSub directory not found at {sub_dir}")
        sys.exit(1)

    modes = find_modes(sub_dir)

    # Sort by mode number
    modes.sort(key=lambda m: m['number'])

    print("ArduSub Flight Modes")
    print("=" * 90)
    print(f"{'Name':<15} {'#':>3} {'GPS':>4} {'Depth':>6} {'Auto':>5} {'Class':<20} {'File':<25}")
    print("-" * 90)

    for mode in modes:
        file_str = mode['file'] or '-'
        class_str = mode['class'] or '-'
        gps_str = 'Yes' if mode['requires_gps'] else ('No' if mode['requires_gps'] is False else '-')
        alt_str = 'Yes' if mode['requires_altitude'] else ('No' if mode['requires_altitude'] is False else '-')
        auto_str = 'Yes' if mode['is_autopilot'] else ('No' if mode['is_autopilot'] is False else '-')
        print(f"{mode['name']:<15} {mode['number']:>3} {gps_str:>4} {alt_str:>6} {auto_str:>5} {class_str:<20} {file_str:<25}")

    print(f"\nTotal: {len(modes)} modes")

    if verbose:
        print("\nMode Categories:")
        print("-" * 40)

        manual_modes = [m for m in modes if m['requires_gps'] == False and m['requires_altitude'] == False]
        depth_modes = [m for m in modes if m['requires_altitude'] == True and m['requires_gps'] == False]
        position_modes = [m for m in modes if m['requires_gps'] == True]

        print(f"Manual (no sensors): {', '.join(m['name'] for m in manual_modes)}")
        print(f"Depth hold: {', '.join(m['name'] for m in depth_modes)}")
        print(f"Position (GPS): {', '.join(m['name'] for m in position_modes)}")

if __name__ == '__main__':
    main()
