"""
_pdf_exporter.py - PDF export via Playwright (Chromium headless).
Converts a standalone HTML CV file to PDF, reusing the same Playwright
dependency already used by the job scraper.

Usage:
    import asyncio
    from _pdf_exporter import export_pdf
    asyncio.run(export_pdf("cv.html", "cv.pdf"))
"""

import asyncio
from pathlib import Path


async def export_pdf(
    html_path: str,
    output_path: str,
    format_: str = "A4",
    print_background: bool = True,
) -> Path:
    """Render an HTML file to PDF using Playwright Chromium.

    Parameters
    ----------
    html_path:
        Path to the HTML file to convert.
    output_path:
        Path where the PDF will be written.
    format_:
        Page format (default ``"A4"``).
    print_background:
        Whether to print background colours and images (default ``True``).

    Returns
    -------
    Path
        The resolved path to the generated PDF.

    Raises
    ------
    FileNotFoundError
        If the HTML file does not exist.
    ImportError
        If Playwright is not installed.
    """
    html_file = Path(html_path).resolve()
    if not html_file.exists():
        raise FileNotFoundError(f"HTML file not found: {html_file}")

    pdf_file = Path(output_path).resolve()
    pdf_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise ImportError(
            "Playwright is required for PDF export.\n"
            "Install it with:  pip install playwright && playwright install chromium"
        )

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(html_file.as_uri(), wait_until="networkidle")
        await page.pdf(
            path=str(pdf_file),
            format=format_,
            print_background=print_background,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )
        await browser.close()

    return pdf_file
