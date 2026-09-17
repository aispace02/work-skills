#!/usr/bin/env python3
"""
Quick simulation launcher with sensible defaults.

Usage:
    python quick_sim.py copter              # Basic copter
    python quick_sim.py plane               # Basic plane
    python quick_sim.py rover               # Basic rover
    python quick_sim.py copter -f hexa      # Hexacopter
    python quick_sim.py copter -n 3         # 3 copters
    python quick_sim.py copter --gazebo     # With Gazebo
"""

import os
import sys
import subprocess

# Vehicle aliases
VEHICLE_MAP = {
    'copter': 'ArduCopter',
    'plane': 'ArduPlane',
    'rover': 'Rover',
    'sub': 'ArduSub',
    'blimp': 'Blimp',
    'tracker': 'AntennaTracker',
    'heli': 'Helicopter',
}

# Default frames for external simulators
EXTERNAL_FRAMES = {
    'gazebo': {
        'ArduCopter': 'gazebo-iris',
        'ArduPlane': 'gazebo-zephyr',
        'Rover': 'gazebo-rover',
    },
    'airsim': {
        'ArduCopter': 'airsim-copter',
        'Rover': 'airsim-rover',
    },
    'xplane': {
        'ArduPlane': 'xplane',
    },
}

def build_command(args):
    """Build sim_vehicle.py command from arguments."""
    # Find sim_vehicle.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sim_vehicle = os.path.join(script_dir, '..', '..', '..', '..',
                                'Tools', 'autotest', 'sim_vehicle.py')
    sim_vehicle = os.path.normpath(sim_vehicle)

    if not os.path.exists(sim_vehicle):
        print(f"Error: sim_vehicle.py not found at {sim_vehicle}")
        sys.exit(1)

    # Parse arguments
    vehicle = None
    frame = None
    location = None
    count = 1
    speedup = 1
    external = None
    debug = False
    wipe = False
    extra_args = []

    i = 0
    while i < len(args):
        arg = args[i]

        if arg in VEHICLE_MAP:
            vehicle = VEHICLE_MAP[arg]
        elif arg in VEHICLE_MAP.values():
            vehicle = arg
        elif arg == '-f' and i + 1 < len(args):
            frame = args[i + 1]
            i += 1
        elif arg == '-L' and i + 1 < len(args):
            location = args[i + 1]
            i += 1
        elif arg == '-n' and i + 1 < len(args):
            count = int(args[i + 1])
            i += 1
        elif arg == '-S' and i + 1 < len(args):
            speedup = int(args[i + 1])
            i += 1
        elif arg == '--gazebo':
            external = 'gazebo'
        elif arg == '--airsim':
            external = 'airsim'
        elif arg == '--xplane':
            external = 'xplane'
        elif arg == '-g' or arg == '--gdb':
            debug = True
        elif arg == '-w' or arg == '--wipe':
            wipe = True
        elif arg.startswith('-'):
            extra_args.append(arg)
            if i + 1 < len(args) and not args[i + 1].startswith('-'):
                extra_args.append(args[i + 1])
                i += 1
        i += 1

    if not vehicle:
        print("Usage: quick_sim.py <vehicle> [options]")
        print("\nVehicles: copter, plane, rover, sub, blimp, tracker, heli")
        print("\nOptions:")
        print("  -f FRAME      Frame type")
        print("  -L LOCATION   Start location")
        print("  -n COUNT      Number of vehicles")
        print("  -S SPEEDUP    Simulation speedup")
        print("  --gazebo      Use Gazebo simulator")
        print("  --airsim      Use AirSim simulator")
        print("  --xplane      Use X-Plane simulator")
        print("  -g, --gdb     Run with GDB debugger")
        print("  -w, --wipe    Wipe parameters")
        sys.exit(1)

    # Build command
    cmd = ['python3', sim_vehicle, '-v', vehicle]

    # Handle external simulator frames
    if external and not frame:
        if external in EXTERNAL_FRAMES and vehicle in EXTERNAL_FRAMES[external]:
            frame = EXTERNAL_FRAMES[external][vehicle]
            cmd.extend(['--model', 'JSON'])
        else:
            print(f"Warning: No {external} frame for {vehicle}")

    if frame:
        cmd.extend(['-f', frame])

    if location:
        cmd.extend(['-L', location])

    if count > 1:
        cmd.extend(['-n', str(count), '--auto-sysid', '--mcast'])

    if speedup != 1:
        cmd.extend(['-S', str(speedup)])

    if debug:
        cmd.append('-G')

    if wipe:
        cmd.append('-w')

    # Always add console and map
    cmd.extend(['--console', '--map'])

    cmd.extend(extra_args)

    return cmd

def main():
    if len(sys.argv) < 2:
        print("Quick SITL Launcher")
        print("=" * 40)
        print("\nUsage: quick_sim.py <vehicle> [options]")
        print("\nExamples:")
        print("  quick_sim.py copter")
        print("  quick_sim.py plane -f quadplane")
        print("  quick_sim.py copter -n 3 -L CMAC")
        print("  quick_sim.py copter --gazebo")
        sys.exit(0)

    cmd = build_command(sys.argv[1:])

    print("Running:", ' '.join(cmd))
    print()

    # Change to ArduPilot root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ardupilot_root = os.path.join(script_dir, '..', '..', '..', '..')
    ardupilot_root = os.path.normpath(ardupilot_root)
    os.chdir(ardupilot_root)

    # Run simulation
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nSimulation stopped")

if __name__ == '__main__':
    main()
