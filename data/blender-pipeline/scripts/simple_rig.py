#!/usr/bin/env python3
"""
간단한 자동 리깅 스크립트
사용법:
  blender -b character.blend --python simple_rig.py -- \
    --target CharacterMesh --type rigify --output rigged.blend

  blender -b character.blend --python simple_rig.py -- \
    --target CharacterMesh --type simple --output rigged.blend
"""

import bpy
import sys
import os
import argparse
from mathutils import Vector


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description='Simple Auto-Rig')
    parser.add_argument('--target', type=str, default='',
                        help='Target mesh object name (empty=auto-detect)')
    parser.add_argument('--type', type=str, default='rigify',
                        choices=['rigify', 'simple', 'basic-biped'],
                        help='Rig type')
    parser.add_argument('--output', type=str, default='rigged.blend',
                        help='Output file path')
    parser.add_argument('--output-format', type=str, default='BLEND',
                        choices=['BLEND', 'FBX', 'GLB'],
                        help='Output format')
    parser.add_argument('--auto-weights', action='store_true', default=True,
                        help='Auto weight painting')
    parser.add_argument('--scale', type=float, default=1.0,
                        help='Rig scale factor')
    return parser.parse_args(argv)


def find_target_mesh(name=''):
    """대상 메시 오브젝트 찾기"""
    if name:
        obj = bpy.data.objects.get(name)
        if obj and obj.type == 'MESH':
            return obj
        print(f"Warning: '{name}' not found or not a mesh")

    # 자동 감지: 가장 폴리곤 수가 많은 메시
    meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    if not meshes:
        print("Error: No mesh objects in scene")
        return None

    meshes.sort(key=lambda o: len(o.data.polygons), reverse=True)
    target = meshes[0]
    print(f"Auto-detected target mesh: {target.name} ({len(target.data.polygons)} polys)")
    return target


def get_mesh_dimensions(mesh_obj):
    """메시의 월드 바운딩 박스 치수"""
    bbox = [mesh_obj.matrix_world @ Vector(corner) for corner in mesh_obj.bound_box]
    min_z = min(v.z for v in bbox)
    max_z = max(v.z for v in bbox)
    min_x = min(v.x for v in bbox)
    max_x = max(v.x for v in bbox)
    center_x = (min_x + max_x) / 2
    height = max_z - min_z
    return {
        'height': height,
        'min_z': min_z,
        'max_z': max_z,
        'center_x': center_x,
        'width': max_x - min_x,
    }


def create_rigify_rig(mesh_obj, scale=1.0):
    """Rigify 메타리그 기반 자동 리깅"""
    # Rigify 활성화
    bpy.ops.preferences.addon_enable(module='rigify')

    dims = get_mesh_dimensions(mesh_obj)
    h = dims['height'] * scale

    # 휴머노이드 메타리그 추가
    bpy.ops.object.armature_human_metarig_add()
    metarig = bpy.context.active_object
    metarig.name = 'metarig'

    # 메타리그를 메시 크기에 맞게 스케일
    # 기본 메타리그 높이 ~1.7m
    default_height = 1.7
    scale_factor = h / default_height if h > 0 else 1.0
    metarig.scale = (scale_factor, scale_factor, scale_factor)
    bpy.ops.object.transform_apply(scale=True)

    # 메타리그 위치를 메시 바닥에 맞춤
    metarig.location.z = dims['min_z']
    metarig.location.x = dims['center_x']

    # 리그 생성
    bpy.context.view_layer.objects.active = metarig
    try:
        bpy.ops.pose.rigify_generate()
        print("Rigify rig generated successfully")
    except Exception as e:
        print(f"Rigify generation failed: {e}")
        print("Falling back to simple rig")
        return create_simple_rig(mesh_obj, scale)

    rig = bpy.data.objects.get('rig')
    if not rig:
        print("Warning: Generated rig not found")
        return metarig

    return rig


