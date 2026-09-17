#!/usr/bin/env python3
"""
Find where a sensor library is used in vehicle code.

Usage:
    python find_sensor_usage.py AP_Baro
    python find_sensor_usage.py AP_GPS ArduCopter
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


def find_sensor_usage(library_name: str, ardupilot_root: Path, vehicle: str = None) -> dict:
    """Find usage of a sensor library in vehicle code."""

    # Determine singleton accessor pattern
    singleton_patterns = {
        "AP_InertialSensor": [r"AP::ins\(\)", r"ins\."],
        "AP_GPS": [r"AP::gps\(\)", r"gps\."],
        "AP_Compass": [r"AP::compass\(\)", r"compass\."],
        "AP_Baro": [r"AP::baro\(\)", r"barometer\.", r"baro\."],
        "AP_RangeFinder": [r"AP::rangefinder\(\)", r"rangefinder"],
        "AP_Airspeed": [r"AP::airspeed\(\)", r"airspeed"],
        "AP_OpticalFlow": [r"AP::opticalflow\(\)", r"optflow"],
        "AP_BattMonitor": [r"AP::battery\(\)", r"battery\."],
        "AP_Proximity": [r"AP::proximity\(\)", r"proximity"],
        "AP_AHRS": [r"AP::ahrs\(\)", r"ahrs\."],
    }

    patterns = singleton_patterns.get(library_name, [f"{library_name}"])

    # Vehicles to search
    vehicles = ["ArduCopter", "ArduPlane", "Rover", "ArduSub", "AntennaTracker", "Blimp"]
    if vehicle:
        vehicles = [vehicle]

    results = {
        "library": library_name,
        "patterns": patterns,
        "usage": {},
    }

    for veh in vehicles:
        veh_path = ardupilot_root / veh
        if not veh_path.exists():
            continue

        veh_usage = []

        for cpp_file in veh_path.glob("*.cpp"):
            content = cpp_file.read_text(errors="ignore")

            for pattern in patterns:
                for match in re.finditer(pattern, content):
                    # Get line number
                    line_num = content[:match.start()].count('\n') + 1

                    # Get the line
                    lines = content.split('\n')
                    if line_num <= len(lines):
                        line = lines[line_num - 1].strip()

                        veh_usage.append({
                            "file": cpp_file.name,
                            "line": line_num,
                            "code": line[:80] + ("..." if len(line) > 80 else ""),
                        })

        if veh_usage:
            results["usage"][veh] = veh_usage

    return results


def print_results(results: dict):
    """Print usage results."""
    print(f"\n{'=' * 70}")
    print(f"Usage of {results['library']} in Vehicle Code")
    print(f"{'=' * 70}")
    print(f"Search patterns: {', '.join(results['patterns'])}")

    if not results["usage"]:
        print("\nNo usage found.")
        return

    for vehicle, usages in results["usage"].items():
        print(f"\n{vehicle}/ ({len(usages)} occurrences)")
        print("-" * 40)

        # Group by file
        by_file = {}
        for u in usages:
            if u["file"] not in by_file:
                by_file[u["file"]] = []
            by_file[u["file"]].append(u)

        for filename, file_usages in sorted(by_file.items()):
            print(f"\n  {filename}:")
            for u in file_usages[:5]:  # Limit to first 5 per file
                print(f"    L{u['line']}: {u['code']}")
            if len(file_usages) > 5:
                print(f"    ... and {len(file_usages) - 5} more")


def main():
    if len(sys.argv) < 2:
        print("Usage: python find_sensor_usage.py <library_name> [vehicle]")
        print("\nExamples:")
        print("  python find_sensor_usage.py AP_Baro")
        print("  python find_sensor_usage.py AP_GPS ArduCopter")
        print("  python find_sensor_usage.py AP_InertialSensor ArduPlane")
        sys.exit(1)

    library_name = sys.argv[1]
    vehicle = sys.argv[2] if len(sys.argv) > 2 else None

    root = find_ardupilot_root()
    if not root:
        print("Error: Could not find ArduPilot root directory")
        sys.exit(1)

    results = find_sensor_usage(library_name, root, vehicle)
    print_results(results)


if __name__ == "__main__":
    main()
