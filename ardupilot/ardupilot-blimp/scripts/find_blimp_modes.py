#!/usr/bin/env python3
"""
Find all Blimp flight modes and their properties.

Usage: python find_blimp_modes.py [--verbose]
"""

import os
import re
import sys

def find_modes(blimp_dir):
    """Find all mode classes in the Blimp directory."""
    modes = []

    mode_h = os.path.join(blimp_dir, 'mode.h')
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
            # Match patterns like "LAND = 0," or "MANUAL = 1,"
            match = re.match(r'\s*(\w+)\s*=\s*(\d+)', line)
            if match:
                modes.append({
                    'name': match.group(1),
                    'number': int(match.group(2)),
                    'class': None,
                    'file': None,
                    'requires_gps': None,
                    'manual_throttle': None
                })

    # Find mode classes and their properties
    class_pattern = r'class\s+(Mode\w*)\s*:\s*public\s+Mode\s*\{'
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
        mode_num_match = re.search(r'Number::([\w_]+)', class_content)
        if mode_num_match:
            mode_name = mode_num_match.group(1)
            for mode in modes:
                if mode['name'] == mode_name:
                    mode['class'] = class_name

                    # Find requires_GPS
                    gps_match = re.search(r'requires_GPS\(\)\s*const\s*override[^{]*\{\s*return\s*(true|false)', class_content)
                    if gps_match:
                        mode['requires_gps'] = gps_match.group(1) == 'true'

                    # Find has_manual_throttle
                    thr_match = re.search(r'has_manual_throttle\(\)\s*const\s*override[^{]*\{\s*return\s*(true|false)', class_content)
                    if thr_match:
                        mode['manual_throttle'] = thr_match.group(1) == 'true'
                    break

    # Find mode files
    for mode in modes:
        if mode['class']:
            class_lower = mode['class'].replace('Mode', '').lower()
            potential_files = [
                f"mode_{class_lower}.cpp",
                f"mode_{mode['name'].lower()}.cpp",
            ]
            for potential_file in potential_files:
                if os.path.exists(os.path.join(blimp_dir, potential_file)):
                    mode['file'] = potential_file
                    break

    return modes

def main():
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    # Find Blimp directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    blimp_dir = os.path.join(script_dir, '..', '..', '..', '..', 'Blimp')
    blimp_dir = os.path.normpath(blimp_dir)

    if not os.path.exists(blimp_dir):
        print(f"Error: Blimp directory not found at {blimp_dir}")
        sys.exit(1)

    modes = find_modes(blimp_dir)

    # Sort by mode number
    modes.sort(key=lambda m: m['number'])

    print("Blimp Flight Modes")
    print("=" * 80)
    print(f"{'Name':<15} {'#':>3} {'GPS':>4} {'Manual':>7} {'Class':<15} {'File':<20}")
    print("-" * 80)

    for mode in modes:
        file_str = mode['file'] or '-'
        class_str = mode['class'] or '-'
        gps_str = 'Yes' if mode['requires_gps'] else ('No' if mode['requires_gps'] is False else '-')
        thr_str = 'Yes' if mode['manual_throttle'] else ('No' if mode['manual_throttle'] is False else '-')
        print(f"{mode['name']:<15} {mode['number']:>3} {gps_str:>4} {thr_str:>7} {class_str:<15} {file_str:<20}")

    print(f"\nTotal: {len(modes)} modes")

    if verbose:
        print("\nMode Categories:")
        print("-" * 40)

        manual_modes = [m for m in modes if m['manual_throttle'] == True]
        auto_modes = [m for m in modes if m['manual_throttle'] == False]
        gps_modes = [m for m in modes if m['requires_gps'] == True]

        print(f"Manual: {', '.join(m['name'] for m in manual_modes)}")
        print(f"Automatic: {', '.join(m['name'] for m in auto_modes)}")
        print(f"GPS required: {', '.join(m['name'] for m in gps_modes)}")

if __name__ == '__main__':
    main()
