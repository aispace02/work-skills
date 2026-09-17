#!/usr/bin/env python3
"""
List available SITL frames for a vehicle type.

Usage:
    python list_frames.py                  # All vehicles
    python list_frames.py ArduCopter       # Copter frames
    python list_frames.py ArduPlane        # Plane frames
    python list_frames.py --external       # Only external simulator frames
"""

import os
import sys

# Add autotest to path
script_dir = os.path.dirname(os.path.abspath(__file__))
autotest_dir = os.path.join(script_dir, '..', '..', '..', '..', 'Tools', 'autotest')
sys.path.insert(0, autotest_dir)

from pysim.vehicleinfo import VehicleInfo

def list_frames(vehicle=None, external_only=False):
    """List available frames for vehicles."""
    vinfo = VehicleInfo()

    vehicles = [vehicle] if vehicle else list(vinfo.options.keys())

    for v in vehicles:
        if v not in vinfo.options:
            print(f"Unknown vehicle: {v}")
            print(f"Available: {', '.join(vinfo.options.keys())}")
            return

        print(f"\n{v} Frames")
        print("=" * 60)

        frames = vinfo.options[v].get("frames", {})
        default = vinfo.options[v].get("default_frame", "")

        # Separate internal and external frames
        internal_frames = []
        external_frames = []

        for frame_name, frame_info in sorted(frames.items()):
            is_external = frame_info.get("external", False)
            if is_external:
                external_frames.append((frame_name, frame_info))
            else:
                internal_frames.append((frame_name, frame_info))

        if not external_only and internal_frames:
            print("\nBuilt-in Frames:")
            print("-" * 40)
            for frame_name, frame_info in internal_frames:
                marker = " (default)" if frame_name == default else ""
                params = frame_info.get("default_params_filename", "")
                if isinstance(params, list):
                    params = params[-1] if params else ""
                params = os.path.basename(params) if params else ""
                print(f"  {frame_name:<25} {params}{marker}")

        if external_frames:
            print("\nExternal Simulator Frames:")
            print("-" * 40)
            for frame_name, frame_info in external_frames:
                params = frame_info.get("default_params_filename", "")
                if isinstance(params, list):
                    params = params[-1] if params else ""
                params = os.path.basename(params) if params else ""
                print(f"  {frame_name:<25} {params}")

        total = len(internal_frames) + len(external_frames)
        print(f"\nTotal: {total} frames")

def main():
    external_only = '--external' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('-')]

    vehicle = args[0] if args else None
    list_frames(vehicle, external_only)

if __name__ == '__main__':
    main()
