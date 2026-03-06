"""
ReSpeaker USB Mic Array v1.0 (0x2886:0x0007) LED control.

States:
  listen()  — solid blue      (wake word detected, recording)
  think()   — solid cyan      (transcribed, waiting for Alfred)
  speak()   — solid green     (playing TTS response)
  off()     — all off
  error()   — brief red flash (STT failed / no speech)

All functions are no-ops if the device isn't found or accessible.
"""

import usb.core
import usb.util
import logging

log = logging.getLogger("jetson.voice")

_VENDOR_ID  = 0x2886
_PRODUCT_ID = 0x0007
_MONO_CMD   = 1

_dev       = None
_hid_intf  = None
_ready     = False


def _init():
    global _dev, _hid_intf, _ready
    if _ready:
        return True
    try:
        dev = usb.core.find(idVendor=_VENDOR_ID, idProduct=_PRODUCT_ID)
        if dev is None:
            log.warning("💡 LED: ReSpeaker not found — skipping LED control")
            return False

        config = dev.get_active_configuration()
        intf_num = None
        for intf in config:
            if intf.bInterfaceClass == 0x03:  # HID
                intf_num = intf.bInterfaceNumber
                try:
                    if dev.is_kernel_driver_active(intf_num):
                        dev.detach_kernel_driver(intf_num)
                except Exception:
                    pass
                break

        if intf_num is None:
            log.warning("💡 LED: HID interface not found")
            return False

        _dev       = dev
        _hid_intf  = intf_num
        _ready     = True
        log.info("💡 LED: ReSpeaker LEDs ready")
        return True

    except Exception as e:
        log.warning(f"💡 LED: init failed: {e}")
        return False


def _write(address, data):
    if not _ready:
        return
    try:
        data   = bytearray(data)
        packet = bytearray([
            address & 0xFF, (address >> 8) & 0xFF,
            len(data) & 0xFF, (len(data) >> 8) & 0xFF,
        ]) + data
        _dev.ctrl_transfer(0x21, 0x09, 0x0300, _hid_intf, packet, 1000)
    except Exception as e:
        log.debug(f"💡 LED: write error: {e}")


def _set(r, g, b):
    _write(0, [_MONO_CMD, b, g, r])


# ─── Public API ───────────────────────────────────────────────────────────────

def init():
    """Call once at startup."""
    _init()


def listen():
    """Solid blue — recording the user's command."""
    if _init():
        _set(0, 0, 80)


def think():
    """Solid cyan — sending to Alfred, waiting for response."""
    if _init():
        _set(0, 60, 80)


def speak():
    """Solid green — playing TTS response."""
    if _init():
        _set(0, 60, 0)


def error():
    """Brief dim red — didn't catch speech."""
    if _init():
        _set(60, 0, 0)


def off():
    """All LEDs off."""
    if _init():
        _set(0, 0, 0)
