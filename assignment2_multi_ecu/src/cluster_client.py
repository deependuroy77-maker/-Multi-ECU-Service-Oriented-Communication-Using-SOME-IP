"""Instrument Cluster ECU: consumes VehicleSpeedService."""
import asyncio
from .common import *
from . import vehicle_speed_interface as vi

def event_callback(event_id, payload):
    try:
        value = read_u16(payload)
        if event_id == vi.SPEED_CHANGED_EVENT_ID:
            print(f"[Instrument Cluster] SpeedChanged notification: {value} km/h", flush=True)
        elif event_id == vi.OVERSPEED_WARNING_EVENT_ID:
            print(f"\n[Instrument Cluster] *** OVERSPEED WARNING: {value} km/h ***\n", flush=True)
    except Exception as exc:
        print(f"[Instrument Cluster] Event decode error: {exc}", flush=True)

async def main():
    print_banner("ECU 2 — INSTRUMENT CLUSTER ECU")
    daemon = await daemon_connect()
    speed_group = make_event_group(vi.SPEED_EVENTGROUP_ID, [vi.SPEED_CHANGED_EVENT_ID])
    over_group = make_event_group(vi.OVERSPEED_EVENTGROUP_ID, [vi.OVERSPEED_WARNING_EVENT_ID])
    service = make_service(
        vi.SERVICE_ID,
        [make_method(vi.GET_SPEED_METHOD_ID), make_method(vi.GET_VEHICLE_STATE_METHOD_ID)],
        [speed_group, over_group],
    )
    client = client_instance(daemon, service, vi.INSTANCE_ID, 30511)
    client.register_callback(event_callback)
    client.subscribe_eventgroup(speed_group, 5)
    client.subscribe_eventgroup(over_group, 5)
    try:
        last = None
        while True:
            found = await service_is_available(client)
            if found != last:
                print(f"[Instrument Cluster] VehicleSpeedService {'AVAILABLE' if found else 'NOT AVAILABLE'}", flush=True)
                last = found
            if found:
                try:
                    r1 = await call_when_found(client, vi.GET_SPEED_METHOD_ID)
                    r2 = await call_when_found(client, vi.GET_VEHICLE_STATE_METHOD_ID)
                    if r1.payload and r2.payload:
                        spd, state = read_u16(r1.payload), read_u8(r2.payload)
                        print(f"[Instrument Cluster] Vehicle Speed: {spd} km/h | Vehicle State: {'STOPPED' if state == 0 else 'MOVING'}", flush=True)
                except Exception as exc:
                    print(f"[Instrument Cluster] Method call issue: {exc}", flush=True)
            await asyncio.sleep(6)
    finally:
        await daemon.disconnect_from_daemon()

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: print("\n[Instrument Cluster] Stopped by user.")
