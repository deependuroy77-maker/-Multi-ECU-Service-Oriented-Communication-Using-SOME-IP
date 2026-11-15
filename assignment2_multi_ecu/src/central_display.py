"""Central Display ECU: consumes VehicleSpeedService and ClimateService."""
import asyncio
from .common import *
from . import vehicle_speed_interface as vi
from . import climate_interface as ci

def vehicle_callback(event_id, payload):
    try:
        val = read_u16(payload)
        if event_id == vi.SPEED_CHANGED_EVENT_ID:
            print(f"[Central Display] Vehicle Speed Updated: {val} km/h", flush=True)
        elif event_id == vi.OVERSPEED_WARNING_EVENT_ID:
            print(f"\n[Central Display] *** OVERSPEED WARNING: {val} km/h ***\n", flush=True)
    except Exception as exc: print(f"[Central Display] Vehicle event decode error: {exc}", flush=True)

def climate_callback(event_id, payload):
    try:
        if event_id == ci.CABIN_TEMPERATURE_CHANGED_EVENT_ID:
            print(f"[Central Display] Cabin Temperature Updated: {read_i16(payload)/10:.1f} °C", flush=True)
    except Exception as exc: print(f"[Central Display] Climate event decode error: {exc}", flush=True)

async def main():
    print_banner("ECU 4 — CENTRAL VEHICLE DISPLAY")
    daemon = await daemon_connect()

    vg1 = make_event_group(vi.SPEED_EVENTGROUP_ID, [vi.SPEED_CHANGED_EVENT_ID])
    vg2 = make_event_group(vi.OVERSPEED_EVENTGROUP_ID, [vi.OVERSPEED_WARNING_EVENT_ID])
    vs = make_service(vi.SERVICE_ID,
        [make_method(vi.GET_SPEED_METHOD_ID), make_method(vi.GET_VEHICLE_STATE_METHOD_ID)], [vg1, vg2])
    vehicle = client_instance(daemon, vs, vi.INSTANCE_ID, 30512)
    vehicle.register_callback(vehicle_callback)
    vehicle.subscribe_eventgroup(vg1, 5)
    vehicle.subscribe_eventgroup(vg2, 5)

    cg = make_event_group(ci.CLIMATE_EVENTGROUP_ID, [ci.CABIN_TEMPERATURE_CHANGED_EVENT_ID])
    cs = make_service(ci.SERVICE_ID,
        [make_method(ci.GET_CABIN_TEMPERATURE_METHOD_ID), make_method(ci.SET_TARGET_TEMPERATURE_METHOD_ID)], [cg])
    climate = client_instance(daemon, cs, ci.INSTANCE_ID, 30513)
    climate.register_callback(climate_callback)
    climate.subscribe_eventgroup(cg, 5)

    async def temperature_command_loop():
        print("[Central Display] Enter target temperature in tenths °C (e.g. 220); type q to stop input.")
        while True:
            try:
                raw = await asyncio.to_thread(input, "[Central Display] Set target (160..300): ")
            except EOFError:
                return
            if raw.strip().lower() == "q":
                return
            try:
                requested = int(raw.strip())
                if not -32768 <= requested <= 32767:
                    raise ValueError
            except ValueError:
                print("[Central Display] Enter a signed 16-bit integer, e.g. 220.")
                continue
            if not await service_is_available(climate):
                print("[Central Display] ClimateService is NOT AVAILABLE; request not sent.")
                continue
            try:
                response = await call_when_found(climate, ci.SET_TARGET_TEMPERATURE_METHOD_ID, i16(requested))
                if response.payload:
                    status = read_u8(response.payload)
                    print("[Central Display] SetTargetTemperature response: " +
                          ("ACCEPTED" if status == ci.ACCEPTED else "INVALID_TEMPERATURE"))
            except Exception as exc:
                print(f"[Central Display] SetTargetTemperature failed: {exc}")

    last_vehicle = last_climate = None
    input_task = asyncio.create_task(temperature_command_loop())
    try:
        while True:
            vf, cf = await service_is_available(vehicle), await service_is_available(climate)
            if vf != last_vehicle:
                print(f"[Central Display] VehicleSpeedService: {'AVAILABLE' if vf else 'NOT AVAILABLE'}", flush=True)
                last_vehicle = vf
            if cf != last_climate:
                print(f"[Central Display] ClimateService: {'AVAILABLE' if cf else 'NOT AVAILABLE'}", flush=True)
                last_climate = cf
            if vf:
                try:
                    sr = await call_when_found(vehicle, vi.GET_SPEED_METHOD_ID)
                    tr = await call_when_found(vehicle, vi.GET_VEHICLE_STATE_METHOD_ID)
                    if sr.payload and tr.payload:
                        print(f"[Central Display] Vehicle Speed: {read_u16(sr.payload)} km/h | State: {'STOPPED' if read_u8(tr.payload)==0 else 'MOVING'}", flush=True)
                except Exception as exc: print(f"[Central Display] Vehicle request failed: {exc}", flush=True)
            if cf:
                try:
                    cr = await call_when_found(climate, ci.GET_CABIN_TEMPERATURE_METHOD_ID)
                    if cr.payload: print(f"[Central Display] Cabin Temperature: {read_i16(cr.payload)/10:.1f} °C", flush=True)
                except Exception as exc: print(f"[Central Display] Climate request failed: {exc}", flush=True)
            await asyncio.sleep(7)
    finally:
        input_task.cancel()
        await daemon.disconnect_from_daemon()

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: print("\n[Central Display] Stopped by user.")
