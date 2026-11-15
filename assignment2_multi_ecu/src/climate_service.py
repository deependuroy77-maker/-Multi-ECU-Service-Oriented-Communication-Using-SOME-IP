"""Climate ECU: offers ClimateService with server-side validation."""
import asyncio
from .common import *
from . import climate_interface as ci

current_temp = 240
target_temp = 220

async def get_temp_handler(payload, addr):
    print(f"[Climate ECU] GetCabinTemperature request from {addr}")
    return method_response(i16(current_temp))

async def set_target_handler(payload, addr):
    global target_temp
    try:
        requested = read_i16(payload)
    except Exception:
        print("[Climate ECU] Malformed target-temperature payload")
        return method_response(u8(ci.INVALID_TEMPERATURE))
    if ci.MIN_TARGET_TENTHS <= requested <= ci.MAX_TARGET_TENTHS:
        target_temp = requested
        status = ci.ACCEPTED
        print(f"[Climate ECU] Target set to {requested/10:.1f} °C: ACCEPTED")
    else:
        status = ci.INVALID_TEMPERATURE
        print(f"[Climate ECU] Requested {requested/10:.1f} °C: INVALID_TEMPERATURE; target unchanged")
    return method_response(u8(status))

async def main():
    global current_temp
    print_banner("ECU 3 — CLIMATE ECU / ClimateService")
    daemon = await daemon_connect()
    group = make_event_group(ci.CLIMATE_EVENTGROUP_ID, [ci.CABIN_TEMPERATURE_CHANGED_EVENT_ID])
    service = make_service(
        ci.SERVICE_ID,
        [make_method(ci.GET_CABIN_TEMPERATURE_METHOD_ID, get_temp_handler),
         make_method(ci.SET_TARGET_TEMPERATURE_METHOD_ID, set_target_handler)],
        [group],
    )
    instance = server_instance(daemon, service, ci.INSTANCE_ID, 30502)
    await instance.start_offer()
    print(f"[Climate ECU] Offering service 0x{ci.SERVICE_ID:04X}, instance 0x{ci.INSTANCE_ID:04X}")
    values = [240, 245, 250, 255, 260]
    idx = 0
    try:
        while True:
            current_temp = values[idx % len(values)]
            idx += 1
            print(f"[Climate ECU] Cabin temperature = {current_temp/10:.1f} °C; publishing event")
            instance.send_event(ci.CLIMATE_EVENTGROUP_ID, ci.CABIN_TEMPERATURE_CHANGED_EVENT_ID, i16(current_temp))
            await asyncio.sleep(5)
    finally:
        await instance.stop_offer()
        await daemon.disconnect_from_daemon()

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: print("\n[Climate ECU] Stopped by user.")
