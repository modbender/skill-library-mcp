#!/usr/bin/env python3
"""
3D 모델 → 2D 스프라이트 시트 렌더링
사용법:
  blender -b character.blend --python render_sprite_sheet.py -- \
    --angles 8 --size 128 --output sprites/character.png

  blender -b --python render_sprite_sheet.py -- \
    --import model.glb --angles 8 --size 128 --camera-angle 30 --output sheet.png

  blender -b character.blend --python render_sprite_sheet.py -- \
    --angles 4 --size 64 --animated --frame-start 1 --frame-end 24 --output anim_sheet.png
"""

import bpy
import sys
import os
import math
import argparse
from mathutils import Vector


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description='Sprite Sheet Renderer')
    parser.add_argument('--import', dest='import_file', type=str,
                        help='Import a 3D file before rendering')
    parser.add_argument('--angles', type=int, default=8,
                        help='Number of rotation angles (4, 8, 16)')
    parser.add_argument('--size', type=int, default=128,
                        help='Sprite size in pixels (square)')
    parser.add_argument('--width', type=int, default=None,
                        help='Sprite width (overrides --size)')
    parser.add_argument('--height', type=int, default=None,
                        help='Sprite height (overrides --size)')
    parser.add_argument('--camera-angle', type=float, default=30.0,
                        help='Camera elevation angle in degrees (0=side, 90=top)')
    parser.add_argument('--camera-distance', type=float, default=0,
                        help='Camera distance (0=auto)')
    parser.add_argument('--ortho-scale', type=float, default=0,
                        help='Orthographic scale (0=auto)')
    parser.add_argument('--output', type=str, default='sprite_sheet.png',
                        help='Output sprite sheet path')
    parser.add_argument('--output-dir', type=str, default='',
                        help='Output individual frames to directory (instead of sheet)')
    # Animation
    parser.add_argument('--animated', action='store_true',
                        help='Render animation frames')
    parser.add_argument('--frame-start', type=int, default=1)
    parser.add_argument('--frame-end', type=int, default=0,
                        help='End frame (0=use scene setting)')
    parser.add_argument('--frame-step', type=int, default=1)
    # Render
    parser.add_argument('--engine', type=str, default='CYCLES',
                        choices=['CYCLES', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'])
    parser.add_argument('--samples', type=int, default=32)
    parser.add_argument('--outline', action='store_true',
                        help='Add Freestyle outline')
    parser.add_argument('--outline-thickness', type=float, default=1.5)
    return parser.parse_args(argv)


def get_scene_bounds():
    """씬의 모든 메시 오브젝트의 바운딩 박스 계산"""
    min_co = Vector((float('inf'), float('inf'), float('inf')))
    max_co = Vector((float('-inf'), float('-inf'), float('-inf')))

    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for corner in obj.bound_box:
                world_co = obj.matrix_world @ Vector(corner)
                min_co.x = min(min_co.x, world_co.x)
                min_co.y = min(min_co.y, world_co.y)
                min_co.z = min(min_co.z, world_co.z)
                max_co.x = max(max_co.x, world_co.x)
                max_co.y = max(max_co.y, world_co.y)
                max_co.z = max(max_co.z, world_co.z)

    if min_co.x == float('inf'):
        return Vector((0, 0, 0)), Vector((1, 1, 1))

    return min_co, max_co


def setup_camera(elevation_deg, ortho_scale=0, distance=0):
    """직교 카메라 설정"""
    # 기존 카메라 제거
    for obj in list(bpy.data.objects):
        if obj.type == 'CAMERA':
            bpy.data.objects.remove(obj, do_unlink=True)

    cam_data = bpy.data.cameras.new('SpriteCam')
    cam_data.type = 'ORTHO'

    cam_obj = bpy.data.objects.new('SpriteCam', cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # 바운딩 박스로 자동 스케일
    min_co, max_co = get_scene_bounds()
    center = (min_co + max_co) / 2
    size = max_co - min_co
    max_dim = max(size.x, size.y, size.z)

    if ortho_scale <= 0:
        cam_data.ortho_scale = max_dim * 1.3  # 여유 마진
    else:
        cam_data.ortho_scale = ortho_scale

    auto_distance = max_dim * 3 if distance <= 0 else distance

    return cam_obj, center, auto_distance


def position_camera(cam_obj, target, distance, yaw_deg, pitch_deg):
    """카메라 궤도 위치 설정"""
    yaw = math.radians(yaw_deg)
    pitch = math.radians(pitch_deg)

    x = distance * math.cos(pitch) * math.sin(yaw)
    y = -distance * math.cos(pitch) * math.cos(yaw)
    z = distance * math.sin(pitch) + target.z

    cam_obj.location = Vector((target.x + x, target.y + y, z))

    direction = target - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()


def setup_render(width, height, engine, samples):
    """렌더 설정"""
    scene = bpy.context.scene
    scene.render.engine = engine
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.compression = 15

    if engine == 'CYCLES':
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True
        scene.cycles.max_bounces = 4

    return scene


def setup_lighting():
    """3점 조명 설정"""
    for obj in list(bpy.data.objects):
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)

    # Key light
    key_data = bpy.data.lights.new('Key', 'SUN')
    key_data.energy = 3.0
    key_obj = bpy.data.objects.new('Key', key_data)
    bpy.context.collection.objects.link(key_obj)
    key_obj.rotation_euler = (math.radians(50), 0, math.radians(30))

    # Fill light
    fill_data = bpy.data.lights.new('Fill', 'SUN')
    fill_data.energy = 1.0
    fill_obj = bpy.data.objects.new('Fill', fill_data)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = (math.radians(40), 0, math.radians(-60))


def setup_outline(thickness):
    """Freestyle 외곽선"""
    view_layer = bpy.context.view_layer
    view_layer.use_freestyle = True
    fs = view_layer.freestyle_settings
    if len(fs.linesets) == 0:
        fs.linesets.new('Outline')
    ls = fs.linesets[0]
    ls.select_silhouette = True
    ls.select_border = True
    ls.select_crease = True
    ls.linestyle.thickness = thickness
    ls.linestyle.color = (0, 0, 0)


def render_frames(cam_obj, target, distance, args):
    """프레임 렌더링 및 이미지 수집"""
    scene = bpy.context.scene
    angles = [i * (360.0 / args.angles) for i in range(args.angles)]
    direction_names = [f'{int(a):03d}' for a in angles]

    # 프레임 범위
    if args.animated:
        frame_start = args.frame_start
        frame_end = args.frame_end if args.frame_end > 0 else scene.frame_end
        frames = list(range(frame_start, frame_end + 1, args.frame_step))
    else:
        frames = [scene.frame_current]

    # 임시 디렉토리
    import tempfile
    temp_dir = args.output_dir if args.output_dir else tempfile.mkdtemp(prefix='blender_sprites_')
    os.makedirs(temp_dir, exist_ok=True)

    rendered_files = []
    total = len(angles) * len(frames)
    count = 0

    for frame in frames:
        scene.frame_set(frame)
        for angle, dir_name in zip(angles, direction_names):
            position_camera(cam_obj, target, distance, angle, args.camera_angle)

            filename = f'sprite_a{dir_name}_f{frame:04d}.png'
            filepath = os.path.join(temp_dir, filename)
            scene.render.filepath = os.path.splitext(filepath)[0]
            bpy.ops.render.render(write_still=True)

            rendered_files.append(filepath)
            count += 1
            print(f"Progress: {count}/{total} ({filename})")

    return rendered_files, temp_dir, len(angles), len(frames)


def create_sprite_sheet(image_files, output_path, sprite_w, sprite_h, cols, rows):
    """개별 이미지를 스프라이트 시트로 합치기"""
    sheet_w = cols * sprite_w
    sheet_h = rows * sprite_h

    # 스프라이트 시트 이미지 생성
    sheet = bpy.data.images.new('SpriteSheet', width=sheet_w, height=sheet_h, alpha=True)
    pixels = [0.0] * (sheet_w * sheet_h * 4)

    for idx, img_path in enumerate(image_files):
        if not os.path.exists(img_path):
            print(f"Warning: {img_path} not found")
            continue

        col = idx % cols
        row = idx // cols

        img = bpy.data.images.load(img_path)

        # 리사이즈 (필요시)
        if img.size[0] != sprite_w or img.size[1] != sprite_h:
            img.scale(sprite_w, sprite_h)

        img_pixels = list(img.pixels)

        # Bottom-left 원점 기준으로 올바른 위치에 복사
        y_offset = (rows - 1 - row) * sprite_h
        x_offset = col * sprite_w

        for py in range(sprite_h):
            for px in range(sprite_w):
                src_idx = (py * sprite_w + px) * 4
                dst_idx = ((y_offset + py) * sheet_w + (x_offset + px)) * 4
                if src_idx + 3 < len(img_pixels) and dst_idx + 3 < len(pixels):
                    for c in range(4):
                        pixels[dst_idx + c] = img_pixels[src_idx + c]

        bpy.data.images.remove(img)

    sheet.pixels = pixels
    sheet.filepath_raw = os.path.abspath(output_path)
    sheet.file_format = 'PNG'
    sheet.save()
    print(f"\nSprite sheet saved: {output_path} ({sheet_w}x{sheet_h}, {cols}x{rows} grid)")


def main():
    args = parse_args()

    sprite_w = args.width or args.size
    sprite_h = args.height or args.size

    # 파일 임포트 (선택적)
    if args.import_file:
        ext = os.path.splitext(args.import_file)[1].lower()
        if ext == '.fbx':
            bpy.ops.import_scene.fbx(filepath=args.import_file, automatic_bone_orientation=True)
        elif ext in ('.gltf', '.glb'):
            bpy.ops.import_scene.gltf(filepath=args.import_file)
        elif ext == '.obj':
            bpy.ops.wm.obj_import(filepath=args.import_file)
        print(f"Imported: {args.import_file}")

    # 설정
    setup_render(sprite_w, sprite_h, args.engine, args.samples)
    setup_lighting()
    cam_obj, center, distance = setup_camera(
        args.camera_angle, args.ortho_scale, args.camera_distance
    )

    if args.outline:
        setup_outline(args.outline_thickness)

    # 렌더링
    rendered_files, temp_dir, num_angles, num_frames = render_frames(
        cam_obj, center, distance, args
    )

    # 스프라이트 시트 생성 (output_dir이 없을 때만)
    if not args.output_dir:
        cols = num_angles
        rows = num_frames
        os.makedirs(os.path.dirname(os.path.abspath(args.output)) or '.', exist_ok=True)
        create_sprite_sheet(rendered_files, args.output, sprite_w, sprite_h, cols, rows)

        # 임시 파일 정리
        import shutil
        if temp_dir and os.path.exists(temp_dir) and temp_dir.startswith('/tmp'):
            shutil.rmtree(temp_dir)
    else:
        print(f"\nIndividual frames saved to: {args.output_dir}")

    print("Done!")


if __name__ == '__main__':
    main()
