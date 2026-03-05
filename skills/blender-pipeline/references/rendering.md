# 스프라이트 시트 / 렌더링 가이드

## 3D → 2D 스프라이트 시트 워크플로우

### 개념
3D 모델을 여러 각도에서 렌더링하여 2D 스프라이트 시트를 생성.
- **탑다운**: 위에서 아래로
- **아이소메트릭**: 30~45도 각도
- **사이드뷰**: 측면
- **8방향**: 0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°

### 핵심 설정

#### 직교 카메라 (필수)
```python
import bpy
import math
from mathutils import Vector

def setup_ortho_camera(scale=5.0, elevation=30):
    """스프라이트용 직교 카메라 설정"""
    # 기존 카메라 제거
    for obj in bpy.data.objects:
        if obj.type == 'CAMERA':
            bpy.data.objects.remove(obj, do_unlink=True)

    # 새 카메라
    cam_data = bpy.data.cameras.new('SpriteCam')
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = scale

    cam_obj = bpy.data.objects.new('SpriteCam', cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    return cam_obj
```

#### 투명 배경
```python
def setup_transparent_render(width=128, height=128, samples=32):
    """스프라이트 렌더링 설정 (투명 배경)"""
    scene = bpy.context.scene

    # 렌더 엔진 (Cycles 권장, headless 호환)
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True

    # 해상도
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100

    # 투명 배경
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.compression = 15

    return scene
```

## 카메라 궤도 설정

### 방향별 카메라 위치 계산
```python
def position_camera_orbit(cam_obj, target, distance, yaw_deg, pitch_deg):
    """
    카메라를 타겟 주위로 궤도 배치
    yaw_deg: 수평 회전 (0=정면, 90=오른쪽, 180=뒤, 270=왼쪽)
    pitch_deg: 수직 각도 (0=수평, 90=위에서 아래로)
    """
    yaw = math.radians(yaw_deg)
    pitch = math.radians(pitch_deg)

    # 구면좌표 → 직교좌표
    x = distance * math.cos(pitch) * math.sin(yaw)
    y = -distance * math.cos(pitch) * math.cos(yaw)
    z = distance * math.sin(pitch)

    cam_obj.location = Vector(target) + Vector((x, y, z))

    # 타겟 바라보기
    direction = Vector(target) - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
```

### 8방향 렌더링
```python
def render_8_directions(
    cam_obj,
    target=(0, 0, 0.8),  # 캐릭터 중심
    distance=5.0,
    pitch=30,              # 아이소메트릭 각도
    output_dir='/tmp/sprites',
    prefix='char'
):
    """8방향 렌더링"""
    import os
    os.makedirs(output_dir, exist_ok=True)

    direction_names = ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE']
    angles = [0, 45, 90, 135, 180, 225, 270, 315]

    scene = bpy.context.scene

    for i, (name, angle) in enumerate(zip(direction_names, angles)):
        position_camera_orbit(cam_obj, target, distance, angle, pitch)

        # 렌더
        filepath = os.path.join(output_dir, f'{prefix}_{name}')
        scene.render.filepath = filepath
        bpy.ops.render.render(write_still=True)
        print(f"Rendered: {filepath}.png ({angle}°)")

    return output_dir
```

## 애니메이션 스프라이트 시트

### 프레임별 렌더링
```python
def render_animation_sprites(
    cam_obj,
    target=(0, 0, 0.8),
    distance=5.0,
    pitch=30,
    yaw=0,  # 단일 방향
    frame_start=1,
    frame_end=24,
    frame_step=1,
    output_dir='/tmp/sprites',
    prefix='anim'
):
    """애니메이션의 각 프레임을 렌더링"""
    import os
    os.makedirs(output_dir, exist_ok=True)

    scene = bpy.context.scene
    position_camera_orbit(cam_obj, target, distance, yaw, pitch)

    frames_rendered = []
    for frame in range(frame_start, frame_end + 1, frame_step):
        scene.frame_set(frame)

        filepath = os.path.join(output_dir, f'{prefix}_f{frame:04d}')
        scene.render.filepath = filepath
        bpy.ops.render.render(write_still=True)
        frames_rendered.append(f'{filepath}.png')
        print(f"Rendered frame {frame}")

    return frames_rendered
```

