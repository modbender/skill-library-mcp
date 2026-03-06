# 프로시저럴 모델링 패턴

## 기본 원칙

1. **bmesh 우선**: 복잡한 지오메트리는 `bmesh`로 직접 생성이 효율적
2. **시드 기반**: `random.seed()`로 재현 가능한 결과 보장
3. **파라메트릭**: 모든 주요 값을 매개변수로 노출
4. **로우폴리 지향**: 게임용 에셋은 최소 폴리곤으로

## 패턴 1: 프로시저럴 나무

```python
import bpy
import bmesh
import random
import math
from mathutils import Vector, Matrix

def create_lowpoly_tree(
    trunk_height=2.0,
    trunk_radius=0.15,
    trunk_segments=6,
    crown_radius=1.2,
    crown_height=1.5,
    crown_segments=6,
    crown_rings=4,
    variation=0.3,
    seed=42
):
    """로우폴리 나무 생성"""
    random.seed(seed)

    # --- 트렁크 (원통형) ---
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=trunk_segments,
        radius=trunk_radius,
        depth=trunk_height,
        location=(0, 0, trunk_height / 2)
    )
    trunk = bpy.context.active_object
    trunk.name = 'Tree_Trunk'

    # 트렁크 변형 (약간 불규칙하게)
    bm = bmesh.new()
    bm.from_mesh(trunk.data)
    for v in bm.verts:
        if v.co.z > 0.1:  # 밑부분은 안정적으로
            v.co.x += random.uniform(-variation * 0.1, variation * 0.1)
            v.co.y += random.uniform(-variation * 0.1, variation * 0.1)
    bm.to_mesh(trunk.data)
    bm.free()

    # --- 수관 (icosphere) ---
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2,
        radius=crown_radius,
        location=(0, 0, trunk_height + crown_height * 0.4)
    )
    crown = bpy.context.active_object
    crown.name = 'Tree_Crown'

    # 수관 변형 (자연스러운 모양)
    bm = bmesh.new()
    bm.from_mesh(crown.data)
    for v in bm.verts:
        noise = random.uniform(-variation, variation)
        direction = v.co.normalized()
        v.co += direction * noise
        # 아래쪽 좁히기
        if v.co.z < 0:
            v.co.x *= 0.6
            v.co.y *= 0.6
    bm.to_mesh(crown.data)
    bm.free()

    # 스케일 (높이 조정)
    crown.scale.z = crown_height / crown_radius

    # 합치기
    bpy.ops.object.select_all(action='DESELECT')
    trunk.select_set(True)
    crown.select_set(True)
    bpy.context.view_layer.objects.active = crown
    bpy.ops.object.join()

    tree = bpy.context.active_object
    tree.name = f'LowPoly_Tree_{seed}'

    return tree
```

## 패턴 2: 프로시저럴 바위

```python
def create_lowpoly_rock(
    size=1.0,
    subdivisions=2,
    noise_strength=0.4,
    flatten_bottom=True,
    seed=42
):
    """로우폴리 바위 생성"""
    random.seed(seed)

    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=subdivisions,
        radius=size,
        location=(0, 0, 0)
    )
    rock = bpy.context.active_object
    rock.name = f'Rock_{seed}'

    bm = bmesh.new()
    bm.from_mesh(rock.data)

    for v in bm.verts:
        # 랜덤 변형
        direction = v.co.normalized()
        displacement = random.uniform(-noise_strength, noise_strength)
        v.co += direction * displacement

        # 하단 평탄화
        if flatten_bottom and v.co.z < -size * 0.3:
            v.co.z = -size * 0.3

    # 면 평탄 셰이딩 (로우폴리 느낌)
    for face in bm.faces:
        face.smooth = False

    bm.to_mesh(rock.data)
    bm.free()

    return rock
```

## 패턴 3: 프로시저럴 건물

