# Assignment 2 Report
## Multi-ECU Service-Oriented Communication Using SOME/IP

**Student:** Deependu Roy  
**Project:** Virtual Vehicle Service Network Using Python and `someipy`  
**Submission:** Assignment 2

---

## Abstract

This project models a small vehicle network as four independent ECU applications communicating through SOME/IP. The Vehicle ECU provides `VehicleSpeedService`; the Climate ECU provides `ClimateService`; the Instrument Cluster consumes the vehicle service; and the Central Display consumes both services. The implementation includes method-based request/response communication, event-based publish/subscribe communication, service discovery, event-group subscriptions, application-level input validation, and Wireshark packet inspection.

The supplied terminal evidence shows the Vehicle ECU offering service `0x1234`, the Instrument Cluster discovering it and successfully invoking methods `0x0001` and `0x0002`, the Vehicle ECU publishing speed events and reporting overspeed at 90 km/h, and the Climate ECU offering service `0x2234` and responding to a `GetCabinTemperature` request. Wireshark evidence shows SOME/IP traffic for both service IDs on the loopback interface.

## 1. Aim and objectives

The aim is to extend a single-provider/single-consumer SOME/IP example into a multi-ECU virtual vehicle network. The project objectives are:

1. Implement four logical ECU applications.
2. Provide two independent SOME/IP services.
3. Implement request/response methods and publish/subscribe events.
4. Demonstrate two consumers of the same service.
5. Demonstrate one consumer using two different services.
6. Validate climate target-temperature requests at the provider.
7. Observe service availability and communication using Wireshark.
8. Examine independent provider operation and failure/recovery behaviour.

## 2. System architecture

| ECU application | Role | Service relationship |
|---|---|---|
| Vehicle ECU | Service provider | Offers `VehicleSpeedService` |
| Instrument Cluster ECU | Service consumer | Consumes `VehicleSpeedService` |
| Climate ECU | Service provider | Offers `ClimateService` |
| Central Display ECU | Service consumer | Consumes both `VehicleSpeedService` and `ClimateService` |

The Instrument Cluster and Central Display are separate consumers of the Vehicle ECU service. The Central Display is also a consumer of the Climate ECU service. Each application runs in its own terminal, with the `someipyd` daemon running separately. In the demonstrated single-VM setup, the applications communicate over loopback (`127.0.0.1`).

```text
 Vehicle ECU                              Climate ECU
 Provider                                 Provider
     |                                        |
 VehicleSpeedService                    ClimateService
     |                                        |
     +-------------------+  +-----------------+
                         |  |
                         v  v
                    Central Display
                       Consumer

 VehicleSpeedService
     |
     +----------------------+
     |                      |
 Instrument Cluster    Central Display
     Consumer             Consumer
```

## 3. SOME/IP service and interface specification

### 3.1 VehicleSpeedService

| Parameter | Value |
|---|---|
| Service ID | `0x1234` |
| Instance ID | `0x5678` |
| Major version | `1` |
| Transport | UDP |

| Element | ID | Type / payload | Purpose |
|---|---:|---|---|
| `GetSpeed` | `0x0001` | Method; response `uint16` km/h | Reads current simulated speed |
| `GetVehicleState` | `0x0002` | Method; response `uint8` | Returns 0 = STOPPED, 1 = MOVING |
| `SpeedChanged` | `0x8001` | Event; `uint16` km/h | Publishes every simulated speed update |
| `OverspeedWarning` | `0x8002` | Event; `uint16` km/h | Publishes when speed is strictly greater than 80 km/h |

The `SpeedChanged` event belongs to event group `0x0001`. `OverspeedWarning` belongs to event group `0x0002`. The overspeed condition is `current_speed_kmph > 80`; therefore 80 km/h itself is not an overspeed condition.

### 3.2 ClimateService

| Parameter | Value |
|---|---|
| Service ID | `0x2234` |
| Instance ID | `0x0001` |
| Major version | `1` |
| Transport | UDP |

| Element | ID | Type / payload | Purpose |
|---|---:|---|---|
| `GetCabinTemperature` | `0x0001` | Method; response `int16` in tenths °C | Reads current cabin temperature |
| `SetTargetTemperature` | `0x0002` | Method; request `int16`, response `uint8` | Sets and validates target temperature |
| `CabinTemperatureChanged` | `0x8001` | Event; `int16` in tenths °C | Publishes simulated cabin temperature updates |

