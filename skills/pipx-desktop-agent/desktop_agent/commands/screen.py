"""Screen and screenshot commands."""
import time
import typer
import pyautogui
from pathlib import Path
from typing import Optional
import json
import pywinctl
from desktop_agent.utils import CommandResponse, ErrorCode, DesktopAgentError

app = typer.Typer(help="Screen and screenshot commands")


def _get_window_region(window_name: Optional[str] = None, active: bool = False) -> Optional[tuple[int, int, int, int]]:
    """Get the region of a specific or active window using PyWinCtl."""
    try:
        if active:
            window = pywinctl.getActiveWindow()
            if not window:
                return None
        elif window_name:
            windows = pywinctl.getWindowsWithTitle(window_name)
            if not windows:
                return None
            window = windows[0]
        else:
            return None

        return (int(window.left), int(window.top), int(window.width), int(window.height))
    except Exception:
        return None


def _handle_command(command: str, func, *args, **kwargs):
    start = time.time()
    try:
        result = func(*args, **kwargs)
        duration_ms = int((time.time() - start) * 1000)
        response = CommandResponse.success_response(
            command=command,
            data=result,
            duration_ms=duration_ms,
        )
        response.print()
    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        error = DesktopAgentError(
            code=ErrorCode.from_exception(e),
            message=str(e),
        )
        response = CommandResponse.error_response(
            command=command,
            code=error.code.to_string(),
            message=error.message,
            details=error.details,
            duration_ms=duration_ms,
        )
        response.print()
        raise sys.exit(error.exit_code())


@app.command()
def screenshot(
    filename: str = typer.Argument("screenshot.png", help="Output filename"),
    region: str = typer.Option(None, "--region", "-r", help="Region as 'x,y,width,height'"),
    window: Optional[str] = typer.Option(None, "--window", "-w", help="Target window title"),
    active: bool = typer.Option(False, "--active", "-a", help="Target active window"),
):
    """Take a screenshot of the entire screen, a window, or a specific region."""
    def execute():
        target_region = None

        window_region = _get_window_region(window, active)
        if window_region:
            target_region = window_region

        if region:
            try:
                target_region = tuple(map(int, region.split(",")))
            except ValueError:
                raise DesktopAgentError(
                    code=ErrorCode.INVALID_ARGUMENT,
                    message="Region must be in format 'x,y,width,height'",
                )

        if target_region:
            img = pyautogui.screenshot(region=target_region)
            img.save(filename)
            return {
                "filename": filename,
                "region": {
                    "x": target_region[0],
                    "y": target_region[1],
                    "width": target_region[2],
                    "height": target_region[3],
                },
            }
        else:
            img = pyautogui.screenshot()
            img.save(filename)
            return {"filename": filename, "region": None}
    _handle_command("screen.screenshot", execute)


@app.command()
def locate(
    image: str = typer.Argument(..., help="Path to image to locate"),
    confidence: float = typer.Option(0.9, "--confidence", "-c", help="Match confidence (0.0-1.0)"),
    window: Optional[str] = typer.Option(None, "--window", "-w", help="Search within a specific window"),
    active: bool = typer.Option(False, "--active", "-a", help="Search within the active window"),
):
    """Locate an image on the screen or within a targeted window."""
    def execute():
        region = _get_window_region(window, active)

        if not Path(image).exists():
            raise DesktopAgentError(
                code=ErrorCode.IMAGE_NOT_FOUND,
                message=f"Image file '{image}' not found",
            )

        location = pyautogui.locateOnScreen(image, confidence=confidence, region=region)
        if location:
            return {
                "image_found": True,
                "bounding_box": {
                    "left": location.left,
                    "top": location.top,
                    "width": location.width,
                    "height": location.height,
                    "center_x": location.left + location.width // 2,
                    "center_y": location.top + location.height // 2,
                },
            }
        else:
            return {"image_found": False}
    _handle_command("screen.locate", execute)


@app.command()
def locate_center(
    image: str = typer.Argument(..., help="Path to image to locate"),
    confidence: float = typer.Option(0.9, "--confidence", "-c", help="Match confidence (0.0-1.0)"),
    window: Optional[str] = typer.Option(None, "--window", "-w", help="Search within a specific window"),
    active: bool = typer.Option(False, "--active", "-a", help="Search within the active window"),
):
    """Get the center coordinates of an image on the screen or within a window."""
    def execute():
        region = _get_window_region(window, active)

        if not Path(image).exists():
            raise DesktopAgentError(
                code=ErrorCode.IMAGE_NOT_FOUND,
                message=f"Image file '{image}' not found",
            )

        location = pyautogui.locateCenterOnScreen(image, confidence=confidence, region=region)
        if location:
            return {"position": {"x": location.x, "y": location.y}}
        else:
            return {"image_found": False}
    _handle_command("screen.locate_center", execute)


@app.command()
def pixel(
    x: int = typer.Argument(..., help="X coordinate"),
    y: int = typer.Argument(..., help="Y coordinate"),
):
    """Get the RGB color of a pixel at specified coordinates."""
    def execute():
        color = pyautogui.pixel(x, y)
        return {
            "pixel": {
                "r": color[0],
                "g": color[1],
                "b": color[2],
                "hex": f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}",
            }
        }
    _handle_command("screen.pixel", execute)