```python
def create_lowpoly_building(
    width=4.0,
    depth=3.0,
    floor_height=3.0,
    floors=2,
    roof_type='flat',  # flat, gabled, hip
    window_rows=2,
    window_cols=3,
    seed=42
):
    """로우폴리 건물 생성"""
    random.seed(seed)
    total_height = floor_height * floors

    # 본체
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, total_height / 2)
    )
    building = bpy.context.active_object
    building.name = f'Building_{seed}'
    building.scale = (width / 2, depth / 2, total_height / 2)
    bpy.ops.object.transform_apply(scale=True)

    # 지붕
    if roof_type == 'gabled':
        bm = bmesh.new()
        bm.from_mesh(building.data)
        bm.verts.ensure_lookup_table()

        # 상단 정점 중 앞뒤 중심을 올려서 삼각 지붕
        top_verts = [v for v in bm.verts if v.co.z > total_height * 0.9]
        for v in top_verts:
            if abs(v.co.x) < width * 0.1:
                v.co.z += floor_height * 0.5

        bm.to_mesh(building.data)
        bm.free()

    elif roof_type == 'hip':
        # 사다리꼴 지붕 추가
        roof_height = floor_height * 0.4
        roof_inset = 0.5

        bm = bmesh.new()
        # 지붕 기초 (상단 평면)
        v1 = bm.verts.new((-width/2, -depth/2, total_height))
        v2 = bm.verts.new(( width/2, -depth/2, total_height))
        v3 = bm.verts.new(( width/2,  depth/2, total_height))
        v4 = bm.verts.new((-width/2,  depth/2, total_height))

        # 지붕 꼭대기
        v5 = bm.verts.new((-width/2 + roof_inset, -depth/2 + roof_inset, total_height + roof_height))
        v6 = bm.verts.new(( width/2 - roof_inset, -depth/2 + roof_inset, total_height + roof_height))
        v7 = bm.verts.new(( width/2 - roof_inset,  depth/2 - roof_inset, total_height + roof_height))
        v8 = bm.verts.new((-width/2 + roof_inset,  depth/2 - roof_inset, total_height + roof_height))

        # 면 생성
        bm.faces.new((v1, v2, v6, v5))
        bm.faces.new((v2, v3, v7, v6))
        bm.faces.new((v3, v4, v8, v7))
        bm.faces.new((v4, v1, v5, v8))
        bm.faces.new((v5, v6, v7, v8))

        roof_mesh = bpy.data.meshes.new('Roof')
        bm.to_mesh(roof_mesh)
        bm.free()

        roof_obj = bpy.data.objects.new('Roof', roof_mesh)
        bpy.context.collection.objects.link(roof_obj)

        # 합치기
        bpy.ops.object.select_all(action='DESELECT')
        building.select_set(True)
        roof_obj.select_set(True)
        bpy.context.view_layer.objects.active = building
        bpy.ops.object.join()

    return building
```

## 패턴 4: 프로시저럴 상자/크레이트

```python
def create_crate(
    size=1.0,
    plank_width=0.15,
    plank_depth=0.05,
    gap=0.02,
    style='wooden',  # wooden, metal
    seed=42
):
    """게임용 상자/크레이트 생성"""
    random.seed(seed)

    # 기본 상자
    bpy.ops.mesh.primitive_cube_add(size=size, location=(0, 0, size / 2))
    crate = bpy.context.active_object
    crate.name = f'Crate_{seed}'

    if style == 'wooden':
        # 판자 디테일 추가 (Solidify + Edge Split)
        # 실제로는 디테일 메시를 따로 생성하고 합침
        bm = bmesh.new()
        bm.from_mesh(crate.data)

        # 약간의 불규칙성 추가
        for v in bm.verts:
            v.co.x += random.uniform(-0.01, 0.01)
            v.co.y += random.uniform(-0.01, 0.01)
            v.co.z += random.uniform(-0.01, 0.01)

        bm.to_mesh(crate.data)
        bm.free()

        # 엣지 강조
        mod = crate.modifiers.new('Bevel', 'BEVEL')
        mod.width = 0.02
        mod.segments = 1

    return crate
```

## 패턴 5: 프로시저럴 지형