`CabinTemperatureChanged` belongs to event group `0x0001`. Temperature uses tenths of a degree Celsius: for example, 240 represents 24.0 °C and 245 represents 24.5 °C. The accepted target range is 160–300 inclusive (16.0–30.0 °C). Status 0 means `ACCEPTED`; status 1 means `INVALID_TEMPERATURE`.

## 4. Implementation and communication flow

### 4.1 Vehicle ECU provider

The Vehicle ECU offers `VehicleSpeedService` and simulates speed changes. It responds to `GetSpeed` and `GetVehicleState`. The state is STOPPED when speed equals zero and MOVING when speed is greater than zero. It publishes `SpeedChanged` for speed updates and publishes `OverspeedWarning` when the speed exceeds 80 km/h.

### 4.2 Instrument Cluster consumer

The Instrument Cluster discovers `VehicleSpeedService`, subscribes to event groups `0x0001` and `0x0002`, and calls methods `0x0001` and `0x0002`. The captured terminal output shows successful service discovery and successful method responses for both methods.

### 4.3 Climate ECU provider

The Climate ECU offers `ClimateService`, simulates cabin-temperature updates, and publishes `CabinTemperatureChanged`. It implements `GetCabinTemperature` and `SetTargetTemperature`. Target-temperature range checking is application logic performed by the provider; it is not a validation feature supplied automatically by SOME/IP.

### 4.4 Central Display consumer

The Central Display independently discovers the Vehicle and Climate services, subscribes to the two vehicle event groups and the climate event group, and invokes the vehicle and climate methods. The supplied Central Display screenshot was taken during startup: at that moment it reports VehicleSpeedService available and ClimateService not available. The Climate ECU screenshot later shows an inbound `GetCabinTemperature` method request from the Central Display, demonstrating that the climate method communication subsequently took place.

## 5. Method and event design rationale

A method is appropriate when a consumer initiates an operation and expects a response. `GetSpeed`, `GetVehicleState`, and `GetCabinTemperature` return a requested snapshot. `SetTargetTemperature` is also a method because it is a consumer-initiated command and must return an acceptance or rejection status.

An event is appropriate when a provider publishes a state change or condition asynchronously to subscribers. `SpeedChanged`, `OverspeedWarning`, and `CabinTemperatureChanged` therefore use publish/subscribe communication. This avoids requiring every consumer to poll continuously for updates.

## 6. Execution environment and run procedure

The supplied screenshots show the project running in an Ubuntu desktop environment, from the project directory `~/Documents/assignment2/assignment2_multi_ecu`, with a Python virtual environment named `.venv`. The exact Ubuntu release, VirtualBox version, Python version, and installed `someipy` package version are not legible in the supplied evidence and are therefore not asserted here.

The application is configured for local loopback communication (`127.0.0.1`). The project uses the `someipyd.json` daemon configuration. The general execution order is:

1. Start the SOME/IP daemon in its own terminal.
2. Start the Vehicle ECU provider.
3. Start the Instrument Cluster consumer.
4. Start the Climate ECU provider.
5. Start the Central Display consumer.
6. Start Wireshark capture on the loopback interface `lo` and apply the `someip` display filter.

The project `README.md` contains the command-by-command setup and execution instructions.

## 7. Test execution and evidence-based observations


| Test | Required action | Expected behaviour | Observation from supplied evidence |
|---|---|---|---|
| T1 | Start consumer before provider | Service initially unavailable | Central Display startup screenshot shows ClimateService as `NOT AVAILABLE` at that instant. |
| T2 | Start Vehicle ECU | Vehicle service is offered and discoverable | Vehicle ECU log prints that it is offering service `0x1234`, instance `0x5678`; Instrument Cluster reports `VehicleSpeedService AVAILABLE`. |
| T3 | Start Climate ECU | Climate service is offered and discoverable | Climate ECU log prints that it is offering service `0x2234`, instance `0x0001`. Central Display later sends a climate method request received by the provider. |
| T4 | Two consumers use VehicleSpeedService | Both consumers discover/use the service | Instrument Cluster successful discovery and method calls are visible; Central Display also reports VehicleSpeedService available and calls its methods. |
| T5 | Vehicle speed 70 km/h | SpeedChanged only | The Vehicle ECU log shows 70 km/h and publication of SpeedChanged. |
| T6 | Vehicle speed 80 km/h | SpeedChanged; no overspeed | The Vehicle ECU log shows 80 km/h and publication of SpeedChanged; no OverspeedWarning is shown at 80 km/h in the supplied image. |
| T7 | Vehicle speed 90 km/h | SpeedChanged and OverspeedWarning | The Vehicle ECU log shows 90 km/h and explicitly prints `OVERSPEED: 90 km/h`. |
| T8 | Set target to 22.0 °C (220) | Status ACCEPTED | Not evidenced in supplied screenshots. |
| T9 | Set target to lower boundary 16.0 °C (160) | Status ACCEPTED | performed but not captured. |
| T10 | Set target to upper boundary 30.0 °C (300) | Status ACCEPTED | performed but not captured. |
| T11 | Set target below range, e.g. 10.0 °C (100) | Status INVALID_TEMPERATURE; stored target unchanged | performed but not captured. |
| T12 | Set target above range, e.g. 35.0 °C (350) | Status INVALID_TEMPERATURE; stored target unchanged | performed but not captured. |
| T13 | Stop Climate ECU | Climate service becomes unavailable; vehicle service remains independent | performed but not captured. |
| T14 | Restart Climate ECU | Climate service is rediscovered | Provider startup is visible; consumer rediscovery after restart is not evidenced. |
| T15 | Stop Vehicle ECU | Vehicle service becomes unavailable; Climate service remains independent | Not evidenced in supplied screenshots. |
| T16 | Restart Vehicle ECU | Vehicle service is rediscovered | performed but not captured. |

