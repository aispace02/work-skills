#!/usr/bin/env python3
"""
Visualize the control hierarchy for an ArduPilot vehicle.

Shows how control libraries connect from navigation down to motors.

Usage:
    python control_hierarchy.py copter
    python control_hierarchy.py plane
    python control_hierarchy.py rover
"""

import sys


COPTER_HIERARCHY = """
┌─────────────────────────────────────────────────────────────────────┐
│                    ARDUPILOT COPTER CONTROL HIERARCHY               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Navigation Layer                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │   │
│  │  │  AC_WPNav    │  │  AC_Loiter   │  │  AC_Circle   │       │   │
│  │  │  Waypoint    │  │  Position    │  │  Circle      │       │   │
│  │  │  navigation  │  │  hold        │  │  navigation  │       │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │   │
│  │         │                 │                 │                │   │
│  └─────────┼─────────────────┼─────────────────┼────────────────┘   │
│            │                 │                 │                    │
│            └─────────────────┼─────────────────┘                    │
│                              ▼ position/velocity targets            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Position Layer                            │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │                   AC_PosControl                       │   │   │
│  │  │  - Horizontal (NE) position/velocity control          │   │   │
│  │  │  - Vertical (D) position/velocity control             │   │   │
│  │  │  - Outputs: roll_rad, pitch_rad, throttle             │   │   │
│  │  └────────────────────────┬─────────────────────────────┘   │   │
│  └───────────────────────────┼──────────────────────────────────┘   │
│                              ▼ roll/pitch angles                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Attitude Layer                            │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │              AC_AttitudeControl_Multi                 │   │   │
│  │  │  - Angle controller (P): angle error → rate           │   │   │
│  │  │  - attitude_controller_run_quat()                     │   │   │
│  │  │  - Outputs: roll/pitch/yaw rate targets               │   │   │
│  │  └────────────────────────┬─────────────────────────────┘   │   │
│  └───────────────────────────┼──────────────────────────────────┘   │
│                              ▼ angular rate targets                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Rate Layer                                │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │              AC_AttitudeControl::rate_controller_run  │   │   │
│  │  │  - Rate PID: rate error → motor commands              │   │   │
│  │  │  - Uses AC_PID for roll/pitch/yaw rates               │   │   │
│  │  │  - Runs at highest frequency (400 Hz)                 │   │   │
│  │  │  - Outputs: roll_out, pitch_out, yaw_out              │   │   │
│  │  └────────────────────────┬─────────────────────────────┘   │   │
│  └───────────────────────────┼──────────────────────────────────┘   │
│                              ▼ motor commands                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Motor Layer                               │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │                    AP_Motors                          │   │   │
│  │  │  - Motor mixing matrix                                │   │   │
│  │  │  - Throttle limiting                                  │   │   │
│  │  │  - PWM output via SRV_Channels                        │   │   │
│  │  └──────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  Key Parameters:                                                    │
│  - ATC_*: Attitude control (angle/rate gains)                      │
│  - PSC_*: Position control (pos/vel gains)                         │
│  - WPNAV_*: Waypoint navigation speeds/accels                      │
│  - LOITER_*: Loiter mode settings                                  │
└─────────────────────────────────────────────────────────────────────┘
"""

PLANE_HIERARCHY = """
┌─────────────────────────────────────────────────────────────────────┐
│                    ARDUPILOT PLANE CONTROL HIERARCHY                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Navigation Layer                          │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │                   AP_L1_Control                       │   │   │
│  │  │  - L1 guidance algorithm for path following           │   │   │
│  │  │  - Waypoint tracking and loiter                       │   │   │
│  │  │  - Outputs: nav_roll_cd, lateral_acceleration         │   │   │
│  │  └────────────────────────┬─────────────────────────────┘   │   │
│  └───────────────────────────┼──────────────────────────────────┘   │
│                              │                                      │
│            ┌─────────────────┴─────────────────┐                    │
│            ▼ nav_roll                          ▼ altitude/airspeed  │
│  ┌─────────────────────┐        ┌───────────────────────────────┐  │
│  │  Lateral Control    │        │      Longitudinal Control      │  │
│  │  ┌───────────────┐  │        │  ┌─────────────────────────┐  │  │
│  │  │AP_RollControl │  │        │  │        AP_TECS          │  │  │
│  │  │ - Roll rate   │  │        │  │ Total Energy Control    │  │  │
│  │  │   PID         │  │        │  │ - Altitude control      │  │  │
│  │  │ - Output:     │  │        │  │ - Airspeed control      │  │  │
│  │  │   aileron     │  │        │  │ - Outputs: throttle,    │  │  │
│  │  └───────┬───────┘  │        │  │   pitch_demand          │  │  │
│  │          │          │        │  └───────────┬─────────────┘  │  │
│  │  ┌───────▼───────┐  │        │              │                │  │
│  │  │AP_YawControl  │  │        │  ┌───────────▼─────────────┐  │  │
│  │  │ - Coordinated │  │        │  │    AP_PitchController   │  │  │
│  │  │   turns       │  │        │  │    - Pitch rate PID     │  │  │
│  │  │ - Rudder      │  │        │  │    - Output: elevator   │  │  │
│  │  │   output      │  │        │  └───────────┬─────────────┘  │  │
│  │  └───────┬───────┘  │        │              │                │  │
│  └──────────┼──────────┘        └──────────────┼────────────────┘  │
│             │                                  │                    │
│             └──────────────┬───────────────────┘                    │
│                            ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Servo Output Layer                        │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │                   SRV_Channels                        │   │   │
│  │  │  - Aileron, Elevator, Rudder, Throttle               │   │   │
│  │  │  - Flaps, Spoilers, etc.                             │   │   │
│  │  └──────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  Key Parameters:                                                    │
│  - NAVL1_*: L1 navigation (period, damping)                        │
│  - TECS_*: Total energy control (climb/sink rates)                 │
│  - RLL_RATE_*: Roll rate PID                                       │
│  - PTCH_RATE_*: Pitch rate PID                                     │
│  - YAW_RATE_*: Yaw rate PID                                        │
└─────────────────────────────────────────────────────────────────────┘
"""

