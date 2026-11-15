# Multi-ECU Service-Oriented Communication Using SOME/IP

## Assignment 2 – Virtual Vehicle Service Network

**Technology:** Python, SOME/IP, `someipy`, Ubuntu and Wireshark

## 1. Project Overview

This project implements a virtual automotive communication network consisting of four logical Electronic Control Units (ECUs) communicating through the SOME/IP (Scalable service-Oriented Middleware over IP) protocol.

The project extends a basic vehicle-speed service into a multi-ECU architecture. It demonstrates service-oriented communication using request-response methods, publish-subscribe events, service discovery and event-group subscriptions.

The system uses Python and the `someipy` library. Each ECU runs as a separate application, while a SOME/IP daemon manages communication in the local environment.

## 2. System Architecture

The project consists of four logical ECUs:

| ECU | Role | Responsibility |
|---|---|---|
| Vehicle ECU | Service Provider | Provides vehicle speed and vehicle state information |
| Instrument Cluster ECU | Service Consumer | Displays vehicle speed and state information |
| Climate ECU | Service Provider | Provides cabin temperature information and accepts target temperature requests |
| Central Display ECU | Service Consumer | Consumes vehicle and climate services |

### Communication Architecture

```text
             Vehicle ECU
             (Provider)
                  |
          VehicleSpeedService
                  |
          +-------+--------+
          |                |
          v                v
   Instrument Cluster   Central Display
       (Consumer)          (Consumer)
                              |
                              |
                       ClimateService
                              |
                              v
                          Climate ECU
                          (Provider)
```

The Instrument Cluster consumes the VehicleSpeedService, while the Central Display consumes both VehicleSpeedService and ClimateService.

## 3. Implemented SOME/IP Services

### 3.1 VehicleSpeedService

The Vehicle ECU provides the VehicleSpeedService.

| Parameter | Value |
|---|---|
| Service ID | `0x1234` |
| Instance ID | `0x5678` |

**Methods:**

| Method | Method ID | Description |
|---|---|---|
| GetSpeed | `0x0001` | Returns the current vehicle speed |
| GetVehicleState | `0x0002` | Returns the current vehicle state |

**Events:**

| Event | Event ID | Event Group ID | Description |
|---|---|---|---|
| SpeedChanged | `0x8001` | `0x0001` | Publishes vehicle speed updates |
| OverspeedWarning | `0x8002` | `0x0002` | Publishes an overspeed warning |

The overspeed condition is triggered when the vehicle speed exceeds 80 km/h.

### 3.2 ClimateService

The Climate ECU provides the ClimateService.

| Parameter | Value |
|---|---|
| Service ID | `0x2234` |
| Instance ID | `0x0001` |

**Methods:**

| Method | Method ID | Description |
|---|---|---|
| GetCabinTemperature | `0x0001` | Returns the current cabin temperature |
| SetTargetTemperature | `0x0002` | Accepts or rejects a requested target temperature |

The target temperature is accepted within the range of 16°C to 30°C, inclusive.

Temperature values are represented in tenths of a degree Celsius.

**Event:**

| Event | Event ID | Event Group ID | Description |
|---|---|---|---|
| CabinTemperatureChanged | `0x8001` | `0x0001` | Publishes cabin temperature updates |

## 4. Technologies Used

- Python 3
- SOME/IP communication protocol
- `someipy` Python library
- Ubuntu Linux
- VirtualBox (for the virtual machine environment)
- Wireshark
- UDP/IP communication
- SOME/IP Service Discovery

## 5. Project Directory Structure

```text
assignment2_multi_ecu/
│
├── src/
│   ├── vehicle_ecu.py
│   ├── cluster_client.py
│   ├── climate_ecu.py
│   ├── central_display.py
│   └── common.py
│
├── scripts/
│   └── setup_ubuntu.sh
│
├── captures/
│   └── .gitkeep
│
├── evidence/
│   └── Wireshark and terminal screenshots
│
├── someipyd.json
├── requirements.txt
├── README.md
├── REPORT.md
└── VIVA.md
```

The `captures/` directory is intended for saved Wireshark packet captures. Add your `.pcap` or `.pcapng` files to this directory after capturing the traffic.

The `evidence/` directory contains screenshots documenting the application execution and packet analysis.

## 6. Installation and Setup

### Prerequisites

- Ubuntu Linux
- Python 3
- pip
- Wireshark
- Internet connection for installing dependencies

### Step 1: Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Navigate into the project directory:

```bash
cd assignment2_multi_ecu
```

### Step 2: Run the Setup Script

```bash
chmod +x scripts/setup_ubuntu.sh
./scripts/setup_ubuntu.sh
```

The setup script installs the required dependencies and prepares the Python virtual environment.

### Step 3: Activate the Virtual Environment

```bash
source .venv/bin/activate
```

If the virtual environment has not been created, create it manually:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 7. Running the Application

The system uses five terminals:

1. SOME/IP daemon
2. Vehicle ECU
3. Instrument Cluster ECU
4. Climate ECU
5. Central Display ECU