### 다방향 애니메이션 (8방향 × N프레임)
```python
def render_8dir_animation(
    cam_obj,
    target=(0, 0, 0.8),
    distance=5.0,
    pitch=30,
    frame_start=1,
    frame_end=24,
    frame_step=2,
    output_dir='/tmp/sprites',
    prefix='char'
):
    """8방향 × 전체 프레임 렌더링"""
    import os

    direction_names = ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE']
    angles = [0, 45, 90, 135, 180, 225, 270, 315]
    scene = bpy.context.scene

    for dir_name, angle in zip(direction_names, angles):
        dir_path = os.path.join(output_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)

        position_camera_orbit(cam_obj, target, distance, angle, pitch)

        for frame in range(frame_start, frame_end + 1, frame_step):
            scene.frame_set(frame)
            filepath = os.path.join(dir_path, f'{prefix}_{dir_name}_f{frame:04d}')
            scene.render.filepath = filepath
            bpy.ops.render.render(write_still=True)

    print(f"Rendered 8-dir animation: {len(direction_names)} dirs × {(frame_end - frame_start) // frame_step + 1} frames")
```

## 스프라이트 시트 합치기

### Blender 내부에서 합치기 (Compositor)
```python
def composite_sprite_sheet(
    image_dir,
    output_path,
    cols=8,
    sprite_width=128,
    sprite_height=128
):
    """개별 이미지를 스프라이트 시트로 합치기 (Python/PIL 사용)"""
    # Blender의 PIL이 없을 수 있으므로, subprocess로 외부 스크립트 호출하거나
    # Blender의 이미지 API 사용

    import os
    images = sorted([
        f for f in os.listdir(image_dir)
        if f.endswith('.png')
    ])

    rows = math.ceil(len(images) / cols)
    sheet_width = cols * sprite_width
    sheet_height = rows * sprite_height

    # Blender 이미지 생성
    sheet = bpy.data.images.new(
        'SpriteSheet',
        width=sheet_width,
        height=sheet_height,
        alpha=True
    )

    # 각 이미지 로드 및 복사
    pixels = [0.0] * (sheet_width * sheet_height * 4)

    for idx, img_name in enumerate(images):
        col = idx % cols
        row = idx // cols

        img = bpy.data.images.load(os.path.join(image_dir, img_name))
        img.scale(sprite_width, sprite_height)
        img_pixels = list(img.pixels)

        # 스프라이트 시트의 올바른 위치에 복사
        # Blender 이미지는 bottom-left 원점
        y_offset = (rows - 1 - row) * sprite_height
        x_offset = col * sprite_width

        for py in range(sprite_height):
            for px in range(sprite_width):
                src_idx = (py * sprite_width + px) * 4
                dst_idx = ((y_offset + py) * sheet_width + (x_offset + px)) * 4
                for c in range(4):
                    pixels[dst_idx + c] = img_pixels[src_idx + c]

        bpy.data.images.remove(img)

    sheet.pixels = pixels
    sheet.filepath_raw = output_path
    sheet.file_format = 'PNG'
    sheet.save()
    print(f"Sprite sheet saved: {output_path} ({sheet_width}x{sheet_height})")
```

### 외부 도구로 합치기 (ImageMagick)
```bash
# montage (ImageMagick)
montage sprites/*.png -tile 8x -geometry 128x128+0+0 -background none sprite_sheet.png

# 특정 순서 지정
montage S_*.png SW_*.png W_*.png NW_*.png N_*.png NE_*.png E_*.png SE_*.png \
    -tile 8x -geometry 128x128+0+0 -background none sprite_sheet.png
```

