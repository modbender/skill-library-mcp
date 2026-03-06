# ESP-IDF CLI patterns (Linux/WSL)

Keep this reference short; paste outputs when troubleshooting.

## Recommended workflow

```bash
# 1. Activate ESP-IDF environment (do this first)
cd /path/to/esp-idf
. ./export.sh

# 2. Build your project
cd /path/to/your-project
idf.py set-target esp32s2
idf.py build
idf.py -p /dev/ttyS33 flash monitor
```

## Environment sanity
- Confirm idf.py exists:
  - `command -v idf.py`
  - `idf.py --version`
- If `idf.py` is missing:
  - `source $IDF_PATH/export.sh` (recommended)
  - or run with wrapper: `./scripts/espidf.sh --idf-path /path/to/esp-idf build`
- In an ESP-IDF project dir, these should exist:
  - `CMakeLists.txt`
  - `main/`

## Common commands
- Select chip target (once per project):
  - `idf.py set-target esp32`
  - `idf.py set-target esp32s2`
  - `idf.py set-target esp32s3`
  - `idf.py set-target esp32c3`
- Configure:
  - `idf.py menuconfig`
- Build:
  - `idf.py build`
- Flash:
  - `idf.py -p /dev/ttyS33 -b 1152000 flash`
- Monitor:
  - `idf.py -p /dev/ttyS33 monitor`
- Flash + monitor:
  - `idf.py -p /dev/ttyS33 -b 1152000 flash monitor`
- Clean:
  - `idf.py fullclean`
- Erase flash (careful):
  - `idf.py -p /dev/ttyUSB0 erase-flash`

## What to paste back when something fails
1) Your chip target (`esp32`, `esp32s3`, etc.)
2) `idf.py --version`
3) The exact command you ran
4) The *first* error lines (usually near the top)
5) Your serial port path and whether it exists: `ls -l <PORT>`

## Serial notes
- If monitor output is unreadable, baud is likely wrong.
- Flash baud (`-b`) and app UART baud (menuconfig) can differ.
- If flash is flaky, drop to `-b 115200`.

## WSL notes (generic)
- Your ports may look like `/dev/ttyS33` (WSL mapped serial). Use whatever exists under `/dev/ttyS*`.
- Ensure the USB-serial device is visible in WSL.
- Ensure your user has permission to open the tty device (group membership).
