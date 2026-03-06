#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "playwright",
#     "python-slugify[unidecode]>=8.0.4",
# ]
# ///
import argparse
import os
from pathlib import Path

from slugify import slugify
from playwright.sync_api import sync_playwright

OUT_DIR = os.getenv("PDF_OUT_DIR", "~/Documents")


def get_stem_from_url(url):
    """Get file stem from a url.

    https://mariozechner.at/posts/2025-11-30-pi-coding-agent/
    -> 2025-11-30-pi-coding-agent

    https://www.ruanyifeng.com/blog/2026/01/weekly-issue-383.html
    -> weekly-issue-383
    """
    url = url.strip().rstrip('/')
    name = url.rsplit('/', 1)[-1]  # last url part
    return name.rsplit('.', 1)[0]  # rm .ext if any


def slugify_stem(stem):
    return slugify(
        stem,
        separator="-",
        max_length=100,
        allow_unicode=True,
        word_boundary=True,
        lowercase=False,
    )


def get_pdf_path(url, output=None) -> Path:
    output = output or OUT_DIR
    path = Path(output).expanduser().resolve()

    # a file
    if path.suffix.lower() == '.pdf':
        return path

    # a folder
    stem = get_stem_from_url(url)
    slug = slugify_stem(stem)
    return path / f"{slug}.pdf"


class iPhone13Pro:
    width = 390
    height = 844 - 74  # rm notch
    device_scale_factor = 3
    is_mobile = True
    has_touch = True
    user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'

    def get_context(self, browser):
        return browser.new_context(
            user_agent=self.user_agent,
            device_scale_factor=self.device_scale_factor,
            is_mobile=self.is_mobile,
            has_touch=self.has_touch,
            viewport={'width': self.width, 'height': self.height},
        )

    def save_as_pdf(self, page, pdf_path, scale=1.1):
        height = self.height
        return page.pdf(
            path=pdf_path,
            width=f'{self.width}px',
            height=f'{height}px',
            print_background=True,
            scale=scale,
            margin={'top': '0px', 'bottom': '0px', 'left': '0px', 'right': '0px'}
        )


def cli():
    parser = argparse.ArgumentParser(description="Convert webpage to PDF for iPhone")
    parser.add_argument("url", help="url to convert")
    parser.add_argument("-o", "--output", help="output path for pdf, either dir or file")
    return parser.parse_args()


def main():
    args = cli()
    url = args.url
    pdf_path = get_pdf_path(url, output=args.output)

    device = iPhone13Pro()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = device.get_context(browser)
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            # Give it a small buffer for fonts/images to settle
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"Navigation warning: {e}")
            print("Proceeding to print...")

        device.save_as_pdf(page, pdf_path)
        print(pdf_path)
        browser.close()


if __name__ == "__main__":
    main()
