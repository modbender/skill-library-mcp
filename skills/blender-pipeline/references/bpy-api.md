# Blender Python API (bpy) 핵심 레퍼런스

## 모듈 구조

```python
import bpy          # 메인 API
import bmesh        # 메시 편집 (로우레벨)
import mathutils    # 벡터, 행렬, 쿼터니언
import os, sys      # 표준 라이브러리
```

## bpy 핵심 모듈

### bpy.data — 데이터 접근
```python
# 씬의 모든 오브젝트
bpy.data.objects['Cube']
bpy.data.meshes['CubeMesh']
bpy.data.materials['Material']
bpy.data.armatures['Armature']
bpy.data.actions['WalkAction']
bpy.data.collections['Collection']

# 현재 blend 파일 경로
bpy.data.filepath

# 모든 데이터 순회
for obj in bpy.data.objects:
    print(obj.name, obj.type)  # MESH, ARMATURE, CAMERA, LIGHT, EMPTY
```

### bpy.context — 현재 컨텍스트
```python
# 현재 씬
scene = bpy.context.scene

# 활성/선택 오브젝트
active = bpy.context.active_object
selected = bpy.context.selected_objects

# 뷰 레이어
view_layer = bpy.context.view_layer

# 모드 (OBJECT, EDIT, POSE, SCULPT...)
bpy.context.mode

# headless에서 컨텍스트 오버라이드 (Blender 3.2+)
with bpy.context.temp_override(active_object=obj):
    bpy.ops.object.some_operation()
```

### bpy.ops — 오퍼레이터 (명령 실행)
```python
# 오브젝트 생성
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=16, ring_count=8)
bpy.ops.mesh.primitive_plane_add(size=10)
bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=2)
bpy.ops.mesh.primitive_cone_add(radius1=1, depth=2)
bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=0.25)

# 오브젝트 조작
bpy.ops.object.select_all(action='SELECT')  # DESELECT, INVERT, TOGGLE
bpy.ops.object.delete()
bpy.ops.object.duplicate()
bpy.ops.object.join()  # 선택된 오브젝트 합치기
bpy.ops.object.convert(target='MESH')  # 커브→메시 등

# 트랜스폼 적용
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# 모디파이어
bpy.ops.object.modifier_add(type='SUBSURF')
bpy.ops.object.modifier_add(type='DECIMATE')
bpy.ops.object.modifier_add(type='MIRROR')
bpy.ops.object.modifier_add(type='SOLIDIFY')
bpy.ops.object.modifier_apply(modifier="Decimate")

# 렌더
bpy.ops.render.render(write_still=True)  # 단일 프레임
bpy.ops.render.render(animation=True)     # 애니메이션

# 씬 관리
bpy.ops.wm.open_mainfile(filepath="scene.blend")
bpy.ops.wm.save_as_mainfile(filepath="output.blend")
```

## 오브젝트 직접 조작

### Transform
```python
obj = bpy.data.objects['Cube']
obj.location = (1.0, 2.0, 3.0)
obj.rotation_euler = (0, 0, 1.5708)  # 라디안
obj.scale = (2.0, 2.0, 2.0)

# 부모 설정
child.parent = parent_obj
child.matrix_parent_inverse = parent_obj.matrix_world.inverted()
```

### 메시 데이터
```python
mesh = obj.data
# 정점
for v in mesh.vertices:
    print(v.co)  # Vector (x, y, z)
    v.co.z += 1.0  # 정점 이동

# 폴리곤
for poly in mesh.polygons:
    print(poly.vertices[:])  # 정점 인덱스
    print(poly.normal)

# 에지
for edge in mesh.edges:
    print(edge.vertices[:])
```

### 머티리얼
```python
# 새 머티리얼 생성
mat = bpy.data.materials.new(name="GameMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Principled BSDF 노드 접근
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.8, 0.2, 0.1, 1.0)
bsdf.inputs['Metallic'].default_value = 0.0
bsdf.inputs['Roughness'].default_value = 0.7

# 오브젝트에 머티리얼 적용
obj.data.materials.append(mat)

# 이미지 텍스처 추가
tex_node = nodes.new('ShaderNodeTexImage')
tex_node.image = bpy.data.images.load('/path/to/texture.png')
links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
```

## bmesh — 로우레벨 메시 편집

```python
import bmesh

# 새 bmesh 생성
bm = bmesh.new()

# 기존 메시에서 로드
bm = bmesh.new()
bm.from_mesh(obj.data)

# 정점 추가
v1 = bm.verts.new((0, 0, 0))
v2 = bm.verts.new((1, 0, 0))
v3 = bm.verts.new((1, 1, 0))
v4 = bm.verts.new((0, 1, 0))

# 면 추가
bm.faces.new((v1, v2, v3, v4))

# 메시에 적용
bm.to_mesh(obj.data)
bm.free()

# bmesh 오퍼레이션
bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=2)
bmesh.ops.extrude_face_region(bm, geom=bm.faces)
bmesh.ops.triangulate(bm, faces=bm.faces)
bmesh.ops.dissolve_limit(bm, angle_limit=0.0872665, verts=bm.verts, edges=bm.edges)
```