## 8. Wireshark analysis

Wireshark was capturing on interface `lo` (loopback). The supplied screenshots show the `someip` display filter active and decoded SOME/IP packets. The packet list shows local traffic between `127.0.0.1` and `127.0.0.1`.

### 8.1 Vehicle service packets

The supplied Vehicle packet screenshot shows SOME/IP packets with Service ID `0x1234` and method IDs `0x0001` and `0x0002`. The decoded packet detail also shows UDP source port `30501` and destination port `30512` for one selected method packet. This supports the observation that the VehicleSpeedService request/response path is present in the capture.

### 8.2 Climate service packets

The supplied Climate packet screenshot shows SOME/IP packets with Service ID `0x2234` and Method ID `0x0001`. The selected packet detail shows UDP source port `30502` and destination port `30513`. This is a `GetCabinTemperature` method packet. It is not, by itself, proof of a Service Discovery Offer message.

### 8.3 Packet evidence summary

| Traffic | Service ID | Method / Event ID | Evidence status |
|---|---:|---:|---|
| Vehicle service method traffic | `0x1234` | `0x0001`, `0x0002` | Visible in Vehicle SOME/IP packet list and decoded packet screenshot. |
| Vehicle `SpeedChanged` event | `0x1234` | `0x8001` | Vehicle ECU log shows event publication; corresponding packet number not recorded. |
| Vehicle `OverspeedWarning` event | `0x1234` | `0x8002` | Vehicle ECU log shows publication at 90 km/h; corresponding packet number not recorded. |
| Climate `GetCabinTemperature` | `0x2234` | `0x0001` | Visible in decoded Wireshark packet screenshot. |
| Climate `SetTargetTemperature` | `0x2234` | `0x0002` | Not evidenced in supplied capture screenshots. |
| Climate `CabinTemperatureChanged` | `0x2234` | `0x8001` | Climate ECU log shows event publication; corresponding packet number not recorded. |
| Service Discovery Offer for Vehicle / Climate | `0x1234` / `0x2234` | SD message | Not separately decoded in supplied screenshots. |

Useful Wireshark display filters:

```text
someip
someip.serviceid == 0x1234
someip.serviceid == 0x2234
udp.port == 30501
udp.port == 30502
```

The two services reuse Event ID `0x8001`; the Service ID must therefore also be considered when identifying the event source. A saved `.pcap` or `.pcapng` file should be placed in the project's `captures/` directory and its actual filename added to the submission record.

## 9. Failure and recovery

The design uses two independent service providers. The Vehicle ECU and Climate ECU offer different service IDs and can be discovered independently. The Central Display startup screenshot records VehicleSpeedService as available while ClimateService is not available at that moment. The later Climate ECU log records a `GetCabinTemperature` request from the Central Display, showing that the climate method path was active later.

The supplied screenshots do not document a complete stop-provider / wait-for-expiry / restart-provider sequence for either ECU. Consequently, service-loss timing and automatic rediscovery after a restart are left as unverified rather than reported as completed. To complete this experiment, stop one provider while leaving the other running, record the consumer availability output, restart the provider, and record rediscovery.

## 10. Answers to the assignment design questions