@app.command()
def size():
    """Get the screen size."""
    def execute():
        screen_size = pyautogui.size()
        return {
            "size": {
                "width": screen_size.width,
                "height": screen_size.height,
            }
        }
    _handle_command("screen.size", execute)


@app.command()
def on_screen(
    x: int = typer.Argument(..., help="X coordinate"),
    y: int = typer.Argument(..., help="Y coordinate"),
):
    """Check if coordinates are on the screen."""
    def execute():
        is_on_screen = pyautogui.onScreen(x, y)
        return {"on_screen": is_on_screen}
    _handle_command("screen.on_screen", execute)


_reader = None
_reader_langs = None


def _get_system_language() -> str:
    import locale
    try:
        system_locale = locale.getdefaultlocale()[0]
        if system_locale:
            lang_code = system_locale.split('_')[0].lower()
            return lang_code
    except Exception:
        pass
    return 'en'


def _get_default_languages() -> list[str]:
    system_lang = _get_system_language()
    if system_lang == 'en':
        return ['en']
    return [system_lang, 'en']


def get_reader(lang: Optional[list[str]] = None):
    global _reader, _reader_langs
    langs = lang or _get_default_languages()
    if _reader is None or set(langs) != set(_reader_langs or []):
        import easyocr
        _reader = easyocr.Reader(langs)
        _reader_langs = langs
    return _reader


@app.command(name="locate-text-coordinates")
def locate_text_coordinates(
    search: str = typer.Argument(..., help="Text to search for (partial match)"),
    image: Optional[str] = typer.Option(None, "--image", "-i", help="Path to image (if not provided, takes screenshot)"),
    lang: Optional[str] = typer.Option(None, "--lang", "-l", help="Languages to use (comma-separated, default: system language + en)"),
    case_sensitive: bool = typer.Option(False, "--case-sensitive", "-c", help="Case sensitive search"),
    window: Optional[str] = typer.Option(None, "--window", "-w", help="Search within a specific window"),
    active: bool = typer.Option(False, "--active", "-a", help="Search within the active window"),
):
    """Locate text coordinates on screen, within a window, or in an image using OCR."""
    def execute():
        region = _get_window_region(window, active)

        if image:
            if not Path(image).exists():
                raise DesktopAgentError(
                    code=ErrorCode.IMAGE_NOT_FOUND,
                    message=f"Image file '{image}' not found",
                )
            image_path = image
        else:
            screenshot_path = "temp_screenshot.png"
            img = pyautogui.screenshot(region=region)
            img.save(screenshot_path)
            image_path = screenshot_path

        languages = lang.split(',') if lang else None
        reader = get_reader(languages)

        results = reader.readtext(image_path)

        search_text = search if case_sensitive else search.lower()
        matches = []

        for (bbox, text, confidence) in results:
            compare_text = text if case_sensitive else text.lower()
            if search_text in compare_text:
                top_left = bbox[0]
                bottom_right = bbox[2]

                x1, y1 = int(top_left[0]), int(top_left[1])
                x2, y2 = int(bottom_right[0]), int(bottom_right[1])
                width = x2 - x1
                height = y2 - y1
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)

                match = {
                    "text": text,
                    "confidence": float(confidence),
                    "bounding_box": {
                        "x": x1,
                        "y": y1,
                        "width": width,
                        "height": height,
                        "center_x": center_x,
                        "center_y": center_y,
                    },
                }
                matches.append(match)

        if not image and Path("temp_screenshot.png").exists():
            Path("temp_screenshot.png").unlink()

        return {"matches": matches}
    _handle_command("screen.locate_text_coordinates", execute)


@app.command(name="read-all-text")
def read_all_text(
    image: Optional[str] = typer.Option(None, "--image", "-i", help="Path to image (if not provided, takes screenshot)"),
    lang: Optional[str] = typer.Option(None, "--lang", "-l", help="Languages to use (comma-separated, default: system language + en)"),
    window: Optional[str] = typer.Option(None, "--window", "-w", help="Read from a specific window"),
    active: bool = typer.Option(False, "--active", "-a", help="Read from the active window"),
):
    """Read all text from screen, a targeted window, or an image using OCR."""
    def execute():
        region = _get_window_region(window, active)

        if image:
            if not Path(image).exists():
                raise DesktopAgentError(
                    code=ErrorCode.IMAGE_NOT_FOUND,
                    message=f"Image file '{image}' not found",
                )
            image_path = image
        else:
            screenshot_path = "temp_screenshot.png"
            img = pyautogui.screenshot(region=region)
            img.save(screenshot_path)
            image_path = screenshot_path

        languages = lang.split(',') if lang else None
        reader = get_reader(languages)

        results = reader.readtext(image_path)

        all_text = []
        for (bbox, text, confidence) in results:
            top_left = bbox[0]
            bottom_right = bbox[2]

            x1, y1 = int(top_left[0]), int(top_left[1])
            x2, y2 = int(bottom_right[0]), int(bottom_right[1])
            width = x2 - x1
            height = y2 - y1
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            item = {
                "text": text,
                "confidence": float(confidence),
                "bounding_box": {
                    "x": x1,
                    "y": y1,
                    "width": width,
                    "height": height,
                    "center_x": center_x,
                    "center_y": center_y,
                },
            }
            all_text.append(item)

        if not image and Path("temp_screenshot.png").exists():
            Path("temp_screenshot.png").unlink()

        return {"text_items": all_text}
    _handle_command("screen.read_all_text", execute)


import sys
