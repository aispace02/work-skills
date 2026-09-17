#!/usr/bin/env python3
"""
Find all AntennaTracker modes and their properties.

Usage: python find_tracker_modes.py [--verbose]
"""

import os
import re
import sys

def find_modes(tracker_dir):
    """Find all mode classes in the AntennaTracker directory."""
    modes = []

    mode_h = os.path.join(tracker_dir, 'mode.h')
    if not os.path.exists(mode_h):
        print(f"Error: {mode_h} not found")
        return modes

    with open(mode_h, 'r') as f:
        content = f.read()

    # Find mode number enum
    enum_match = re.search(r'enum class Number\s*\{([^}]+)\}', content, re.DOTALL)
    if enum_match:
        enum_content = enum_match.group(1)
        for line in enum_content.split('\n'):
            # Match patterns like "MANUAL=0," or "MANUAL = 1,"
            match = re.match(r'\s*(\w+)\s*=\s*(\d+)', line)
            if match:
                modes.append({
                    'name': match.group(1),
                    'number': int(match.group(2)),
                    'class': None,
                    'file': None,
                    'requires_armed': None,
                })

    # Find mode classes and their properties
    class_pattern = r'class\s+(Mode\w+)\s*:\s*public\s+Mode\s*\{'
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

        # Find mode number - handle both "Number::MODE" and "Mode::Number::MODE"
        mode_num_match = re.search(r'(?:Mode::)?Number::(\w+)', class_content)
        if mode_num_match:
            mode_name = mode_num_match.group(1)
            for mode in modes:
                if mode['name'] == mode_name:
                    mode['class'] = class_name

                    # Find requires_armed_servos - handle multiline
                    armed_match = re.search(r'requires_armed_servos\(\)[^}]*return\s*(true|false)', class_content, re.DOTALL)
                    if armed_match:
                        mode['requires_armed'] = armed_match.group(1) == 'true'
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
                if os.path.exists(os.path.join(tracker_dir, potential_file)):
                    mode['file'] = potential_file
                    break

    return modes

def main():
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    # Find AntennaTracker directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tracker_dir = os.path.join(script_dir, '..', '..', '..', '..', 'AntennaTracker')
    tracker_dir = os.path.normpath(tracker_dir)

    if not os.path.exists(tracker_dir):
        print(f"Error: AntennaTracker directory not found at {tracker_dir}")
        sys.exit(1)

    modes = find_modes(tracker_dir)

    # Sort by mode number
    modes.sort(key=lambda m: m['number'])

    print("AntennaTracker Modes")
    print("=" * 70)
    print(f"{'Name':<15} {'#':>3} {'Armed':>6} {'Class':<20} {'File':<20}")
    print("-" * 70)

    for mode in modes:
        file_str = mode['file'] or '-'
        class_str = mode['class'] or '-'
        armed_str = 'Yes' if mode['requires_armed'] else ('No' if mode['requires_armed'] is False else '-')
        print(f"{mode['name']:<15} {mode['number']:>3} {armed_str:>6} {class_str:<20} {file_str:<20}")

    print(f"\nTotal: {len(modes)} modes")

    if verbose:
        print("\nMode Descriptions:")
        print("-" * 40)
        descriptions = {
            'MANUAL': 'Direct RC pass-through to servos',
            'STOP': 'Servos held/zeroed',
            'SCAN': 'Continuous pan/tilt scanning',
            'SERVOTEST': 'Servo diagnostic testing',
            'GUIDED': 'GCS-commanded pointing',
            'AUTO': 'Automatic vehicle tracking',
            'INITIALISING': 'Startup initialization',
        }
        for mode in modes:
            desc = descriptions.get(mode['name'], 'No description')
            print(f"{mode['name']}: {desc}")

if __name__ == '__main__':
    main()
