#!/usr/bin/env python3
"""
Helper script to render a MechanicsSketches JSON file to an image/PDF.

Usage:
    python generate_sketch.py <input.json> <output.pdf|png|svg>

The input JSON should follow the MechanicsSketches sketch format.
Alternatively, it can be a "script" JSON with a "commands" array
that builds a sketch step-by-step.
"""

import sys
import os
import json

# Ensure MechanicsSketches is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from MechanicsSketches import *  # noqa: E402
from MechanicsSketches.qt_renderer import render  # noqa: E402


def build_sketch_from_commands(commands_data):
    """
    Build a sketch from a list of command dicts.

    Example input:
    {
        "name": "My Sketch",
        "scale_factor": 30.0,
        "commands": [
            {"action": "add_beam", "params": {"ax": 0, "ay": 0, "bx": 300, "by": 0}},
            {"action": "add_pinned_support", "params": {"cx": 0, "cy": 0, "angle_deg": 0}},
            {"action": "add_force", "params": {"cx": 150, "cy": 0, "angle_deg": 0, "annotation": "$F$"}}
        ]
    }
    """
    name = commands_data.get("name", "Sketch")
    S = commands_data.get("scale_factor", 30.0)
    sketch = create_sketch(name)

    action_map = {
        "add_beam": add_beam,
        "add_truss": add_truss,
        "add_pinned_support": add_pinned_support,
        "add_roller_support": add_roller_support,
        "add_fixed_support": add_fixed_support,
        "add_hinge": add_hinge,
        "add_force": add_force,
        "add_moment": add_moment,
        "add_dimension_arrow": add_dimension_arrow,
        "add_dimension_thickness": add_dimension_thickness,
        "add_coordinate_system": add_coordinate_system,
        "add_text": add_text,
    }

    for cmd in commands_data.get("commands", []):
        action = cmd.get("action")
        params = cmd.get("params", {})

        if action not in action_map:
            print(f"Warning: Unknown action '{action}', skipping.")
            continue

        fn = action_map[action]

        # Inject scale_factor if the function expects it and it's not provided
        if action != "add_text" and "scale_factor" not in params:
            params["scale_factor"] = S

        try:
            fn(sketch, **params)
        except TypeError as e:
            print(f"Error in '{action}': {e}")
            sys.exit(1)

    return sketch


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_sketch.py <input.json> <output.pdf|png|svg>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    with open(input_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    # Determine if this is a raw sketch dict or a command-based format
    if "commands" in data:
        sketch = build_sketch_from_commands(data)
    elif "objects" in data:
        # Raw sketch format — use directly
        sketch = data
    else:
        print("Error: JSON must contain either 'commands' or 'objects' key.")
        sys.exit(1)

    render(sketch, filename=output_path, dpi=300)
    print(f"Rendered sketch to: {output_path}")


if __name__ == "__main__":
    main()