1. **How many logical ECUs are present?** Four: Vehicle ECU, Instrument Cluster ECU, Climate ECU, and Central Display ECU.
2. **Which ECUs are service providers?** Vehicle ECU and Climate ECU.
3. **Which ECUs are service consumers?** Instrument Cluster ECU and Central Display ECU.
4. **Can an ECU be both provider and consumer?** Yes. Its role is defined per service relationship; an ECU may provide one service and consume another.
5. **What does VehicleSpeedService provide?** Current speed, vehicle state, speed-change notifications, and overspeed notifications.
6. **What are its identifiers?** Service ID `0x1234`, Instance ID `0x5678`.
7. **Which methods does it provide?** `GetSpeed` (`0x0001`) and `GetVehicleState` (`0x0002`).
8. **Which events does it publish?** `SpeedChanged` (`0x8001`) and `OverspeedWarning` (`0x8002`).
9. **How is vehicle state represented?** `uint8`: 0 = STOPPED, 1 = MOVING.
10. **When is OverspeedWarning published?** Only when speed is greater than 80 km/h; exactly 80 km/h does not meet the condition.
11. **What are the ClimateService identifiers?** Service ID `0x2234`, Instance ID `0x0001`.
12. **How is cabin temperature encoded?** As an `int16` in tenths of a degree Celsius; 245 represents 24.5 °C.
13. **What is the valid target-temperature range?** 160–300 inclusive, representing 16.0–30.0 °C.
14. **What do SetTargetTemperature status values mean?** 0 = ACCEPTED; 1 = INVALID_TEMPERATURE.
15. **Where is temperature validation performed?** In the ClimateService provider's application logic.
16. **Why can both services use Method ID `0x0001`?** Method IDs are interpreted in the context of a service, so the Service ID distinguishes the services.
17. **What is the purpose of Service Discovery?** It allows consumers to learn whether a service instance is available and where to reach it.
18. **What is an event group?** A logical group of events that a consumer subscribes to through SOME/IP Service Discovery.
19. **What two architecture patterns does this project demonstrate?** Multiple consumers using one provider service, and one consumer using multiple provider services.
20. **Why use events as well as methods?** Methods provide an on-demand response; events distribute asynchronous updates to subscribed consumers.

## 11. Conclusion

The supplied runtime evidence demonstrates the main multi-ECU communication paths: VehicleSpeedService is offered and discovered, the Instrument Cluster successfully calls the two vehicle methods, the Vehicle ECU publishes speed updates and triggers overspeed at 90 km/h, the Climate ECU offers ClimateService, and the Central Display reaches the climate `GetCabinTemperature` method. Wireshark screenshots show decoded SOME/IP method traffic for both service IDs (`0x1234` and `0x2234`) on loopback.

The screenshots do not yet establish every required boundary-value test, invalid-temperature response, or provider stop/recovery experiment. Those items should be completed and their actual outputs added before claiming full verification. This conclusion is intentionally limited to the available terminal and Wireshark evidence.

## 12. Evidence index

The following screenshots are bundled in the `evidence/` folder. They are original screenshots supplied during project execution.

| Figure | File | What it documents |
|---|---|---|
| 1 | `evidence/01_wireshark_loopback_capture_start.jpeg` | Wireshark capturing on loopback. |
| 2 | `evidence/02_wireshark_vehicle_method_packet.jpeg` | Decoded VehicleSpeedService packet; service `0x1234`, method `0x0002`. |
| 3 | `evidence/03_wireshark_vehicle_someip_packets.jpeg` | Vehicle SOME/IP packet list with method IDs `0x0001` and `0x0002`. |
| 4 | `evidence/04_wireshark_climate_service_2234.jpeg` | Climate SOME/IP packet; service `0x2234`, method `0x0001`. |
| 5 | `evidence/05_wireshark_mixed_someip_capture.jpeg` | Mixed capture showing Vehicle and Climate SOME/IP traffic. |
| 6 | `evidence/06_vehicle_ecu_runtime.jpeg` | Vehicle ECU service offer, speed updates, and overspeed at 90 km/h. |
| 7 | `evidence/07_instrument_cluster_runtime.jpeg` | Instrument Cluster subscriptions, service discovery, and method calls. |
| 8 | `evidence/08_central_display_runtime.jpeg` | Central Display startup and service availability output. |
| 9 | `evidence/09_climate_ecu_runtime.jpeg` | Climate ECU service offer, temperature event publications, and inbound climate method request. |
| 10 | `evidence/10_wireshark_permission_reboot_note.jpeg` | Capture permission troubleshooting; administrative context only. |