## 임포트/익스포트

### FBX
```python
# 임포트
bpy.ops.import_scene.fbx(
    filepath='model.fbx',
    use_custom_normals=True,
    use_image_search=True,
    force_connect_children=False,
    automatic_bone_orientation=True,
    primary_bone_axis='Y',
    secondary_bone_axis='X',
    use_prepost_rot=True
)

# 익스포트
bpy.ops.export_scene.fbx(
    filepath='output.fbx',
    use_selection=False,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_NONE',
    use_mesh_modifiers=True,
    add_leaf_bones=False,  # 게임엔진용: leaf bone 불필요
    bake_anim=True,
    bake_anim_use_all_bones=True,
    bake_anim_use_nla_strips=True,
    bake_anim_use_all_actions=True,
    primary_bone_axis='Y',
    secondary_bone_axis='X'
)
```

### glTF/GLB
```python
# 임포트
bpy.ops.import_scene.gltf(
    filepath='model.gltf',
    import_shading='NORMALS',
    bone_heuristic='BLENDER',
    merge_vertices=False
)

# 익스포트
bpy.ops.export_scene.gltf(
    filepath='output.glb',
    export_format='GLB',           # GLB, GLTF_SEPARATE, GLTF_EMBEDDED
    use_selection=False,
    export_apply=True,             # 모디파이어 적용
    export_animations=True,
    export_skins=True,
    export_morph=True,
    export_lights=False,
    export_cameras=False,
    export_image_format='AUTO',    # AUTO, JPEG, WEBP, NONE
    export_draco_mesh_compression_enable=False
)
```

### OBJ
```python
# 임포트
bpy.ops.wm.obj_import(filepath='model.obj')

# 익스포트
bpy.ops.wm.obj_export(
    filepath='output.obj',
    export_selected_objects=False,
    export_uv=True,
    export_normals=True,
    export_materials=True,
    apply_modifiers=True
)
```

## 렌더 설정

```python
scene = bpy.context.scene

# 렌더 엔진
scene.render.engine = 'CYCLES'  # 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'

# 해상도
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100

# 출력
scene.render.filepath = '/output/path/frame_'
scene.render.image_settings.file_format = 'PNG'  # JPEG, OPEN_EXR, TIFF

# 투명 배경 (스프라이트용)
scene.render.film_transparent = True
scene.render.image_settings.color_mode = 'RGBA'

# Cycles 설정
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.cycles.device = 'GPU'  # 'CPU'

# 프레임 범위
scene.frame_start = 1
scene.frame_end = 60
scene.frame_step = 1
```

## 카메라 제어

```python
import math

# 카메라 생성
cam_data = bpy.data.cameras.new('RenderCam')
cam_obj = bpy.data.objects.new('RenderCam', cam_data)
bpy.context.collection.objects.link(cam_obj)

# 활성 카메라 설정
bpy.context.scene.camera = cam_obj

# 직교 카메라 (스프라이트/아이소메트릭)
cam_data.type = 'ORTHO'
cam_data.ortho_scale = 5.0

# 원근 카메라
cam_data.type = 'PERSP'
cam_data.lens = 50  # mm

# 카메라 위치 (궤도)
import mathutils
angle_rad = math.radians(45)
distance = 10
cam_obj.location = (
    distance * math.cos(angle_rad),
    distance * math.sin(angle_rad),
    distance * 0.7  # 높이
)

# 타겟 바라보기
direction = mathutils.Vector((0, 0, 0)) - cam_obj.location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam_obj.rotation_euler = rot_quat.to_euler()
```

## CLI 인자 파싱

```python
import sys
import argparse

def parse_args():
    """Blender CLI에서 -- 이후 인자 파싱"""
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description='Blender Script')
    parser.add_argument('--input', type=str, required=True)
    parser.add_argument('--output', type=str, required=True)
    parser.add_argument('--verbose', action='store_true')
    return parser.parse_args(argv)

args = parse_args()
```

## 씬 초기화 (headless 공통 패턴)

```python
import bpy

def clear_scene():
    """씬의 모든 오브젝트 삭제"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # 고아 데이터 정리
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in bpy.data.textures:
        if block.users == 0:
            bpy.data.textures.remove(block)
    for block in bpy.data.images:
        if block.users == 0:
            bpy.data.images.remove(block)

def setup_scene():
    """기본 씬 설정"""
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 64
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    return scene
```

## 유용한 유틸리티

```python
# 오브젝트 선택
def select_object(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

# 바운딩 박스
def get_bbox(obj):
    """오브젝트의 월드 바운딩 박스"""
    bbox = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
    min_co = mathutils.Vector((min(v.x for v in bbox), min(v.y for v in bbox), min(v.z for v in bbox)))
    max_co = mathutils.Vector((max(v.x for v in bbox), max(v.y for v in bbox), max(v.z for v in bbox)))
    return min_co, max_co

# 폴리곤 수 확인
def get_polycount(obj):
    if obj.type == 'MESH':
        return len(obj.data.polygons)
    return 0

# 씬 전체 폴리곤 수
def total_polycount():
    return sum(get_polycount(obj) for obj in bpy.data.objects if obj.type == 'MESH')
```
