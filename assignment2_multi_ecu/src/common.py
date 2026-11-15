"""Shared helpers for the Assignment 2 someipy 2.x implementation."""
import asyncio
import logging
import socket
import struct

from someipy import (
    Event, EventGroup, Method, ServiceBuilder, TransportLayerProtocol,
    MessageType, ReturnCode, MethodResult, connect_to_someipy_daemon,
)
from someipy.server_service_instance import ServerServiceInstance
from someipy.client_service_instance import ClientServiceInstance

IP = "127.0.0.1"
TTL = 5
OFFER_MS = 2000

def u8(value=0): return struct.pack("!B", int(value))
def u16(value=0): return struct.pack("!H", int(value))
def i16(value=0): return struct.pack("!h", int(value))
def read_u8(data): return struct.unpack("!B", data[:1])[0]
def read_u16(data): return struct.unpack("!H", data[:2])[0]
def read_i16(data): return struct.unpack("!h", data[:2])[0]

def make_method(method_id, handler=None):
    if handler is None:
        return Method(id=method_id, protocol=TransportLayerProtocol.UDP)
    return Method(id=method_id, protocol=TransportLayerProtocol.UDP, method_handler=handler)

def make_event_group(group_id, event_ids):
    events = [Event(id=eid, protocol=TransportLayerProtocol.UDP) for eid in event_ids]
    return EventGroup(id=group_id, events=events)

def make_service(service_id, methods=(), event_groups=()):
    builder = ServiceBuilder().with_service_id(service_id).with_major_version(1)
    for method in methods:
        builder = builder.with_method(method)
    for group in event_groups:
        builder = builder.with_eventgroup(group)
    return builder.build()

async def daemon_connect():
    return await connect_to_someipy_daemon()

def server_instance(daemon, service, instance_id, port):
    return ServerServiceInstance(
        daemon=daemon, service=service, instance_id=instance_id,
        endpoint_ip=IP, endpoint_port=port, ttl=TTL,
        cyclic_offer_delay_ms=OFFER_MS,
    )

def client_instance(daemon, service, instance_id, port):
    return ClientServiceInstance(
        daemon=daemon, service=service, instance_id=instance_id,
        endpoint_ip=IP, endpoint_port=port,
    )

def method_response(payload=b"", ok=True):
    result = MethodResult()
    result.message_type = MessageType.RESPONSE
    result.return_code = ReturnCode.E_OK if ok else ReturnCode.E_NOT_OK
    result.payload = payload
    return result

def print_banner(title):
    print("\n" + "=" * 58)
    print(title)
    print("=" * 58, flush=True)

async def service_is_available(client):
    """Return discovery state across someipy API variants.

    someipy 2.x exposes is_available() as an async method. The fallback
    supports older builds that expose service_found().
    """
    checker = getattr(client, "is_available", None)
    if checker is not None:
        result = checker()
        if asyncio.iscoroutine(result):
            return bool(await result)
        return bool(result)
    legacy_checker = getattr(client, "service_found", None)
    if legacy_checker is not None:
        result = legacy_checker()
        if asyncio.iscoroutine(result):
            result = await result
        return bool(result)
    raise AttributeError("ClientServiceInstance has no is_available/service_found API")

async def wait_for_service(client, label):
    last = None
    while True:
        found = await service_is_available(client)
        if found != last:
            print(f"[SD] {label}: {'AVAILABLE' if found else 'NOT AVAILABLE'}", flush=True)
            last = found
        await asyncio.sleep(1)

async def call_when_found(client, method_id, payload=b"", timeout=2):
    if not await service_is_available(client):
        raise RuntimeError("Service not discovered yet")
    return await asyncio.wait_for(client.call_method(method_id, payload), timeout=timeout)
