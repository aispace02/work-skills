#!/usr/bin/env python3
"""
Find all ArduCopter flight modes and their properties.

Usage: python find_copter_modes.py [--verbose]
"""

import os
import re
import sys

def find_modes(copter_dir):
    """Find all mode classes in the ArduCopter directory."""
    modes = []

    mode_h = os.path.join(copter_dir, 'mode.h')
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
                    'manual_throttle': None,
                    'is_autopilot': None
                })

    # Find mode classes and their properties
    class_pattern = r'class\s+(Mode\w*)\s*:\s*public\s+(?:Mode|ModeGuided|ModeAcro|ModeStabilize|ModeRTL)\s*\{'
    for match in re.finditer(class_pattern, content):
        class_name = match.group(1)

        # Get the class content (up to next class or end)
        start = match.end()
        # Find the matching closing brace
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
        mode_num_match = re.search(r'Number::([\w_]+)', class_content)
        if mode_num_match:
            mode_name = mode_num_match.group(1)
            for mode in modes:
                if mode['name'] == mode_name:
                    mode['class'] = class_name

                    # Find requires_GPS
                    gps_match = re.search(r'requires_GPS\(\)\s*const\s*override\s*\{\s*return\s*(true|false)', class_content)
                    if gps_match:
                        mode['requires_gps'] = gps_match.group(1) == 'true'

                    # Find has_manual_throttle
                    thr_match = re.search(r'has_manual_throttle\(\)\s*const\s*override\s*\{\s*return\s*(true|false)', class_content)
                    if thr_match:
                        mode['manual_throttle'] = thr_match.group(1) == 'true'

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
                if os.path.exists(os.path.join(copter_dir, potential_file)):
                    mode['file'] = potential_file
                    break

    return modes

def main():
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    # Find ArduCopter directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    copter_dir = os.path.join(script_dir, '..', '..', '..', '..', 'ArduCopter')
    copter_dir = os.path.normpath(copter_dir)

    if not os.path.exists(copter_dir):
        print(f"Error: ArduCopter directory not found at {copter_dir}")
        sys.exit(1)

    modes = find_modes(copter_dir)

    # Sort by mode number
    modes.sort(key=lambda m: m['number'])

    print("ArduCopter Flight Modes")
    print("=" * 100)
    print(f"{'Name':<15} {'#':>3} {'GPS':>4} {'ManThr':>7} {'Auto':>5} {'Class':<20} {'File':<25}")
    print("-" * 100)

    for mode in modes:
        file_str = mode['file'] or '-'
        class_str = mode['class'] or '-'
        gps_str = 'Yes' if mode['requires_gps'] else ('No' if mode['requires_gps'] is False else '-')
        thr_str = 'Yes' if mode['manual_throttle'] else ('No' if mode['manual_throttle'] is False else '-')
        auto_str = 'Yes' if mode['is_autopilot'] else ('No' if mode['is_autopilot'] is False else '-')
        print(f"{mode['name']:<15} {mode['number']:>3} {gps_str:>4} {thr_str:>7} {auto_str:>5} {class_str:<20} {file_str:<25}")

    print(f"\nTotal: {len(modes)} modes")

    if verbose:
        print("\nMode Categories:")
        print("-" * 40)

        manual_modes = [m for m in modes if m['manual_throttle'] == True]
        auto_throttle = [m for m in modes if m['manual_throttle'] == False and m['requires_gps'] == False]
        position_modes = [m for m in modes if m['requires_gps'] == True]
        autopilot_modes = [m for m in modes if m['is_autopilot'] == True]

        print(f"Manual throttle: {', '.join(m['name'] for m in manual_modes)}")
        print(f"Auto throttle (no GPS): {', '.join(m['name'] for m in auto_throttle)}")
        print(f"Position (GPS): {', '.join(m['name'] for m in position_modes)}")
        print(f"Autopilot: {', '.join(m['name'] for m in autopilot_modes)}")

if __name__ == '__main__':
    main()