Open five separate Ubuntu terminals and navigate to the project directory in each terminal.

Activate the virtual environment in each terminal:

```bash
source .venv/bin/activate
```

### Terminal 1: Start SOME/IP Daemon

```bash
someipyd --config someipyd.json
```

Keep this terminal running.

### Terminal 2: Start Vehicle ECU

```bash
python src/vehicle_ecu.py
```

The Vehicle ECU offers VehicleSpeedService and publishes vehicle speed and overspeed events.

### Terminal 3: Start Instrument Cluster ECU

```bash
python src/cluster_client.py
```

The Instrument Cluster discovers VehicleSpeedService, subscribes to its events and requests vehicle information.

### Terminal 4: Start Climate ECU

```bash
python src/climate_ecu.py
```

The Climate ECU offers ClimateService and publishes cabin temperature updates.

### Terminal 5: Start Central Display ECU

```bash
python src/central_display.py
```

The Central Display discovers and consumes both VehicleSpeedService and ClimateService.

Keep all application terminals running while observing communication.

## 8. Wireshark Packet Analysis

Wireshark is used to observe SOME/IP communication between the virtual ECUs.

### Step 1: Open Wireshark

Start Wireshark and select the loopback interface:

```text
lo
```

The applications communicate locally using:

```text
127.0.0.1
```

### Step 2: Start Packet Capture

Start capturing packets before or while the ECU applications are running.

### Step 3: Apply the SOME/IP Display Filter

```text
someip
```

To filter VehicleSpeedService traffic:

```text
someip.serviceid == 0x1234
```

To filter ClimateService traffic:

```text
someip.serviceid == 0x2234
```

### Step 4: Inspect SOME/IP Packets

Inspect the decoded packet fields, where available:

- Service ID
- Method ID
- Client ID
- Session ID
- Message Type
- Return Code
- Source and destination addresses
- Source and destination ports
- Payload

The packet captures can be saved in the `captures/` directory.

Suggested filename:

```text
assignment2-multi-ecu.pcapng
```

## 9. Expected Communication Behaviour

The application is designed to demonstrate:

1. Vehicle ECU offering VehicleSpeedService.
2. Instrument Cluster discovering and consuming VehicleSpeedService.
3. Central Display consuming VehicleSpeedService.
4. Climate ECU offering ClimateService.
5. Central Display consuming ClimateService.
6. Method-based request-response communication.
7. Event-based publish-subscribe communication.
8. Event-group subscriptions.
9. Overspeed warning when vehicle speed exceeds 80 km/h.
10. Climate target-temperature validation.
11. Observation of SOME/IP packets using Wireshark.

## 10. Repository Contents

| File or Directory | Purpose |
|---|---|
| `src/` | Python source code for the ECU applications |
| `scripts/` | Environment setup script |
| `someipyd.json` | SOME/IP daemon configuration |
| `requirements.txt` | Python dependencies |
| `captures/` | Location for Wireshark packet captures |
| `evidence/` | Screenshots of application execution and packet analysis |
| `REPORT.md` | Project report and implementation discussion |
| `VIVA.md` | 45 viva questions with answers |

## 11. Troubleshooting

### Python Module Not Found

Activate the virtual environment and install the dependencies:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Wireshark Permission Error

Configure non-superuser capture permissions:

```bash
sudo dpkg-reconfigure wireshark-common
```

Select **Yes** when asked whether non-superusers should be able to capture packets.

Then add your user to the Wireshark group:

```bash
sudo usermod -aG wireshark $USER
```

Log out and log in again, or reboot the Ubuntu virtual machine.

### No SOME/IP Packets Visible

- Confirm that the SOME/IP daemon is running.
- Confirm that all required ECU applications are running.
- Select the loopback interface (`lo`).
- Start a fresh capture.
- Apply the `someip` display filter.

## 12. Learning Outcomes

This project provides practical experience with:

- Multi-ECU automotive communication architecture.
- Service-oriented communication using SOME/IP.
- Service providers and service consumers.
- Service IDs, Instance IDs and Method IDs.
- Request-response communication.
- Publish-subscribe communication.
- Events and event groups.
- SOME/IP Service Discovery.
- Application-level input validation.
- Network packet inspection using Wireshark.

## 13. Conclusion

The project demonstrates a virtual multi-ECU vehicle communication system using Python and SOME/IP. It extends a vehicle-speed service into an architecture containing four logical ECUs and two independent services.

The implementation illustrates how service providers expose functionality and how consumers discover and use services through methods and events.

Wireshark is used to inspect SOME/IP communication on the loopback interface, including traffic associated with VehicleSpeedService (`0x1234`) and ClimateService (`0x2234`).

For detailed implementation information, execution observations and limitations, refer to `REPORT.md`. For oral examination preparation, refer to `VIVA.md`, which contains 45 questions and answers.

---

**Project:** Assignment 2 – Multi-ECU Service-Oriented Communication Using SOME/IP  
**Language:** Python  
**Communication Protocol:** SOME/IP  
**Packet Analysis:** Wireshark
