#!/usr/bin/env python3
"""
프로시저럴 게임 소품 생성
사용법:
  blender -b --python procedural_props.py -- --type tree --style low-poly --seed 42 --output tree.glb
  blender -b --python procedural_props.py -- --type rock --count 5 --output rocks.glb
  blender -b --python procedural_props.py -- --type crate --style wooden --output crate.glb
  blender -b --python procedural_props.py -- --type building --floors 3 --output building.glb
"""

import bpy
import bmesh
import sys
import os
import math
import random
import argparse
from mathutils import Vector


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description='Procedural Props Generator')
    parser.add_argument('--type', type=str, required=True,
                        choices=['tree', 'rock', 'crate', 'building', 'barrel',
                                 'fence', 'lamp', 'crystal', 'mushroom'],
                        help='Asset type to generate')
    parser.add_argument('--style', type=str, default='low-poly',
                        choices=['low-poly', 'wooden', 'stone', 'metal', 'medieval',
                                 'modern', 'fantasy'],
                        help='Visual style')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--count', type=int, default=1,
                        help='Number of variants to generate')
    parser.add_argument('--output', type=str, default='output.glb',
                        help='Output file path')
    parser.add_argument('--format', type=str, default='GLB',
                        choices=['GLB', 'GLTF', 'FBX', 'OBJ', 'BLEND'])
    # Type-specific
    parser.add_argument('--floors', type=int, default=2, help='Building floors')
    parser.add_argument('--size', type=float, default=1.0, help='Base size')
    return parser.parse_args(argv)


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for dt in [bpy.data.meshes, bpy.data.materials, bpy.data.textures,
               bpy.data.images, bpy.data.armatures]:
        for block in dt:
            if block.users == 0:
                dt.remove(block)


def create_material(name, color, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
    return mat


def assign_material(obj, mat):
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


# ========== GENERATORS ==========

def generate_tree(seed=42, size=1.0):
    random.seed(seed)

    trunk_h = size * (1.5 + random.uniform(0, 1.0))
    trunk_r = size * 0.12

    # Trunk
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=6, radius=trunk_r, depth=trunk_h,
        location=(0, 0, trunk_h / 2)
    )
    trunk = bpy.context.active_object
    trunk.name = f'Tree_Trunk_{seed}'
    assign_material(trunk, create_material(f'Bark_{seed}', (0.35, 0.2, 0.1)))

    # Deform trunk
    bm = bmesh.new()
    bm.from_mesh(trunk.data)
    for v in bm.verts:
        if v.co.z > 0.2:
            v.co.x += random.uniform(-0.03, 0.03) * size
            v.co.y += random.uniform(-0.03, 0.03) * size
    bm.to_mesh(trunk.data)
    bm.free()

    # Crown (1-3 spheres)
    crown_count = random.randint(1, 3)
    crown_objects = [trunk]

    for i in range(crown_count):
        r = size * random.uniform(0.6, 1.0)
        z_off = trunk_h + random.uniform(-0.2, 0.5) * size
        x_off = random.uniform(-0.3, 0.3) * size if i > 0 else 0
        y_off = random.uniform(-0.3, 0.3) * size if i > 0 else 0

        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2, radius=r,
            location=(x_off, y_off, z_off)
        )
        crown = bpy.context.active_object
        crown.name = f'Tree_Crown_{seed}_{i}'

        # Deform crown
        bm = bmesh.new()
        bm.from_mesh(crown.data)
        for v in bm.verts:
            noise = random.uniform(-0.2, 0.2) * size
            v.co += v.co.normalized() * noise
            if v.co.z < -r * 0.3:
                v.co.x *= 0.5
                v.co.y *= 0.5
        for face in bm.faces:
            face.smooth = False
        bm.to_mesh(crown.data)
        bm.free()

        green = (
            0.1 + random.uniform(0, 0.1),
            0.35 + random.uniform(0, 0.2),
            0.05 + random.uniform(0, 0.1)
        )
        assign_material(crown, create_material(f'Leaf_{seed}_{i}', green))
        crown_objects.append(crown)

    # Join
    bpy.ops.object.select_all(action='DESELECT')
    for obj in crown_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = crown_objects[0]
    bpy.ops.object.join()

    result = bpy.context.active_object
    result.name = f'Tree_{seed}'
    return result


