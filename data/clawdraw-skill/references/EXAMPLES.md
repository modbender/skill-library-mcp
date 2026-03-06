# Composition Examples

Complete examples mixing built-in primitives and custom stroke patterns.

## 1. Mandala with Gradient Background

A mandala centered on a color wash background.

```json
{
  "composition": [
    {
      "primitive": "colorWash",
      "params": { "cx": 0, "cy": 0, "width": 400, "height": 400, "color": "#1a0a2e", "opacity": 0.4 }
    },
    {
      "primitive": "mandala",
      "params": {
        "cx": 0, "cy": 0, "radius": 150, "symmetry": 12, "complexity": 5,
        "colors": ["#ff6b6b", "#feca57", "#48dbfb", "#ff9ff3"],
        "brushSize": 3, "wobbleAmount": 0.2
      }
    },
    {
      "primitive": "circle",
      "params": { "cx": 0, "cy": 0, "radius": 160, "color": "#feca57", "brushSize": 2, "opacity": 0.5 }
    }
  ],
  "symmetry": "none"
}
```

## 2. Forest Scene

Fractal trees on a hatched ground with a flow field sky.

```json
{
  "composition": [
    {
      "primitive": "gradientFill",
      "params": {
        "cx": 0, "cy": -100, "width": 500, "height": 200,
        "colorStart": "#0a0a2e", "colorEnd": "#1a3a5c", "angle": 90, "density": 0.6
      }
    },
    {
      "primitive": "flowField",
      "params": {
        "cx": 0, "cy": -120, "width": 500, "height": 150,
        "noiseScale": 0.008, "density": 0.3, "palette": "turbo", "brushSize": 1
      }
    },
    {
      "primitive": "hatchFill",
      "params": {
        "cx": 0, "cy": 100, "width": 500, "height": 80,
        "angle": 0, "spacing": 4, "color": "#2d5a27", "brushSize": 2
      }
    },
    {
      "primitive": "fractalTree",
      "params": {
        "cx": -80, "cy": 60, "trunkLength": 70, "branchAngle": 25,
        "depth": 6, "palette": "viridis", "brushSize": 4, "branchRatio": 0.68
      }
    },
    {
      "primitive": "fractalTree",
      "params": {
        "cx": 60, "cy": 70, "trunkLength": 55, "branchAngle": 30,
        "depth": 5, "palette": "viridis", "brushSize": 3, "branchRatio": 0.72
      }
    }
  ],
  "symmetry": "none"
}
```

## 3. Abstract Art with Strange Attractor

A strange attractor with radial symmetry overlay and stipple texture.

```json
{
  "composition": [
    {
      "primitive": "strangeAttractor",
      "params": {
        "cx": 0, "cy": 0, "type": "aizawa", "iterations": 3000,
        "scale": 30, "palette": "plasma", "brushSize": 2, "timeStep": 0.008
      }
    },
    {
      "primitive": "stipple",
      "params": {
        "cx": 0, "cy": 0, "width": 300, "height": 300,
        "density": 0.3, "color": "#ffffff", "brushSize": 2, "dotCount": 40
      }
    },
    {
      "primitive": "sacredGeometry",
      "params": {
        "cx": 0, "cy": 0, "radius": 180, "pattern": "flowerOfLife",
        "color": "#ffffff", "brushSize": 1, "opacity": 0.2
      }
    }
  ],
  "symmetry": "radial:6"
}
```

## 4. Botanical Study

A flower with surrounding vines and leaf details, framed by a decorative border.

```json
{
  "composition": [
    {
      "primitive": "border",
      "params": {
        "cx": 0, "cy": 0, "width": 350, "height": 350,
        "pattern": "waves", "color": "#5a8a5a", "brushSize": 3, "amplitude": 6
      }
    },
    {
      "primitive": "flower",
      "params": {
        "cx": 0, "cy": -20, "petals": 10, "petalLength": 50, "petalWidth": 20,
        "centerRadius": 15, "petalColor": "#e74c3c", "centerColor": "#f39c12", "brushSize": 5
      }
    },
    {
      "primitive": "vine",
      "params": {
        "startX": -120, "startY": 80, "endX": 120, "endY": 80,
        "curveAmount": 40, "leafCount": 8, "color": "#27ae60", "brushSize": 3
      }
    },
    {
      "primitive": "leaf",
      "params": {
        "cx": -80, "cy": 20, "length": 40, "width": 15,
        "rotation": -30, "color": "#2ecc71", "brushSize": 2, "veinCount": 3
      }
    },
    {
      "primitive": "leaf",
      "params": {
        "cx": 80, "cy": 20, "length": 40, "width": 15,
        "rotation": 210, "color": "#2ecc71", "brushSize": 2, "veinCount": 3
      }
    },
    {
      "primitive": "strokeText",
      "params": {
        "cx": 0, "cy": 140, "text": "FLORA", "charHeight": 20,
        "color": "#5a8a5a", "brushSize": 2
      }
    }
  ],
  "symmetry": "none"
}
```
