# Assignment 2 — Multi-ECU Service-Oriented Communication Using SOME/IP

**Student:** Deependu Roy  
**Platform:** Ubuntu Linux in VirtualBox  
**Library:** `someipy` 2.x (tested interactively by me in the supplied screenshots)  
**Transport:** SOME/IP over UDP

## What is included

- `src/vehicle_speed_interface.py` — VehicleSpeedService IDs and interface metadata.
- `src/vehicle_speed_service.py` — Vehicle ECU provider: methods and events.
- `src/cluster_client.py` — Instrument Cluster consumer.
- `src/climate_interface.py` — ClimateService IDs and interface metadata.
- `src/climate_service.py` — Climate ECU provider: methods, validation and event.
- `src/central_display.py` — Central Display consumer of both services.
- `src/common.py` — shared someipy setup, payload helpers and service builders.
- `scripts/` — setup, launch and validation helpers.
- `REPORT.md` — report template. Fill the evidence/results sections only after running the experiments.
- `VIVA.md` — concise viva preparation.
- `captures/` — save the Wireshark `.pcapng` capture here.
- `evidence/` — the 10 screenshots supplied during the working session, copied into the submission.
- `REPORT.md` — report with screenshot evidence references and clearly marked observations.

> This is a standalone Assignment 2 implementation using the Assignment 1 service/instance/method/event identifiers specified in the brief. If your Assignment 1 setup uses a different someipy major version, daemon configuration, or network interface, reconcile that setup before running.

## Requirements

The implementation targets the someipy 2.x API documented at https://someipy.readthedocs.io/en/v2.1.2/ . Use Python 3.10+ if available. The `someipy` package must expose `ServerServiceInstance`, `ClientServiceInstance`, `ServiceBuilder`, `Method`, `Event`, `EventGroup`, `TransportLayerProtocol`, and the `someipy.serialization` payload types.

## Ubuntu VirtualBox setup

1. Configure the VM network. For a single-VM demonstration, use the Ubuntu loopback interface (`lo`) and `127.0.0.1`. This avoids VirtualBox adapter routing issues. For multi-VM communication, use a host-only network and use the VM's host-only IPv4 address instead.
2. Copy/extract this repository into Ubuntu.
3. Open a terminal in the repository folder and run:

```bash
chmod +x scripts/*.sh
./scripts/setup_ubuntu.sh
```

4. Open a terminal for the daemon:

```bash
source .venv/bin/activate
someipyd --config someipyd.json
```

5. Open four more terminals in the repository folder. In each, run `source .venv/bin/activate` first, then launch one ECU:

```bash
python -m src.cluster_client
python -m src.central_display
python -m src.vehicle_speed_service
python -m src.climate_service
```

Start consumers first if demonstrating independent service discovery. Start the Vehicle and Climate providers afterwards.

### Important daemon note

For this single Ubuntu VM, run **one** `someipyd` daemon for the host and connect the four application processes to it. The applications are four logical ECUs represented by four terminals; they are not four separate Linux network namespaces or four physical machines. If the course's Assignment 1 setup requires one daemon per isolated ECU/network namespace, follow that environment's configuration instead.

## Terminal order for the discovery demonstration

1. Terminal 1: `someipyd --config someipyd.json`
2. Terminal 2: `python -m src.cluster_client`
3. Terminal 3: `python -m src.central_display`
4. Terminal 4: `python -m src.vehicle_speed_service`
5. Terminal 5: `python -m src.climate_service`

Expected: the consumers initially report services unavailable, then detect each provider independently when it starts.

## Temperature validation

The Central Display prompts for a target temperature in tenths of °C. Enter:

- `220` → 22.0 °C → ACCEPTED
- `160` → 16.0 °C → ACCEPTED
- `300` → 30.0 °C → ACCEPTED
- `100` → 10.0 °C → INVALID_TEMPERATURE
- `350` → 35.0 °C → INVALID_TEMPERATURE

The range is inclusive: 160–300.

## Vehicle speed / overspeed

The Vehicle ECU cycles through a demonstration sequence that includes 70, 80, 90, 100 and 0 km/h. `SpeedChanged` is sent for each change. `OverspeedWarning` is sent only when speed is strictly greater than 80 km/h.

## Wireshark

For localhost, capture on `lo`. A useful display filter is:

```text
someip || someip_sd
```

If Wireshark does not decode automatically, use **Analyze → Decode As** and select SOME/IP for the UDP traffic as appropriate. Save the capture as `captures/assignment2-multi-ecu.pcapng`.

## Evidence checklist

Capture your own screenshots after running the system:

- [ ] daemon running
- [ ] Instrument Cluster showing both vehicle methods and event reception
- [ ] Central Display showing both services available
- [ ] both consumers receiving SpeedChanged
- [ ] both consumers receiving OverspeedWarning at >80 km/h
- [ ] Climate valid and invalid temperature responses
- [ ] Climate ECU stopped while Vehicle service continues
- [ ] Climate ECU restarted and rediscovered
- [ ] Vehicle ECU stopped while Climate service continues
- [ ] Vehicle ECU restarted and rediscovered
- [ ] Wireshark showing SD, method request/response and event traffic

Do not submit expected output as if it were observed output. Record the actual behaviour and attach actual screenshots.

## Troubleshooting

- `Connection refused` to daemon: start `someipyd` first; check the daemon log and configured UDS/TCP mode.
- `is_available()` remains false: check that the provider is running, all apps use the same interface/IP, and the SD multicast address is joined on the selected interface. The shared helper also supports older builds exposing `service_found()`.
- No events: verify the consumer subscribed to the correct **event group ID**, not the event ID. Subscription TTL must be an integer (the project uses `5`, not `5.0`).
- `ModuleNotFoundError`: activate `.venv` and rerun `pip install -r requirements.txt`.
- Port/interface conflict: ensure each service instance has a unique UDP endpoint port.


## Current package update

The client discovery checks use the asynchronous `ClientServiceInstance.is_available()` API used by the someipy 2.x client. A compatibility fallback to `service_found()` is retained for older releases. Event subscription TTLs are integers (`5`) to avoid the `ttl_subscription_seconds must be an integer value` exception encountered during setup.

## Screenshot evidence

See [`evidence/README.md`](evidence/README.md) for the evidence index. The screenshots establish that the Vehicle ECU and Instrument Cluster ran, and that Wireshark decoded SOME/IP traffic for both service IDs. They do not include a saved raw `.pcapng` capture; save one from Wireshark separately before submission.