def generate_rock(seed=42, size=1.0):
    random.seed(seed)

    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2, radius=size, location=(0, 0, 0)
    )
    rock = bpy.context.active_object
    rock.name = f'Rock_{seed}'

    # Stretch
    rock.scale.x *= random.uniform(0.7, 1.3)
    rock.scale.y *= random.uniform(0.7, 1.3)
    rock.scale.z *= random.uniform(0.5, 0.9)
    bpy.ops.object.transform_apply(scale=True)

    bm = bmesh.new()
    bm.from_mesh(rock.data)
    for v in bm.verts:
        displacement = random.uniform(-0.3, 0.3) * size
        v.co += v.co.normalized() * displacement
        if v.co.z < -size * 0.2:
            v.co.z = -size * 0.2 + random.uniform(-0.05, 0) * size
    for face in bm.faces:
        face.smooth = False
    bm.to_mesh(rock.data)
    bm.free()

    gray = random.uniform(0.3, 0.6)
    assign_material(rock, create_material(f'Rock_{seed}', (gray, gray * 0.95, gray * 0.9)))
    return rock


def generate_crate(seed=42, size=1.0):
    random.seed(seed)

    bpy.ops.mesh.primitive_cube_add(size=size, location=(0, 0, size / 2))
    crate = bpy.context.active_object
    crate.name = f'Crate_{seed}'

    # Slight irregularity
    bm = bmesh.new()
    bm.from_mesh(crate.data)
    for v in bm.verts:
        v.co.x += random.uniform(-0.01, 0.01) * size
        v.co.y += random.uniform(-0.01, 0.01) * size
    for face in bm.faces:
        face.smooth = False
    bm.to_mesh(crate.data)
    bm.free()

    # Bevel edges
    mod = crate.modifiers.new('Bevel', 'BEVEL')
    mod.width = 0.02 * size
    mod.segments = 1
    bpy.context.view_layer.objects.active = crate
    bpy.ops.object.modifier_apply(modifier='Bevel')

    assign_material(crate, create_material(f'Wood_{seed}', (0.55, 0.35, 0.15)))
    return crate


def generate_barrel(seed=42, size=1.0):
    random.seed(seed)

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12, radius=size * 0.4, depth=size * 1.0,
        location=(0, 0, size * 0.5)
    )
    barrel = bpy.context.active_object
    barrel.name = f'Barrel_{seed}'

    # Bulge middle
    bm = bmesh.new()
    bm.from_mesh(barrel.data)
    center_z = size * 0.5
    for v in bm.verts:
        dist = abs(v.co.z - center_z) / (size * 0.5)
        bulge = 1.0 + 0.15 * (1.0 - dist * dist)
        v.co.x *= bulge
        v.co.y *= bulge
    for face in bm.faces:
        face.smooth = False
    bm.to_mesh(barrel.data)
    bm.free()

    assign_material(barrel, create_material(f'Barrel_{seed}', (0.5, 0.3, 0.12)))
    return barrel


def generate_building(seed=42, size=1.0, floors=2):
    random.seed(seed)

    w = size * (2.0 + random.uniform(0, 2.0))
    d = size * (1.5 + random.uniform(0, 1.5))
    floor_h = size * 2.5
    total_h = floor_h * floors

    # Main body
    bpy.ops.mesh.primitive_cube_add(
        size=1, location=(0, 0, total_h / 2)
    )
    building = bpy.context.active_object
    building.name = f'Building_{seed}'
    building.scale = (w / 2, d / 2, total_h / 2)
    bpy.ops.object.transform_apply(scale=True)

    assign_material(building, create_material(f'Wall_{seed}',
        (0.85 + random.uniform(-0.1, 0), 0.82 + random.uniform(-0.1, 0), 0.75)))

    # Roof
    roof_h = size * 1.0
    bm = bmesh.new()
    hw, hd = w / 2, d / 2
    v1 = bm.verts.new((-hw, -hd, total_h))
    v2 = bm.verts.new((hw, -hd, total_h))
    v3 = bm.verts.new((hw, hd, total_h))
    v4 = bm.verts.new((-hw, hd, total_h))
    v5 = bm.verts.new((0, -hd, total_h + roof_h))
    v6 = bm.verts.new((0, hd, total_h + roof_h))

    bm.faces.new((v1, v2, v5))
    bm.faces.new((v3, v4, v6))
    bm.faces.new((v1, v4, v6, v5))
    bm.faces.new((v2, v3, v6, v5))

    roof_mesh = bpy.data.meshes.new(f'Roof_{seed}')
    bm.to_mesh(roof_mesh)
    bm.free()

    roof_obj = bpy.data.objects.new(f'Roof_{seed}', roof_mesh)
    bpy.context.collection.objects.link(roof_obj)
    assign_material(roof_obj, create_material(f'Roof_{seed}',
        (0.55 + random.uniform(-0.1, 0.1), 0.15, 0.1)))

    # Join
    bpy.ops.object.select_all(action='DESELECT')
    building.select_set(True)
    roof_obj.select_set(True)
    bpy.context.view_layer.objects.active = building
    bpy.ops.object.join()

    result = bpy.context.active_object
    result.name = f'Building_{seed}'
    return result


