"""Vehicle ECU: offers VehicleSpeedService."""
import asyncio
from .common import *
from . import vehicle_speed_interface as vi

speed = 0
SEQUENCE = [50, 60, 70, 80, 90, 100, 0, 45, 85, 55]

async def get_speed_handler(payload, addr):
    print(f"[Vehicle ECU] GetSpeed request from {addr}")
    return method_response(u16(speed))

async def get_state_handler(payload, addr):
    state = 0 if speed == 0 else 1
    print(f"[Vehicle ECU] GetVehicleState request from {addr}: {state}")
    return method_response(u8(state))

async def main():
    global speed
    print_banner("ECU 1 — VEHICLE ECU / VehicleSpeedService")
    daemon = await daemon_connect()
    speed_group = make_event_group(vi.SPEED_EVENTGROUP_ID, [vi.SPEED_CHANGED_EVENT_ID])
    over_group = make_event_group(vi.OVERSPEED_EVENTGROUP_ID, [vi.OVERSPEED_WARNING_EVENT_ID])
    service = make_service(
        vi.SERVICE_ID,
        [make_method(vi.GET_SPEED_METHOD_ID, get_speed_handler),
         make_method(vi.GET_VEHICLE_STATE_METHOD_ID, get_state_handler)],
        [speed_group, over_group],
    )
    instance = server_instance(daemon, service, vi.INSTANCE_ID, 30501)
    await instance.start_offer()
    print(f"[Vehicle ECU] Offering service 0x{vi.SERVICE_ID:04X}, instance 0x{vi.INSTANCE_ID:04X}")
    index = 0
    try:
        while True:
            speed = SEQUENCE[index % len(SEQUENCE)]
            index += 1
            print(f"[Vehicle ECU] Speed = {speed} km/h; publishing SpeedChanged")
            instance.send_event(vi.SPEED_EVENTGROUP_ID, vi.SPEED_CHANGED_EVENT_ID, u16(speed))
            if speed > 80:
                print(f"[Vehicle ECU] OVERSPEED: {speed} km/h")
                instance.send_event(vi.OVERSPEED_EVENTGROUP_ID, vi.OVERSPEED_WARNING_EVENT_ID, u16(speed))
            await asyncio.sleep(4)
    finally:
        await instance.stop_offer()
        await daemon.disconnect_from_daemon()

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: print("\n[Vehicle ECU] Stopped by user.")
