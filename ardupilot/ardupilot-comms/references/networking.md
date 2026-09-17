# Network Communication

TCP/UDP MAVLink over network interfaces.

## AP_Networking

**Library**: `libraries/AP_Networking/`
**Singleton**: `AP::network()` (when enabled)

### Enabling

Network support requires:
- Board with network hardware (Ethernet, WiFi)
- Build with `HAL_NETWORKING_ENABLED`

### Parameters

| Parameter | Description |
|-----------|-------------|
| `NET_ENABLE` | Enable networking |
| `NET_DHCP` | Enable DHCP client |
| `NET_IPADDR0-3` | Static IP address |
| `NET_NETMASK` | Subnet mask |
| `NET_GATEWAY` | Default gateway |
| `NET_MACADDR0-5` | MAC address |

---

## MAVLink over UDP

### Configuration

```
NET_P1_TYPE = 1       (UDP client)
NET_P1_IP0-3 = x.x.x.x  (Target IP)
NET_P1_PORT = 14550   (Target port)
NET_P1_PROTOCOL = 2   (MAVLink2)
```

### Port Types

| Type | Description |
|------|-------------|
| 0 | Disabled |
| 1 | UDP client (connect to GCS) |
| 2 | UDP server (listen for connections) |
| 3 | TCP server |
| 4 | TCP client |

### Multiple Connections

Up to 4 network ports (NET_P1_ through NET_P4_).

---

## MAVLink over TCP

```
NET_P1_TYPE = 3       (TCP server)
NET_P1_PORT = 5760    (Listen port)
NET_P1_PROTOCOL = 2   (MAVLink2)
```

or

```
NET_P1_TYPE = 4       (TCP client)
NET_P1_IP0-3 = x.x.x.x  (Server IP)
NET_P1_PORT = 5760    (Server port)
```

---

## PPP (Point-to-Point Protocol)

### Use Case

MAVLink over cellular modems or other serial links that need IP layer.

### Configuration

```
SERIALn_PROTOCOL = 48  (PPP)
SERIALn_BAUD = 115200
```

### Network over PPP

Once PPP link is up, network traffic routes over the serial connection.

---

## Registered Ports

Network ports are registered with AP_SerialManager:

```cpp
// From AP_Networking
class NetworkPort : public AP_SerialManager::RegisteredPort {
    // Implements UARTDriver interface
    // Traffic goes over network instead of serial
};

// Registration
AP::serialmanager().register_port(&network_port);
```

---

## Integration with GCS

Network ports appear as regular serial channels to GCS_MAVLink:

```cpp
// GCS setup iterates all ports including network
void GCS::setup_uarts() {
    // ... setup serial ports ...

    // Network ports are found via find_serial() like normal ports
    AP_HAL::UARTDriver *uart = AP::serialmanager().find_serial(
        AP_SerialManager::SerialProtocol_MAVLink, n);

    if (uart != nullptr) {
        create_gcs_mavlink_backend(*uart);
    }
}
```

---

## Web Server

Some boards support a built-in web server for configuration:

### Parameters

| Parameter | Description |
|-----------|-------------|
| `WEB_ENABLE` | Enable web server |
| `WEB_BIND_PORT` | HTTP port (default 80) |

### Features

- Parameter configuration
- File management (logs, scripts)
- Firmware update

---

## Common Network Setups

### Ground Station over WiFi

```
Vehicle (STA mode) → WiFi AP → GCS
NET_P1_TYPE = 1     (UDP client)
NET_P1_IP = GCS IP
NET_P1_PORT = 14550
```

### Vehicle as WiFi AP

```
Vehicle (AP mode) ← GCS connects
NET_P1_TYPE = 2     (UDP server)
NET_P1_PORT = 14550
```

### Companion Computer

```
Vehicle ←Ethernet→ Companion ←WiFi→ GCS
NET_P1_TYPE = 2     (UDP server, companion connects)
NET_P1_PORT = 14550
```

### Cellular Telemetry

```
Vehicle ←PPP→ Modem ←Cellular→ Internet → GCS
SERIALn_PROTOCOL = 48  (PPP to modem)
NET_P1_TYPE = 1        (UDP client to GCS)
```

---

## Debugging

### Status Messages

```cpp
// Network status sent via GCS_SEND_TEXT
GCS_SEND_TEXT(MAV_SEVERITY_INFO, "Network: IP %s", ip_str);
```

### MAVLink Message

SYSTEM_STATUS includes network interface health in `onboard_control_sensors_health`.
