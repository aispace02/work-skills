#!/usr/bin/env python3
"""
Find all parameters for an ArduPilot control library.

Usage:
    python find_control_params.py AC_AttitudeControl
    python find_control_params.py AC_PosControl
    python find_control_params.py --prefix ATC_
    python find_control_params.py --prefix PSC_
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


def find_params_by_prefix(prefix: str, ardupilot_root: Path) -> list:
    """Find parameters matching a prefix in vehicle parameter files."""
    params = []

    # Search in vehicle directories
    vehicle_dirs = ["ArduCopter", "ArduPlane", "Rover", "ArduSub"]

    for vehicle in vehicle_dirs:
        param_file = ardupilot_root / vehicle / "Parameters.cpp"
        if not param_file.exists():
            continue

        content = param_file.read_text(errors="ignore")

        # Find parameter definitions
        pattern = rf'@Param:\s*({re.escape(prefix)}\w+)'
        matches = re.findall(pattern, content)

        for match in matches:
            if match not in [p["name"] for p in params]:
                # Try to get description
                desc_pattern = rf'@Param:\s*{re.escape(match)}\s*\n\s*//\s*@DisplayName:\s*([^\n]+)'
                desc_match = re.search(desc_pattern, content)
                desc = desc_match.group(1) if desc_match else ""

                params.append({
                    "name": match,
                    "description": desc,
                    "vehicle": vehicle
                })

    return params


def find_params_in_library(library_name: str, ardupilot_root: Path) -> dict:
    """Find parameters defined in a control library."""
    lib_path = ardupilot_root / "libraries" / library_name

    if not lib_path.exists():
        print(f"Error: Library {library_name} not found at {lib_path}")
        return {}

    results = {
        "library": library_name,
        "path": str(lib_path),
        "parameters": [],
        "prefixes": set(),
    }

    # Search all cpp files for AP_GROUPINFO
    for cpp_file in lib_path.glob("*.cpp"):
        content = cpp_file.read_text(errors="ignore")

        # Find AP_GROUPINFO entries
        groupinfo_pattern = r'AP_GROUPINFO\s*\(\s*"([^"]+)"'
        matches = re.findall(groupinfo_pattern, content)

        for name in matches:
            results["parameters"].append({
                "name": name,
                "file": cpp_file.name,
            })

        # Find AP_SUBGROUPINFO (nested parameter tables)
        subgroup_pattern = r'AP_SUBGROUPINFO\s*\([^,]+,\s*"([^"]+)"'
        submatches = re.findall(subgroup_pattern, content)

        for prefix in submatches:
            results["prefixes"].add(prefix)

    # Try to identify common prefixes
    if results["parameters"]:
        # Look for prefix in var_info table
        for cpp_file in lib_path.glob("*.cpp"):
            content = cpp_file.read_text(errors="ignore")
            prefix_pattern = r'AP_GROUPINFO\s*\(\s*"(\w+)_'
            prefix_matches = re.findall(prefix_pattern, content)
            for p in prefix_matches:
                results["prefixes"].add(p + "_")

    results["prefixes"] = list(results["prefixes"])
    return results


def print_results(results: dict):
    """Pretty print the results."""
    if not results:
        return

    print(f"\n{'=' * 60}")
    print(f"Control Library: {results['library']}")
    print(f"Path: {results['path']}")
    print(f"{'=' * 60}")

    if results.get("prefixes"):
        print(f"\nParameter Prefixes: {', '.join(results['prefixes'])}")

    print(f"\nParameters ({len(results['parameters'])} found):")
    print("-" * 40)

    for param in sorted(results["parameters"], key=lambda x: x["name"]):
        print(f"  {param['name']}")
        if param.get("file"):
            print(f"    File: {param['file']}")


def print_prefix_results(prefix: str, params: list):
    """Print parameters found by prefix search."""
    print(f"\n{'=' * 60}")
    print(f"Parameters with prefix: {prefix}")
    print(f"{'=' * 60}")
    print(f"\nFound {len(params)} parameters:")
    print("-" * 40)

    for param in sorted(params, key=lambda x: x["name"]):
        print(f"  {param['name']}")
        if param.get("description"):
            print(f"    {param['description']}")
        if param.get("vehicle"):
            print(f"    Vehicle: {param['vehicle']}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python find_control_params.py <library_name>")
        print("  python find_control_params.py --prefix <prefix>")
        print("\nExamples:")
        print("  python find_control_params.py AC_AttitudeControl")
        print("  python find_control_params.py AC_PosControl")
        print("  python find_control_params.py --prefix ATC_")
        print("  python find_control_params.py --prefix PSC_")
        print("  python find_control_params.py --prefix WPNAV_")
        sys.exit(1)

    root = find_ardupilot_root()
    if not root:
        print("Error: Could not find ArduPilot root directory")
        sys.exit(1)

    if sys.argv[1] == "--prefix":
        if len(sys.argv) < 3:
            print("Error: --prefix requires a prefix argument")
            sys.exit(1)
        prefix = sys.argv[2]
        params = find_params_by_prefix(prefix, root)
        print_prefix_results(prefix, params)
    else:
        library_name = sys.argv[1]
        results = find_params_in_library(library_name, root)
        print_results(results)


if __name__ == "__main__":
    main()