def create_simple_rig(mesh_obj, scale=1.0):
    """심플 본 리그 (기본 바이페드)"""
    dims = get_mesh_dimensions(mesh_obj)
    h = dims['height']
    base_z = dims['min_z']
    cx = dims['center_x']

    # 비율 계산
    hip_z = base_z + h * 0.45
    spine_z = base_z + h * 0.55
    chest_z = base_z + h * 0.7
    neck_z = base_z + h * 0.82
    head_z = base_z + h * 0.88
    head_top = base_z + h * 1.0

    shoulder_w = dims['width'] * 0.35
    hip_w = dims['width'] * 0.15

    # 아마추어 생성
    arm_data = bpy.data.armatures.new('SimpleRig')
    arm_data.display_type = 'OCTAHEDRAL'
    arm_obj = bpy.data.objects.new('SimpleRig', arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj

    bpy.ops.object.mode_set(mode='EDIT')

    bones = {}

    def add_bone(name, head, tail, parent_name=None):
        bone = arm_data.edit_bones.new(name)
        bone.head = Vector(head)
        bone.tail = Vector(tail)
        if parent_name and parent_name in bones:
            bone.parent = bones[parent_name]
            bone.use_connect = (bone.head - bones[parent_name].tail).length < 0.01
        bones[name] = bone
        return bone

    # Spine chain
    add_bone('root', (cx, 0, base_z), (cx, 0, base_z + 0.1))
    add_bone('spine', (cx, 0, hip_z), (cx, 0, spine_z), 'root')
    add_bone('spine.001', (cx, 0, spine_z), (cx, 0, chest_z), 'spine')
    add_bone('spine.002', (cx, 0, chest_z), (cx, 0, neck_z), 'spine.001')
    add_bone('neck', (cx, 0, neck_z), (cx, 0, head_z), 'spine.002')
    add_bone('head', (cx, 0, head_z), (cx, 0, head_top), 'neck')

    # Left arm
    add_bone('shoulder.L', (cx + 0.05, 0, chest_z), (cx + shoulder_w * 0.5, 0, chest_z), 'spine.002')
    add_bone('upper_arm.L', (cx + shoulder_w * 0.5, 0, chest_z),
             (cx + shoulder_w, 0, spine_z), 'shoulder.L')
    add_bone('forearm.L', (cx + shoulder_w, 0, spine_z),
             (cx + shoulder_w * 1.3, 0, hip_z), 'upper_arm.L')
    add_bone('hand.L', (cx + shoulder_w * 1.3, 0, hip_z),
             (cx + shoulder_w * 1.4, 0, hip_z - 0.05), 'forearm.L')

    # Right arm (mirrored)
    add_bone('shoulder.R', (cx - 0.05, 0, chest_z), (cx - shoulder_w * 0.5, 0, chest_z), 'spine.002')
    add_bone('upper_arm.R', (cx - shoulder_w * 0.5, 0, chest_z),
             (cx - shoulder_w, 0, spine_z), 'shoulder.R')
    add_bone('forearm.R', (cx - shoulder_w, 0, spine_z),
             (cx - shoulder_w * 1.3, 0, hip_z), 'upper_arm.R')
    add_bone('hand.R', (cx - shoulder_w * 1.3, 0, hip_z),
             (cx - shoulder_w * 1.4, 0, hip_z - 0.05), 'forearm.R')

    # Left leg
    add_bone('thigh.L', (cx + hip_w, 0, hip_z),
             (cx + hip_w, 0, hip_z - h * 0.22), 'root')
    add_bone('shin.L', (cx + hip_w, 0, hip_z - h * 0.22),
             (cx + hip_w, 0, base_z + 0.05), 'thigh.L')
    add_bone('foot.L', (cx + hip_w, 0, base_z + 0.05),
             (cx + hip_w, -0.08, base_z), 'shin.L')

    # Right leg (mirrored)
    add_bone('thigh.R', (cx - hip_w, 0, hip_z),
             (cx - hip_w, 0, hip_z - h * 0.22), 'root')
    add_bone('shin.R', (cx - hip_w, 0, hip_z - h * 0.22),
             (cx - hip_w, 0, base_z + 0.05), 'thigh.R')
    add_bone('foot.R', (cx - hip_w, 0, base_z + 0.05),
             (cx - hip_w, -0.08, base_z), 'foot.L'.replace('.L', '.R'))  # parent fix
    # Fix foot.R parent
    bones['foot.R'].parent = bones['shin.R']

    bpy.ops.object.mode_set(mode='OBJECT')

    print(f"Simple rig created with {len(bones)} bones")
    return arm_obj


def bind_mesh_to_rig(mesh_obj, rig_obj, auto_weights=True):
    """메시를 리그에 바인딩"""
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    rig_obj.select_set(True)
    bpy.context.view_layer.objects.active = rig_obj

    if auto_weights:
        try:
            bpy.ops.object.parent_set(type='ARMATURE_AUTO')
            print("Auto weight painting applied")
        except Exception as e:
            print(f"Auto weights failed ({e}), using envelope weights")
            bpy.ops.object.parent_set(type='ARMATURE_ENVELOPE')
    else:
        bpy.ops.object.parent_set(type='ARMATURE_NAME')
        print("Mesh bound to rig (manual weight painting needed)")


def export_result(filepath, fmt):
    os.makedirs(os.path.dirname(os.path.abspath(filepath)) or '.', exist_ok=True)

    if fmt == 'BLEND':
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(filepath))
    elif fmt == 'FBX':
        bpy.ops.export_scene.fbx(
            filepath=filepath,
            use_selection=False,
            use_mesh_modifiers=True,
            add_leaf_bones=False,
            bake_anim=True,
            primary_bone_axis='Y',
            secondary_bone_axis='X'
        )
    elif fmt == 'GLB':
        bpy.ops.export_scene.gltf(
            filepath=filepath,
            export_format='GLB',
            export_apply=True,
            export_animations=True,
            export_skins=True
        )

    print(f"Saved: {filepath} ({fmt})")


def main():
    args = parse_args()

    # 대상 메시 찾기
    mesh_obj = find_target_mesh(args.target)
    if not mesh_obj:
        sys.exit(1)

    # 리그 생성
    print(f"\nCreating {args.type} rig for '{mesh_obj.name}'...")

    if args.type == 'rigify':
        rig_obj = create_rigify_rig(mesh_obj, args.scale)
    elif args.type in ('simple', 'basic-biped'):
        rig_obj = create_simple_rig(mesh_obj, args.scale)
    else:
        print(f"Unknown rig type: {args.type}")
        sys.exit(1)

    # 바인딩
    bind_mesh_to_rig(mesh_obj, rig_obj, args.auto_weights)

    # 저장
    export_result(args.output, args.output_format)
    print("\nRigging complete!")


if __name__ == '__main__':
    main()