ROVER_HIERARCHY = """
┌─────────────────────────────────────────────────────────────────────┐
│                    ARDUPILOT ROVER CONTROL HIERARCHY                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Navigation Layer                          │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │                   AR_WPNav                            │   │   │
│  │  │  - Waypoint navigation                                │   │   │
│  │  │  - Path following                                     │   │   │
│  │  │  - Outputs: heading target, speed target              │   │   │
│  │  └────────────────────────┬─────────────────────────────┘   │   │
│  └───────────────────────────┼──────────────────────────────────┘   │
│                              │                                      │
│            ┌─────────────────┴─────────────────┐                    │
│            ▼ heading                           ▼ speed              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Attitude Control Layer                    │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │               AR_AttitudeControl                      │   │   │
│  │  │                                                       │   │   │
│  │  │  Steering Control:                                    │   │   │
│  │  │  - get_steering_out_heading() → steering angle        │   │   │
│  │  │  - get_steering_out_rate() → turn rate control        │   │   │
│  │  │  - get_steering_out_lat_accel() → lateral accel       │   │   │
│  │  │                                                       │   │   │
│  │  │  Speed Control:                                       │   │   │
│  │  │  - get_throttle_out_speed() → maintain speed          │   │   │
│  │  │  - get_throttle_out_stop() → controlled stop          │   │   │
│  │  │                                                       │   │   │
│  │  │  Special Modes:                                       │   │   │
│  │  │  - BalanceBot: get_throttle_out_from_pitch()         │   │   │
│  │  │  - Sailboat: get_sail_out_from_heel()                │   │   │
│  │  └────────────────────────┬─────────────────────────────┘   │   │
│  └───────────────────────────┼──────────────────────────────────┘   │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Motor Output Layer                        │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │                   AR_Motors                           │   │   │
│  │  │  - Differential steering (skid steer)                 │   │   │
│  │  │  - Ackermann steering                                 │   │   │
│  │  │  - Omni-directional                                   │   │   │
│  │  │  - PWM output via SRV_Channels                        │   │   │
│  │  └──────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  Key Parameters:                                                    │
│  - ATC_STR_*: Steering PID gains                                   │
│  - ATC_SPEED_*: Speed control PID                                  │
│  - ATC_ACCEL_MAX: Max acceleration                                 │
│  - ATC_DECEL_MAX: Max deceleration                                 │
│  - ATC_TURN_MAX_G: Max lateral acceleration                        │
│  - CRUISE_SPEED: Cruise speed                                      │
│  - CRUISE_THROTTLE: Cruise throttle                                │
└─────────────────────────────────────────────────────────────────────┘
"""


def main():
    if len(sys.argv) < 2:
        print("Usage: python control_hierarchy.py <vehicle>")
        print("\nVehicles: copter, plane, rover")
        sys.exit(1)

    vehicle = sys.argv[1].lower()

    if vehicle in ["copter", "multicopter", "quad", "arducopter"]:
        print(COPTER_HIERARCHY)
    elif vehicle in ["plane", "fixed-wing", "fixedwing", "arduplane"]:
        print(PLANE_HIERARCHY)
    elif vehicle in ["rover", "ground", "car", "boat"]:
        print(ROVER_HIERARCHY)
    else:
        print(f"Unknown vehicle type: {vehicle}")
        print("Supported: copter, plane, rover")
        sys.exit(1)


if __name__ == "__main__":
    main()
