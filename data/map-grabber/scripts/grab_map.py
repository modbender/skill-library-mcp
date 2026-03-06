#!/usr/bin/env python3
"""
Fetch OpenStreetMap vector data for an address: street network and/or building footprints.
Export to SVG (for illustration) and GeoPackage; optional DXF via ezdxf.
"""
import argparse
import sys

try:
    import osmnx as ox
except ImportError:
    print("Error: osmnx is required. Install with: pip install osmnx", file=sys.stderr)
    sys.exit(1)


def grab_and_export(address: str, dist: int, buildings: bool, out_svg: str, out_png: str, out_gpkg: str, out_dxf: str):
    point = ox.geocoder.geocode(address)
    if point is None:
        raise ValueError(f"Could not geocode address: {address}")
    lat, lon = point
    G = ox.graph_from_point((lat, lon), dist=dist, network_type="all")
    if out_svg:
        ox.plot_graph(G, show=False, close=True, save=True, filepath=out_svg)
        print(f"SVG saved: {out_svg}")
    if out_png:
        ox.plot_graph(G, show=False, close=True, save=True, filepath=out_png)
        print(f"PNG saved: {out_png}")
    nodes_gdf, edges_gdf = ox.graph_to_gdfs(G)
    buildings_gdf = None
    if buildings:
        try:
            tags = {"building": True}
            b = ox.features_from_point((lat, lon), tags=tags, dist=dist)
            if b is not None and len(b) > 0:
                buildings_gdf = b
        except Exception:
            pass
    if out_gpkg:
        edges_gdf.to_file(out_gpkg, driver="GPKG", layer="streets")
        if buildings_gdf is not None:
            base = out_gpkg.rsplit(".", 1)[0] if "." in out_gpkg else out_gpkg
            bpath = base + "_buildings.gpkg"
            buildings_gdf.to_file(bpath, driver="GPKG")
            print(f"GeoPackage (buildings) saved: {bpath}")
        print(f"GeoPackage (streets) saved: {out_gpkg}")
    if out_dxf:
        __export_dxf(edges_gdf, buildings_gdf, out_dxf)
        print(f"DXF saved: {out_dxf}")


def __export_dxf(edges_gdf, buildings_gdf, path: str):
    try:
        import ezdxf
    except ImportError:
        print("Warning: ezdxf not installed; skip DXF. pip install ezdxf", file=sys.stderr)
        return
    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()
    for gdf in [edges_gdf, buildings_gdf]:
        if gdf is None or len(gdf) == 0:
            continue
        gdf = gdf.to_crs("EPSG:3857")
        for _, row in gdf.iterrows():
            _add_geom_to_dxf(msp, row.geometry)
    doc.saveas(path)


def _add_geom_to_dxf(msp, geom):
    if geom is None:
        return
    if geom.geom_type == "LineString":
        coords = [(p[0], p[1]) for p in geom.coords]
        if len(coords) >= 2:
            msp.add_lwpolyline(coords, close=False)
    elif geom.geom_type == "Polygon":
        coords = [(p[0], p[1]) for p in geom.exterior.coords]
        if len(coords) >= 2:
            msp.add_lwpolyline(coords, close=True)
    elif geom.geom_type == "MultiLineString":
        for part in geom.geoms:
            coords = [(p[0], p[1]) for p in part.coords]
            if len(coords) >= 2:
                msp.add_lwpolyline(coords, close=False)
    elif geom.geom_type == "MultiPolygon":
        for poly in geom.geoms:
            coords = [(p[0], p[1]) for p in poly.exterior.coords]
            if len(coords) >= 2:
                msp.add_lwpolyline(coords, close=True)


def main():
    parser = argparse.ArgumentParser(description="Grab OSM vector data for an address; export SVG/GPKG/DXF.")
    parser.add_argument("address", help="Address or place name to center the map")
    parser.add_argument("--dist", type=int, default=500, help="Radius in meters (default 500)")
    parser.add_argument("--buildings", action="store_true", help="Include building footprints")
    parser.add_argument("--svg", default="", help="Output SVG path")
    parser.add_argument("--png", default="", help="Output PNG path (e.g. for Telegram)")
    parser.add_argument("--gpkg", default="", help="Output GeoPackage path")
    parser.add_argument("--dxf", default="", help="Output DXF path (requires ezdxf)")
    args = parser.parse_args()
    if not args.svg and not args.png and not args.gpkg and not args.dxf:
        parser.error("At least one of --svg, --png, --gpkg, --dxf is required")
    try:
        grab_and_export(
            args.address,
            args.dist,
            args.buildings,
            args.svg or None,
            args.png or None,
            args.gpkg or None,
            args.dxf or None,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
