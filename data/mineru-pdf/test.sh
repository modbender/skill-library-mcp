#!/bin/bash
# Test script for MinerU PDF parsing

PDF_FILE="${1:-/Users/lwj04/.openclaw/media/inbound/4088222---c7382f48-d754-4ae4-87d6-fd12e12cc43f.pdf}"
START_PAGE="${2:-0}"
END_PAGE="${3:-0}"

echo "Parsing PDF: $PDF_FILE"
echo "Page range: $START_PAGE to $END_PAGE"
echo ""

uvx --from mcp-mineru python -c "
import asyncio
from mcp_mineru.server import call_tool

async def parse_pdf():
    result = await call_tool(
        name='parse_pdf',
        arguments={
            'file_path': '$PDF_FILE',
            'backend': 'pipeline',
            'formula_enable': True,
            'table_enable': True,
            'start_page': $START_PAGE,
            'end_page': $END_PAGE
        }
    )
    if hasattr(result, 'content'):
        for item in result.content:
            if hasattr(item, 'text'):
                print(item.text)
                break

asyncio.run(parse_pdf())
"
