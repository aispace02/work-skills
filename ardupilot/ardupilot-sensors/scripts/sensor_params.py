#!/usr/bin/env python3
"""
Extract parameters for a given ArduPilot sensor library.

Usage:
    python sensor_params.py AP_Baro
    python sensor_params.py AP_GPS
    python sensor_params.py AP_Compass
"""

import os
import sys
import re
from pathlib import Path


def find_ardupilot_root():
    """Find the ArduPilot root directory."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "ArduCopter").exists() and (current / "libraries").exists():
            return current
        current = current.parent

    cwd = Path.cwd()
    while cwd != cwd.parent:
        if (cwd / "ArduCopter").exists() and (cwd / "libraries").exists():
            return cwd
        cwd = cwd.parent

    return None


def extract_params(library_name: str, ardupilot_root: Path) -> list:
    """Extract parameter definitions from a sensor library."""
    lib_path = ardupilot_root / "libraries" / library_name

    if not lib_path.exists():
        print(f"Error: Library {library_name} not found at {lib_path}")
        return []

    params = []

    # Search all .cpp files for parameter definitions
    for cpp_file in lib_path.glob("*.cpp"):
        content = cpp_file.read_text(errors="ignore")

        # Find AP_GROUPINFO entries
        # Pattern: AP_GROUPINFO("NAME", idx, Class, member, default)
        groupinfo_pattern = r'AP_GROUPINFO\s*\(\s*"([^"]+)"\s*,\s*(\d+)\s*,\s*\w+\s*,\s*(\w+)\s*,\s*([^)]+)\)'

        for match in re.finditer(groupinfo_pattern, content):
            param_name = match.group(1)
            param_idx = match.group(2)
            member_name = match.group(3)
            default_val = match.group(4).strip()

            # Try to find the @Param comment block before this
            start_pos = match.start()
            block_start = content.rfind("// @Param:", 0, start_pos)

            description = ""
            units = ""
            range_str = ""
            values = ""

            if block_start != -1:
                block_end = start_pos
                block = content[block_start:block_end]

                # Extract description
                desc_match = re.search(r"@Description:\s*(.+?)(?=\n\s*//\s*@|\n\s*AP_)", block, re.DOTALL)
                if desc_match:
                    description = " ".join(desc_match.group(1).replace("//", "").split())

                # Extract units
                units_match = re.search(r"@Units:\s*(\S+)", block)
                if units_match:
                    units = units_match.group(1)

                # Extract range
                range_match = re.search(r"@Range:\s*(.+?)(?=\n|$)", block)
                if range_match:
                    range_str = range_match.group(1).strip()

                # Extract values
                values_match = re.search(r"@Values:\s*(.+?)(?=\n\s*//\s*@|\n\s*AP_)", block, re.DOTALL)
                if values_match:
                    values = " ".join(values_match.group(1).replace("//", "").split())

            params.append({
                "name": param_name,
                "index": param_idx,
                "member": member_name,
                "default": default_val,
                "description": description,
                "units": units,
                "range": range_str,
                "values": values,
                "file": cpp_file.name,
            })

    # Sort by name
    params.sort(key=lambda x: x["name"])

    return params


def print_params(library_name: str, params: list):
    """Pretty print parameters."""
    if not params:
        print(f"No parameters found for {library_name}")
        return

    print(f"\n{'=' * 70}")
    print(f"Parameters for {library_name}")
    print(f"{'=' * 70}")
    print(f"\nFound {len(params)} parameters:\n")

    for p in params:
        print(f"  {p['name']}")
        if p["description"]:
            # Wrap description
            desc = p["description"]
            if len(desc) > 60:
                desc = desc[:57] + "..."
            print(f"    Description: {desc}")
        if p["default"]:
            print(f"    Default: {p['default']}")
        if p["units"]:
            print(f"    Units: {p['units']}")
        if p["range"]:
            print(f"    Range: {p['range']}")
        if p["values"]:
            vals = p["values"]
            if len(vals) > 50:
                vals = vals[:47] + "..."
            print(f"    Values: {vals}")
        print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python sensor_params.py <library_name>")
        print("\nExamples:")
        print("  python sensor_params.py AP_Baro")
        print("  python sensor_params.py AP_GPS")
        print("  python sensor_params.py AP_Compass")
        print("  python sensor_params.py AP_RangeFinder")
        print("  python sensor_params.py AP_BattMonitor")
        sys.exit(1)

    library_name = sys.argv[1]

    root = find_ardupilot_root()
    if not root:
        print("Error: Could not find ArduPilot root directory")
        sys.exit(1)

    params = extract_params(library_name, root)
    print_params(library_name, params)


if __name__ == "__main__":
    main()
