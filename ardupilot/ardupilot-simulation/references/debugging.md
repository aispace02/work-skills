# Debugging SITL

## GDB Debugging

### Start with GDB

```bash
sim_vehicle.py -v ArduCopter -G --console --map
```

GDB starts and automatically runs the program.

### GDB Stopped at Start

```bash
sim_vehicle.py -v ArduCopter -g --console --map
```

Stops before running - useful for setting breakpoints.

### Setting Breakpoints

```bash
# Via command line
sim_vehicle.py -v ArduCopter -g -B "AP_Arming::arm" --console --map

# Multiple breakpoints
sim_vehicle.py -v ArduCopter -g \
    -B "AP_Arming::arm" \
    -B "Copter::init_ardupilot" \
    --console --map
```

### GDB Commands

Once in GDB:

```gdb
# Continue execution
c

# Set breakpoint
b AP_Arming::arm
b mode.cpp:123

# Step through code
n          # next line
s          # step into
finish     # finish function

# Print variables
p variable_name
p *pointer
p this->member

# Backtrace
bt

# List code
l

# Quit
q
```

### Debug Build

For better debugging:

```bash
sim_vehicle.py -v ArduCopter -D -G --console --map
```

The `-D` flag enables debug symbols.

## LLDB Debugging (macOS)

```bash
sim_vehicle.py -v ArduCopter --lldb --console --map

# Stopped at start
sim_vehicle.py -v ArduCopter --lldb-stopped --console --map
```

## Valgrind Memory Checking

### Basic Valgrind

```bash
sim_vehicle.py -v ArduCopter -V --console --map
```

Detects:
- Memory leaks
- Use of uninitialized memory
- Invalid memory access

**Note:** Very slow (10-50x slower)

### Callgrind Profiling

```bash
sim_vehicle.py -v ArduCopter --callgrind --console --map
```

Generates profiling data for performance analysis.

View with KCachegrind:
```bash
kcachegrind callgrind.out.*
```

## Strace System Call Tracing

```bash
sim_vehicle.py -v ArduCopter --strace --console --map
```

Creates `arducopter.strace` with system calls.

## Sanitizers

### Undefined Behavior Sanitizer

```bash
sim_vehicle.py -v ArduCopter --ubsan --console --map
```

### UBSan with Abort

```bash
sim_vehicle.py -v ArduCopter --ubsan-abort --console --map
```

Aborts on first undefined behavior for debugging.

## Code Coverage

```bash
sim_vehicle.py -v ArduCopter --coverage --console --map
```

Generates `.gcda` files for coverage analysis.

View with gcov/lcov:
```bash
lcov --capture --directory . --output-file coverage.info
genhtml coverage.info --output-directory coverage_report
```

## Logging and Analysis

### DataFlash Logs

Logs stored in:
- `logs/` directory
- Or specified by `--aircraft NAME`

View with:
```bash
# MAVExplorer
mavlogdump.py --format json logs/*.BIN

# Mission Planner DataFlash Log Browser
```

### MAVLink Telemetry Logs

`mav.tlog` in working directory.

```bash
# Analyze
mavlogdump.py mav.tlog
```

### Console Logging

```bash
# More verbose
sim_vehicle.py -v ArduCopter --moddebug 3 --console --map
```

## Parameter Debugging

### Fresh Parameters

```bash
sim_vehicle.py -v ArduCopter --fresh-params --console --map
```

Builds parameter documentation locally.

### Wipe and Reset

```bash
sim_vehicle.py -v ArduCopter -w --console --map
```

Clears `eeprom.bin` and reloads defaults.

## Common Debug Scenarios

### Crash Investigation

1. Run with GDB:
```bash
sim_vehicle.py -v ArduCopter -G --console --map
```

2. When crash occurs, get backtrace:
```gdb
bt
```

3. Examine variables:
```gdb
info locals
p *this
```

### Performance Issue

1. Run with Callgrind:
```bash
sim_vehicle.py -v ArduCopter --callgrind --console --map
```

2. Analyze with KCachegrind

### Memory Leak

1. Run with Valgrind:
```bash
sim_vehicle.py -v ArduCopter -V --console --map
```

2. Review leak report at exit

### Assertion Failure

1. Run with GDB stopped:
```bash
sim_vehicle.py -v ArduCopter -g --console --map
```

2. Set breakpoint on assert:
```gdb
b __assert_fail
c
```

3. When triggered, get backtrace:
```gdb
bt
```

## Testing

### Autotest Framework

Run automated tests:

```bash
cd Tools/autotest
python autotest.py --list        # List tests
python autotest.py build.Copter  # Build test
python autotest.py fly.Copter    # Fly tests
```

### Running Specific Tests

```bash
# Single test
python autotest.py test.Copter.STABILIZE

# Test with GDB
python autotest.py test.Copter.STABILIZE --gdb
```

### Test Development

Tests in `Tools/autotest/`:
- `arducopter.py` - Copter tests
- `arduplane.py` - Plane tests
- `rover.py` - Rover tests
- `ardusub.py` - Sub tests

## Remote Debugging

### GDB Server

On target:
```bash
gdbserver :1234 ./arducopter --model quad
```

On host:
```bash
gdb ./arducopter
(gdb) target remote target_ip:1234
```

## IDE Integration

### VS Code

`.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "SITL Debug",
            "type": "cppdbg",
            "request": "launch",
            "program": "${workspaceFolder}/build/sitl/bin/arducopter",
            "args": ["--model", "quad", "--speedup", "1"],
            "stopAtEntry": false,
            "cwd": "${workspaceFolder}/ArduCopter",
            "environment": [],
            "MIMode": "gdb"
        }
    ]
}
```

### CLion

Configure with:
- Executable: `build/sitl/bin/arducopter`
- Arguments: `--model quad --speedup 1`
- Working directory: `ArduCopter/`
