#!/usr/bin/env python3
"""
Draw.io URL Generator Script

This script generates a draw.io URL from Mermaid, XML, or CSV diagram code.
It outputs a markdown link that opens the diagram in draw.io.

Usage:
    python generate_drawio_url.py --type mermaid --code "graph TD\n    A --> B"
    python generate_drawio_url.py -t xml -c "<mxGraphModel>...</mxGraphModel>"
    python generate_drawio_url.py -t csv -c "name,manager\nCEO,\nCTO,CEO"
"""

import argparse
import json
import zlib
import base64
from urllib.parse import quote


def generate_drawio_url(diagram_type: str, diagram_code: str) -> str:
    """
    Generate a draw.io URL from diagram code.
    
    Args:
        diagram_type: "mermaid", "xml", or "csv"
        diagram_code: The diagram content as a string
    
    Returns:
        A draw.io URL that opens the diagram
    """
    encoded = quote(diagram_code, safe='')
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    raw_deflate = c.compress(encoded.encode('utf-8')) + c.flush()
    data = base64.b64encode(raw_deflate).decode()
    
    payload = json.dumps({"type": diagram_type, "compressed": True, "data": data})
    url = f"https://app.diagrams.net/?pv=0&grid=0#create={quote(payload, safe='')}"
    
    return url


def main():
    parser = argparse.ArgumentParser(
        description='Generate a draw.io URL from diagram code'
    )
    parser.add_argument(
        '-t', '--type',
        type=str,
        required=True,
        choices=['mermaid', 'xml', 'csv'],
        help='Diagram type: mermaid, xml, or csv'
    )
    parser.add_argument(
        '-c', '--code',
        type=str,
        required=True,
        help='Diagram code content'
    )
    
    args = parser.parse_args()
    
    url = generate_drawio_url(args.type, args.code)
    print(f"[点击查看图表]({url})")


if __name__ == '__main__':
    main()
