# Assignment 2 — Complete Viva Questions and Answers

**Student Name:** Deependu Roy  
**Project:** Multi-ECU Service-Oriented Communication Using SOME/IP

### 1. How many logical ECUs are present in the system?

Four: Vehicle ECU, Instrument Cluster ECU, Climate ECU, and Central Display ECU.

### 2. Which ECUs are Service Providers?

The Vehicle ECU provides `VehicleSpeedService`. The Climate ECU provides `ClimateService`.

### 3. Which ECUs are Service Consumers?

The Instrument Cluster ECU consumes `VehicleSpeedService`. The Central Display ECU consumes both `VehicleSpeedService` and `ClimateService`.

### 4. Can the same ECU be both a Service Provider and Service Consumer?

Yes. An ECU can provide one service and consume another. Its role depends on the particular service relationship.

### 5. What is the purpose of `VehicleSpeedService`?

It provides vehicle-speed and vehicle-state information to consumers, and publishes speed-change and overspeed notifications.

### 6. What is its Service ID?

`0x1234`.

### 7. What is its Instance ID?

`0x5678`.

### 8. What methods does it provide?

`GetSpeed()` with Method ID `0x0001`, and `GetVehicleState()` with Method ID `0x0002`.

### 9. What events does it provide?

`SpeedChanged` with Event ID `0x8001` and `OverspeedWarning` with Event ID `0x8002`.

### 10. What is the purpose of `GetVehicleState()`?

It lets a consumer request whether the simulated vehicle is stopped or moving.

### 11. Why is `GetVehicleState()` a method?

The consumer initiates a request when it needs the current state, and the Vehicle ECU returns a response. That is request-response communication.

### 12. How is vehicle state calculated?

If speed is `0 km/h`, the state is `STOPPED` (value `0`). If speed is greater than `0 km/h`, the state is `MOVING` (value `1`).

### 13. What is the Method ID of `GetVehicleState()`?

`0x0002`.

### 14. What is the purpose of `OverspeedWarning`?

It notifies subscribed consumers that the simulated vehicle has exceeded the configured speed threshold.

### 15. What condition generates `OverspeedWarning`?

The current speed must be strictly greater than `80 km/h`.

### 16. Why is no warning generated at exactly 80 km/h?

The condition is `speed > 80`, not `speed >= 80`. Therefore, 80 km/h does not exceed the threshold.

### 17. What is the Event ID of `OverspeedWarning`?

`0x8002`.

### 18. What is its Event Group ID?

`0x0002`.

### 19. What is the purpose of `ClimateService`?

It provides current cabin-temperature information, accepts target-temperature requests, and publishes cabin-temperature updates.

### 20. What is the Service ID of `ClimateService`?

`0x2234`.

### 21. What does `GetCabinTemperature()` return?

The current simulated cabin temperature as an `int16` represented in tenths of a degree Celsius. For example, `245` means `24.5 °C`.

### 22. Why is cabin temperature represented in tenths of a degree Celsius?

It allows decimal temperatures to be represented precisely using an integer payload, avoiding floating-point encoding. For example, `240` means `24.0 °C` and `245` means `24.5 °C`.

### 23. What does `SetTargetTemperature()` do?

It receives a requested target temperature from a consumer, checks whether it is in the permitted range, updates the target if valid, and returns a status.

### 24. What is the valid target temperature range?

`16.0 °C` to `30.0 °C`, inclusive. In the tenths-of-a-degree payload representation, that is `160` through `300`.

### 25. What happens when an invalid temperature is requested?

The Climate ECU returns status `1` (`INVALID_TEMPERATURE