```python
def create_terrain(
    size=20.0,
    subdivisions=10,
    height_scale=3.0,
    noise_scale=5.0,
    seed=42
):
    """로우폴리 지형 생성"""
    random.seed(seed)
    import math

    bpy.ops.mesh.primitive_grid_add(
        x_subdivisions=subdivisions,
        y_subdivisions=subdivisions,
        size=size
    )
    terrain = bpy.context.active_object
    terrain.name = f'Terrain_{seed}'

    bm = bmesh.new()
    bm.from_mesh(terrain.data)

    # 심플 노이즈 (Perlin 없이)
    for v in bm.verts:
        # 여러 주파수의 sin/cos 합성
        nx = v.co.x / noise_scale
        ny = v.co.y / noise_scale
        height = 0
        height += math.sin(nx * 1.0) * math.cos(ny * 1.0) * 1.0
        height += math.sin(nx * 2.3 + 0.5) * math.cos(ny * 1.7 + 0.3) * 0.5
        height += math.sin(nx * 4.1 + 1.2) * math.cos(ny * 3.9 + 0.7) * 0.25
        height += random.uniform(-0.1, 0.1)  # 미세 변화
        v.co.z = height * height_scale

    # 면 평탄 셰이딩 (로우폴리 느낌)
    for face in bm.faces:
        face.smooth = False

    bm.to_mesh(terrain.data)
    bm.free()

    return terrain
```

## 패턴 6: 배치 에셋 생성

```python
def batch_generate_assets(output_dir, asset_type='tree', count=10, base_seed=0):
    """다양한 시드로 에셋 배치 생성"""
    import os
    os.makedirs(output_dir, exist_ok=True)

    generators = {
        'tree': create_lowpoly_tree,
        'rock': create_lowpoly_rock,
        'crate': create_crate,
        'building': create_lowpoly_building,
    }

    gen_func = generators.get(asset_type)
    if not gen_func:
        print(f"Unknown asset type: {asset_type}")
        return

    for i in range(count):
        # 씬 초기화
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        seed = base_seed + i
        obj = gen_func(seed=seed)

        # GLB로 익스포트
        filepath = os.path.join(output_dir, f'{asset_type}_{seed:04d}.glb')
        bpy.ops.export_scene.gltf(
            filepath=filepath,
            export_format='GLB',
            use_selection=False,
            export_apply=True
        )
        print(f"Generated: {filepath}")
```

## 머티리얼 자동 생성

```python
def create_flat_color_material(name, color):
    """단색 플랫 머티리얼 (로우폴리용)"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # 기존 노드 제거
    for node in nodes:
        nodes.remove(node)

    # Principled BSDF
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    bsdf.inputs['Metallic'].default_value = 0.0

    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat

def create_game_color_palette():
    """게임용 컬러 팔레트"""
    colors = {
        'grass_green': (0.2, 0.6, 0.15),
        'tree_green': (0.15, 0.5, 0.1),
        'dark_green': (0.1, 0.35, 0.08),
        'trunk_brown': (0.35, 0.2, 0.1),
        'rock_gray': (0.5, 0.48, 0.45),
        'dark_rock': (0.3, 0.28, 0.25),
        'sand': (0.85, 0.75, 0.5),
        'water_blue': (0.2, 0.5, 0.8),
        'wood': (0.6, 0.4, 0.2),
        'metal': (0.6, 0.6, 0.65),
        'roof_red': (0.6, 0.15, 0.1),
        'wall_white': (0.9, 0.88, 0.82),
    }

    materials = {}
    for name, color in colors.items():
        materials[name] = create_flat_color_material(f'Game_{name}', color)

    return materials
```

## Decimate (폴리곤 감소)

```python
def decimate_object(obj, ratio=0.5, method='COLLAPSE'):
    """폴리곤 수 감소"""
    bpy.context.view_layer.objects.active = obj

    if method == 'COLLAPSE':
        mod = obj.modifiers.new('Decimate', 'DECIMATE')
        mod.decimate_type = 'COLLAPSE'
        mod.ratio = ratio
    elif method == 'PLANAR':
        mod = obj.modifiers.new('Decimate', 'DECIMATE')
        mod.decimate_type = 'DISSOLVE'
        mod.angle_limit = 0.0872665  # 5도
    elif method == 'UNSUBDIV':
        mod = obj.modifiers.new('Decimate', 'DECIMATE')
        mod.decimate_type = 'UNSUBDIV'
        mod.iterations = 2

    bpy.ops.object.modifier_apply(modifier='Decimate')

    new_count = len(obj.data.polygons)
    print(f"Decimated to {new_count} polygons")
    return new_count
```