### 외부 도구로 합치기 (ffmpeg)
```bash
# 이미지 시퀀스 → 스프라이트 시트 (ffmpeg tile 필터)
ffmpeg -i sprites/frame_%04d.png -filter_complex "tile=8x4" sprite_sheet.png
```

## 라이팅 설정

### 스프라이트용 표준 라이팅
```python
def setup_sprite_lighting():
    """스프라이트 렌더링용 3점 조명"""
    # 기존 라이트 제거
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)

    # Key Light (주광)
    key_data = bpy.data.lights.new('KeyLight', 'SUN')
    key_data.energy = 3.0
    key_obj = bpy.data.objects.new('KeyLight', key_data)
    bpy.context.collection.objects.link(key_obj)
    key_obj.rotation_euler = (math.radians(50), 0, math.radians(30))

    # Fill Light (보조광)
    fill_data = bpy.data.lights.new('FillLight', 'SUN')
    fill_data.energy = 1.0
    fill_obj = bpy.data.objects.new('FillLight', fill_data)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = (math.radians(40), 0, math.radians(-60))

    # Rim Light (림광 — 윤곽 강조)
    rim_data = bpy.data.lights.new('RimLight', 'SUN')
    rim_data.energy = 1.5
    rim_obj = bpy.data.objects.new('RimLight', rim_data)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.rotation_euler = (math.radians(-20), 0, math.radians(150))

    # 환경광 (World)
    world = bpy.data.worlds.get('World')
    if not world:
        world = bpy.data.worlds.new('World')
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs['Strength'].default_value = 0.3
    bg.inputs['Color'].default_value = (0.8, 0.85, 1.0, 1.0)
```

### 외곽선 효과 (Freestyle)
```python
def setup_outline_rendering(thickness=1.5):
    """Freestyle 외곽선 (셀 셰이딩 / 2D 느낌)"""
    scene = bpy.context.scene
    view_layer = bpy.context.view_layer

    # Freestyle 활성화
    view_layer.use_freestyle = True

    # 라인 설정
    freestyle = view_layer.freestyle_settings
    linesets = freestyle.linesets
    if len(linesets) == 0:
        linesets.new('OutlineSet')

    lineset = linesets[0]
    lineset.select_silhouette = True
    lineset.select_border = True
    lineset.select_crease = True
    lineset.select_edge_mark = False

    # 라인 스타일
    linestyle = lineset.linestyle
    linestyle.thickness = thickness
    linestyle.color = (0, 0, 0)  # 검은 외곽선
```

## 렌더 엔진 비교 (스프라이트용)

| 기준 | Cycles | EEVEE | Workbench |
|------|--------|-------|-----------|
| **품질** | 최고 (레이트레이싱) | 좋음 (래스터) | 기본 |
| **속도** | 느림 | 빠름 | 매우 빠름 |
| **headless** | ✅ 완전 | ⚠️ Linux+GPU만 | ⚠️ Linux+GPU만 |
| **투명 배경** | ✅ | ✅ | ✅ |
| **추천 용도** | 고품질 스프라이트 | 빠른 프리뷰 | 와이어프레임/실루엣 |

### 스프라이트 렌더링 최적화 팁

1. **Cycles**: samples 32~64면 스프라이트에 충분. denoising 활성화.
2. **스프라이트 크기**: 128x128 이하면 samples 더 줄여도 OK
3. **빛 바운스**: `scene.cycles.max_bounces = 4` (기본 12 불필요)
4. **캐싱**: 같은 씬에서 카메라만 이동 시 BVH 재구축 불필요
5. **배치**: xargs/GNU parallel로 여러 Blender 인스턴스 병렬 실행
```bash
# 8코어로 병렬 렌더
seq 0 7 | xargs -P 8 -I {} blender -b scene.blend -P render.py -- --angle {}
```
