#!/usr/bin/env python3
"""
Find all backends (drivers) for a given ArduPilot sensor library.

Usage:
    python find_sensor_backends.py AP_Baro
    python find_sensor_backends.py AP_GPS
    python find_sensor_backends.py AP_InertialSensor
"""

import os
import sys
import re
from pathlib import Path


def find_ardupilot_root():
    """Find the ArduPilot root directory."""
    # Start from script location and search upward
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "ArduCopter").exists() and (current / "libraries").exists():
            return current
        current = current.parent

    # Try current working directory
    cwd = Path.cwd()
    while cwd != cwd.parent:
        if (cwd / "ArduCopter").exists() and (cwd / "libraries").exists():
            return cwd
        cwd = cwd.parent

    return None


def find_backends(library_name: str, ardupilot_root: Path) -> dict:
    """Find all backend files for a sensor library."""
    lib_path = ardupilot_root / "libraries" / library_name

    if not lib_path.exists():
        print(f"Error: Library {library_name} not found at {lib_path}")
        return {}

    results = {
        "library": library_name,
        "path": str(lib_path),
        "backends": [],
        "frontend": None,
        "backend_base": None,
    }

    # Find all .cpp and .h files
    for f in lib_path.glob("*.h"):
        name = f.stem

        # Skip config files
        if "_config" in name:
            continue

        # Identify frontend (main class)
        if name == library_name:
            results["frontend"] = name
            continue

        # Identify backend base class
        if name.endswith("_Backend"):
            results["backend_base"] = name
            continue

        # Everything else starting with library name is a backend
        if name.startswith(library_name + "_"):
            backend_name = name.replace(library_name + "_", "")

            # Read file to find supported devices
            content = f.read_text(errors="ignore")

            # Try to extract class name and supported devices
            class_match = re.search(r"class\s+(\w+)\s*:", content)
            class_name = class_match.group(1) if class_match else name

            # Look for device IDs or names
            devices = []
            id_matches = re.findall(r"#define\s+\w+_(?:CHIP_)?ID\s+0x([0-9A-Fa-f]+)", content)
            devices.extend([f"0x{m}" for m in id_matches])

            results["backends"].append({
                "name": backend_name,
                "class": class_name,
                "header": f.name,
                "devices": devices,
            })

    # Sort backends alphabetically
    results["backends"].sort(key=lambda x: x["name"])

    return results


def print_results(results: dict):
    """Pretty print the results."""
    if not results:
        return

    print(f"\n{'=' * 60}")
    print(f"Sensor Library: {results['library']}")
    print(f"Path: {results['path']}")
    print(f"{'=' * 60}")

    if results["frontend"]:
        print(f"\nFrontend: {results['frontend']}.h")

    if results["backend_base"]:
        print(f"Backend Base: {results['backend_base']}.h")

    print(f"\nBackends ({len(results['backends'])} found):")
    print("-" * 40)

    for backend in results["backends"]:
        print(f"  {backend['name']}")
        print(f"    Class: {backend['class']}")
        if backend["devices"]:
            print(f"    Device IDs: {', '.join(backend['devices'])}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python find_sensor_backends.py <library_name>")
        print("\nExamples:")
        print("  python find_sensor_backends.py AP_Baro")
        print("  python find_sensor_backends.py AP_GPS")
        print("  python find_sensor_backends.py AP_InertialSensor")
        print("  python find_sensor_backends.py AP_Compass")
        print("  python find_sensor_backends.py AP_RangeFinder")
        sys.exit(1)

    library_name = sys.argv[1]

    # Find ArduPilot root
    root = find_ardupilot_root()
    if not root:
        print("Error: Could not find ArduPilot root directory")
        print("Run this script from within the ArduPilot repository")
        sys.exit(1)

    # Find and print backends
    results = find_backends(library_name, root)
    print_results(results)


if __name__ == "__main__":
    main()
