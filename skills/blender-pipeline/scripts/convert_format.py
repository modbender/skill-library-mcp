#!/usr/bin/env python3
"""
Blender 3D 포맷 변환 스크립트
사용법:
  blender -b --python convert_format.py -- --input model.fbx --output model.glb --format GLB
  blender -b --python convert_format.py -- --input-dir ./models/ --output-dir ./converted/ --input-ext .fbx --format GLB
"""

import bpy
import sys
import os
import argparse


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description='3D Format Converter')
    parser.add_argument('--input', type=str, help='Input file path')
    parser.add_argument('--output', type=str, help='Output file path')
    parser.add_argument('--format', type=str, default='GLB',
                        choices=['GLB', 'GLTF', 'FBX', 'OBJ'],
                        help='Output format')
    # Batch mode
    parser.add_argument('--input-dir', type=str, help='Input directory for batch')
    parser.add_argument('--output-dir', type=str, help='Output directory for batch')
    parser.add_argument('--input-ext', type=str, default='.fbx',
                        help='Input file extension for batch (e.g. .fbx, .obj, .gltf)')
    # Options
    parser.add_argument('--apply-modifiers', action='store_true', default=True,
                        help='Apply modifiers on export')
    parser.add_argument('--triangulate', action='store_true', default=False,
                        help='Triangulate meshes')
    parser.add_argument('--scale', type=float, default=1.0,
                        help='Global scale factor')
    return parser.parse_args(argv)


def clear_scene():
    """씬 초기화"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    # Orphan data 정리
    for block_type in [bpy.data.meshes, bpy.data.materials, bpy.data.textures,
                       bpy.data.images, bpy.data.armatures, bpy.data.actions]:
        for block in block_type:
            if block.users == 0:
                block_type.remove(block)


def import_file(filepath):
    """파일 형식에 따라 임포트"""
    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.fbx':
        bpy.ops.import_scene.fbx(
            filepath=filepath,
            use_custom_normals=True,
            use_image_search=True,
            automatic_bone_orientation=True,
            ignore_leaf_bones=True
        )
    elif ext in ('.gltf', '.glb'):
        bpy.ops.import_scene.gltf(
            filepath=filepath,
            import_shading='NORMALS',
            merge_vertices=False
        )
    elif ext == '.obj':
        bpy.ops.wm.obj_import(filepath=filepath)
    elif ext == '.blend':
        bpy.ops.wm.open_mainfile(filepath=filepath)
    else:
        print(f"Unsupported import format: {ext}")
        return False

    print(f"Imported: {filepath}")
    return True


def export_file(filepath, fmt, apply_modifiers=True, triangulate=False, scale=1.0):
    """지정 형식으로 익스포트"""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    # 삼각화 옵션
    if triangulate:
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                mod = obj.modifiers.new('Triangulate', 'TRIANGULATE')
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.modifier_apply(modifier='Triangulate')

    if fmt in ('GLB', 'GLTF'):
        export_format = 'GLB' if fmt == 'GLB' else 'GLTF_SEPARATE'
        bpy.ops.export_scene.gltf(
            filepath=filepath,
            export_format=export_format,
            use_selection=False,
            export_apply=apply_modifiers,
            export_animations=True,
            export_skins=True,
            export_morph=True,
            export_lights=False,
            export_cameras=False,
            export_image_format='AUTO'
        )
    elif fmt == 'FBX':
        bpy.ops.export_scene.fbx(
            filepath=filepath,
            use_selection=False,
            global_scale=scale,
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_NONE',
            use_mesh_modifiers=apply_modifiers,
            add_leaf_bones=False,
            bake_anim=True,
            bake_anim_use_all_bones=True,
            bake_anim_use_nla_strips=True,
            bake_anim_use_all_actions=True
        )
    elif fmt == 'OBJ':
        bpy.ops.wm.obj_export(
            filepath=filepath,
            export_selected_objects=False,
            export_uv=True,
            export_normals=True,
            export_materials=True,
            apply_modifiers=apply_modifiers
        )
    else:
        print(f"Unsupported export format: {fmt}")
        return False

    print(f"Exported: {filepath} ({fmt})")
    return True


def get_output_ext(fmt):
    """포맷에 따른 확장자"""
    return {
        'GLB': '.glb',
        'GLTF': '.gltf',
        'FBX': '.fbx',
        'OBJ': '.obj',
    }.get(fmt, '.glb')


def convert_single(input_path, output_path, fmt, apply_modifiers, triangulate, scale):
    """단일 파일 변환"""
    clear_scene()
    if not import_file(input_path):
        return False

    # 스케일 적용
    if scale != 1.0:
        for obj in bpy.data.objects:
            obj.scale *= scale
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.transform_apply(scale=True)

    return export_file(output_path, fmt, apply_modifiers, triangulate, scale)


def convert_batch(input_dir, output_dir, input_ext, fmt, apply_modifiers, triangulate, scale):
    """배치 변환"""
    os.makedirs(output_dir, exist_ok=True)
    out_ext = get_output_ext(fmt)

    files = sorted([
        f for f in os.listdir(input_dir)
        if f.lower().endswith(input_ext.lower())
    ])

    if not files:
        print(f"No {input_ext} files found in {input_dir}")
        return

    print(f"Converting {len(files)} files: {input_ext} → {fmt}")

    success = 0
    for f in files:
        input_path = os.path.join(input_dir, f)
        output_name = os.path.splitext(f)[0] + out_ext
        output_path = os.path.join(output_dir, output_name)

        try:
            if convert_single(input_path, output_path, fmt, apply_modifiers, triangulate, scale):
                success += 1
        except Exception as e:
            print(f"Error converting {f}: {e}")

    print(f"\nBatch complete: {success}/{len(files)} converted")


def main():
    args = parse_args()

    if args.input_dir:
        # 배치 모드
        if not args.output_dir:
            print("Error: --output-dir required for batch mode")
            sys.exit(1)
        convert_batch(
            args.input_dir, args.output_dir, args.input_ext,
            args.format, args.apply_modifiers, args.triangulate, args.scale
        )
    elif args.input:
        # 단일 파일 모드
        if not args.output:
            base = os.path.splitext(args.input)[0]
            args.output = base + get_output_ext(args.format)
        convert_single(
            args.input, args.output, args.format,
            args.apply_modifiers, args.triangulate, args.scale
        )
    else:
        print("Error: --input or --input-dir required")
        sys.exit(1)


if __name__ == '__main__':
    main()