def generate_crystal(seed=42, size=1.0):
    random.seed(seed)

    bpy.ops.mesh.primitive_cone_add(
        vertices=random.choice([5, 6, 7, 8]),
        radius1=size * 0.3,
        radius2=0,
        depth=size * (1.0 + random.uniform(0, 1.0)),
        location=(0, 0, size * 0.5)
    )
    crystal = bpy.context.active_object
    crystal.name = f'Crystal_{seed}'

    # Random tilt
    crystal.rotation_euler.x = random.uniform(-0.2, 0.2)
    crystal.rotation_euler.y = random.uniform(-0.2, 0.2)

    color = random.choice([
        (0.3, 0.6, 0.9),   # Blue
        (0.8, 0.2, 0.8),   # Purple
        (0.2, 0.9, 0.5),   # Green
        (0.9, 0.3, 0.2),   # Red
    ])
    mat = create_material(f'Crystal_{seed}', color, roughness=0.2, metallic=0.1)
    assign_material(crystal, mat)

    return crystal


def generate_mushroom(seed=42, size=1.0):
    random.seed(seed)

    # Stem
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=size * 0.1,
        depth=size * 0.5,
        location=(0, 0, size * 0.25)
    )
    stem = bpy.context.active_object
    stem.name = f'Mushroom_Stem_{seed}'
    assign_material(stem, create_material(f'Stem_{seed}', (0.9, 0.85, 0.7)))

    # Cap
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12, ring_count=6,
        radius=size * 0.35,
        location=(0, 0, size * 0.5)
    )
    cap = bpy.context.active_object
    cap.name = f'Mushroom_Cap_{seed}'
    cap.scale.z = 0.5
    bpy.ops.object.transform_apply(scale=True)

    # Remove bottom half
    bm = bmesh.new()
    bm.from_mesh(cap.data)
    verts_to_remove = [v for v in bm.verts if v.co.z < size * 0.45]
    bmesh.ops.delete(bm, geom=verts_to_remove, context='VERTS')
    for face in bm.faces:
        face.smooth = False
    bm.to_mesh(cap.data)
    bm.free()

    cap_color = random.choice([
        (0.8, 0.15, 0.1),  # Red
        (0.6, 0.4, 0.1),   # Brown
        (0.9, 0.8, 0.3),   # Yellow
    ])
    assign_material(cap, create_material(f'Cap_{seed}', cap_color))

    # Join
    bpy.ops.object.select_all(action='DESELECT')
    stem.select_set(True)
    cap.select_set(True)
    bpy.context.view_layer.objects.active = stem
    bpy.ops.object.join()

    result = bpy.context.active_object
    result.name = f'Mushroom_{seed}'
    return result


# ========== MAIN ==========

GENERATORS = {
    'tree': generate_tree,
    'rock': generate_rock,
    'crate': generate_crate,
    'barrel': generate_barrel,
    'building': generate_building,
    'crystal': generate_crystal,
    'mushroom': generate_mushroom,
}


def export_result(filepath, fmt):
    os.makedirs(os.path.dirname(os.path.abspath(filepath)) or '.', exist_ok=True)

    if fmt in ('GLB', 'GLTF'):
        export_format = 'GLB' if fmt == 'GLB' else 'GLTF_SEPARATE'
        bpy.ops.export_scene.gltf(
            filepath=filepath,
            export_format=export_format,
            use_selection=False,
            export_apply=True
        )
    elif fmt == 'FBX':
        bpy.ops.export_scene.fbx(
            filepath=filepath,
            use_selection=False,
            use_mesh_modifiers=True,
            add_leaf_bones=False
        )
    elif fmt == 'OBJ':
        bpy.ops.wm.obj_export(filepath=filepath)
    elif fmt == 'BLEND':
        bpy.ops.wm.save_as_mainfile(filepath=filepath)

    print(f"Exported: {filepath}")


def main():
    args = parse_args()
    gen_func = GENERATORS.get(args.type)

    if not gen_func:
        print(f"Unknown type: {args.type}. Available: {list(GENERATORS.keys())}")
        sys.exit(1)

    if args.count == 1:
        clear_scene()
        kwargs = {'seed': args.seed, 'size': args.size}
        if args.type == 'building':
            kwargs['floors'] = args.floors
        gen_func(**kwargs)
        export_result(args.output, args.format)
    else:
        # Multiple variants
        base, ext = os.path.splitext(args.output)
        for i in range(args.count):
            clear_scene()
            seed = args.seed + i
            kwargs = {'seed': seed, 'size': args.size}
            if args.type == 'building':
                kwargs['floors'] = args.floors

            obj = gen_func(**kwargs)

            # Space out variants
            if args.count > 1:
                obj.location.x = i * args.size * 3

            filepath = f'{base}_{seed:04d}{ext}' if args.count > 1 else args.output
            export_result(filepath, args.format)

    print(f"\nGenerated {args.count} {args.type}(s)")


if __name__ == '__main__':
    main()
