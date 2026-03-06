# 리깅 가이드 (Rigify, 커스텀, Mixamo)

## Rigify 자동 리깅

### 개요
Rigify는 Blender 내장 애드온으로, 메타리그(metarig)를 기반으로 완전한 컨트롤 리그를 자동 생성한다.

### Python에서 Rigify 사용

```python
import bpy

# 1. Rigify 애드온 활성화
bpy.ops.preferences.addon_enable(module='rigify')

# 2. 휴머노이드 메타리그 추가
bpy.ops.object.armature_human_metarig_add()
metarig = bpy.context.active_object

# 3. 메타리그 본 위치 조정 (편집 모드에서)
bpy.ops.object.mode_set(mode='EDIT')
# 본 위치를 캐릭터 메시에 맞게 조정
# 예: 머리 본 위치
metarig.data.edit_bones['spine.006'].head = (0, 0, 1.7)
bpy.ops.object.mode_set(mode='OBJECT')

# 4. 리그 생성
bpy.context.view_layer.objects.active = metarig
bpy.ops.pose.rigify_generate()

# 생성된 리그 이름은 기본 'rig'
rig = bpy.data.objects.get('rig')
```

### 메타리그 본 구조 (휴머노이드)
```
spine → spine.001 → spine.002 → spine.003 (몸통)
  ├── spine.004 → spine.005 → spine.006 (목/머리)
  ├── shoulder.L → upper_arm.L → forearm.L → hand.L (왼팔)
  │     └── palm.01.L → f_index.01.L → ... (손가락)
  ├── shoulder.R → upper_arm.R → forearm.R → hand.R (오른팔)
  ├── thigh.L → shin.L → foot.L → toe.L (왼다리)
  └── thigh.R → shin.R → foot.R → toe.R (오른다리)
```

### 메시를 리그에 바인딩
```python
# 1. 메시와 리그 선택
mesh_obj = bpy.data.objects['CharacterMesh']
rig_obj = bpy.data.objects['rig']

# 메시 선택 후 리그를 활성으로
bpy.ops.object.select_all(action='DESELECT')
mesh_obj.select_set(True)
rig_obj.select_set(True)
bpy.context.view_layer.objects.active = rig_obj

# 2. Automatic Weights로 부모 설정
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
```

### Rigify 설정 커스터마이즈
```python
metarig = bpy.data.objects['metarig']

# 리그 이름 설정
metarig.data.rigify_rig_basename = "character_rig"

# 위젯 컬렉션 설정
metarig.data.rigify_target_rig = None  # 새로 생성

# IK/FK 전환 기본값
# Rigify는 generate 시 UI 스크립트도 생성함
```

## 커스텀 심플 리깅

### 기본 아마추어 생성
```python
import bpy
from mathutils import Vector

def create_simple_rig(bone_definitions):
    """
    심플 리그 생성
    bone_definitions: [(name, head_pos, tail_pos, parent_name), ...]
    """
    # 아마추어 생성
    arm_data = bpy.data.armatures.new('SimpleRig')
    arm_obj = bpy.data.objects.new('SimpleRig', arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj

    # 편집 모드
    bpy.ops.object.mode_set(mode='EDIT')

    bones = {}
    for name, head, tail, parent_name in bone_definitions:
        bone = arm_data.edit_bones.new(name)
        bone.head = Vector(head)
        bone.tail = Vector(tail)
        if parent_name and parent_name in bones:
            bone.parent = bones[parent_name]
        bones[name] = bone

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj

# 사용 예: 2D 게임용 심플 캐릭터 리그
bones = [
    ('root',      (0, 0, 0),     (0, 0, 0.2),   None),
    ('spine',     (0, 0, 0.5),   (0, 0, 1.0),   'root'),
    ('spine.001', (0, 0, 1.0),   (0, 0, 1.4),   'spine'),
    ('neck',      (0, 0, 1.4),   (0, 0, 1.6),   'spine.001'),
    ('head',      (0, 0, 1.6),   (0, 0, 1.9),   'neck'),
    ('arm.L',     (0.2, 0, 1.3), (0.6, 0, 1.3), 'spine.001'),
    ('arm.R',     (-0.2, 0, 1.3),(-0.6, 0, 1.3),'spine.001'),
    ('leg.L',     (0.1, 0, 0.5), (0.1, 0, 0),   'root'),
    ('leg.R',     (-0.1, 0, 0.5),(-0.1, 0, 0),  'root'),
]
rig = create_simple_rig(bones)
```

### IK 컨스트레인트 추가
```python
def add_ik_constraint(rig_obj, bone_name, target_bone_name, chain_length=2):
    """IK 컨스트레인트 추가"""
    bpy.context.view_layer.objects.active = rig_obj
    bpy.ops.object.mode_set(mode='POSE')

    pose_bone = rig_obj.pose.bones[bone_name]
    constraint = pose_bone.constraints.new('IK')
    constraint.target = rig_obj
    constraint.subtarget = target_bone_name
    constraint.chain_count = chain_length

    bpy.ops.object.mode_set(mode='OBJECT')
```

## Mixamo 파이프라인

### Mixamo FBX 임포트 문제 및 해결

#### 공통 문제
1. **스케일 불일치**: Mixamo는 cm 단위, Blender는 m 단위
2. **회전 오프셋**: FBX 축 방향 차이
3. **Leaf Bone 문제**: 불필요한 끝 본이 추가됨
4. **NLA 트랙 정리 필요**: 여러 애니메이션 병합 시

#### 임포트 설정
```python
import bpy

def import_mixamo_fbx(filepath, fix_scale=True, fix_rotation=True):
    """Mixamo FBX를 올바르게 임포트"""

    bpy.ops.import_scene.fbx(
        filepath=filepath,
        use_custom_normals=True,
        use_image_search=True,
        force_connect_children=False,
        automatic_bone_orientation=True,
        primary_bone_axis='Y',
        secondary_bone_axis='X',
        use_prepost_rot=True,
        # Mixamo 특유 설정
        ignore_leaf_bones=True,        # leaf bone 무시
        use_anim=True,
        anim_offset=1.0
    )

    imported = bpy.context.selected_objects
    armature = None
    meshes = []

    for obj in imported:
        if obj.type == 'ARMATURE':
            armature = obj
        elif obj.type == 'MESH':
            meshes.append(obj)

    if armature and fix_scale:
        # Mixamo FBX는 보통 100배 크기
        armature.scale = (0.01, 0.01, 0.01)
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.select_all(action='DESELECT')
        armature.select_set(True)
        for m in meshes:
            m.select_set(True)
        bpy.ops.object.transform_apply(scale=True)

    if armature and fix_rotation:
        armature.rotation_euler = (0, 0, 0)
        bpy.ops.object.transform_apply(rotation=True)

    return armature, meshes
```

### 여러 Mixamo 애니메이션 병합
```python
def merge_mixamo_animations(anim_dir, character_fbx=None):
    """여러 Mixamo FBX 애니메이션을 하나의 아마추어에 NLA 트랙으로 병합"""
    import os

    # 캐릭터 임포트 (첫 번째 파일)
    if character_fbx:
        armature, meshes = import_mixamo_fbx(character_fbx)
    else:
        armature = None

    # 애니메이션 FBX 파일들
    anim_files = sorted([
        f for f in os.listdir(anim_dir)
        if f.lower().endswith('.fbx')
    ])

    for anim_file in anim_files:
        filepath = os.path.join(anim_dir, anim_file)
        anim_name = os.path.splitext(anim_file)[0]

        # 임포트
        bpy.ops.import_scene.fbx(
            filepath=filepath,
            use_custom_normals=True,
            automatic_bone_orientation=True,
            ignore_leaf_bones=True,
            use_anim=True
        )

        # 임포트된 아마추어 찾기
        imported_arm = None
        for obj in bpy.context.selected_objects:
            if obj.type == 'ARMATURE':
                imported_arm = obj
                break

        if imported_arm and imported_arm.animation_data:
            action = imported_arm.animation_data.action
            if action:
                action.name = anim_name

                if armature is None:
                    armature = imported_arm
                else:
                    # 액션을 메인 아마추어에 NLA 트랙으로 추가
                    if not armature.animation_data:
                        armature.animation_data_create()

                    track = armature.animation_data.nla_tracks.new()
                    track.name = anim_name
                    track.strips.new(anim_name, int(action.frame_range[0]), action)

                    # 임포트된 아마추어 삭제
                    bpy.data.objects.remove(imported_arm, do_unlink=True)

    return armature
```

### Mixamo 본 이름 리매핑
```python
# Mixamo → Blender 표준 본 이름 매핑
MIXAMO_TO_BLENDER = {
    'mixamorig:Hips': 'spine',
    'mixamorig:Spine': 'spine.001',
    'mixamorig:Spine1': 'spine.002',
    'mixamorig:Spine2': 'spine.003',
    'mixamorig:Neck': 'spine.004',
    'mixamorig:Head': 'spine.006',
    'mixamorig:LeftShoulder': 'shoulder.L',
    'mixamorig:LeftArm': 'upper_arm.L',
    'mixamorig:LeftForeArm': 'forearm.L',
    'mixamorig:LeftHand': 'hand.L',
    'mixamorig:RightShoulder': 'shoulder.R',
    'mixamorig:RightArm': 'upper_arm.R',
    'mixamorig:RightForeArm': 'forearm.R',
    'mixamorig:RightHand': 'hand.R',
    'mixamorig:LeftUpLeg': 'thigh.L',
    'mixamorig:LeftLeg': 'shin.L',
    'mixamorig:LeftFoot': 'foot.L',
    'mixamorig:LeftToeBase': 'toe.L',
    'mixamorig:RightUpLeg': 'thigh.R',
    'mixamorig:RightLeg': 'shin.R',
    'mixamorig:RightFoot': 'foot.R',
    'mixamorig:RightToeBase': 'toe.R',
}

def rename_mixamo_bones(armature):
    """Mixamo 본 이름을 Blender 표준으로 변환"""
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')

    for bone in armature.data.edit_bones:
        if bone.name in MIXAMO_TO_BLENDER:
            bone.name = MIXAMO_TO_BLENDER[bone.name]

    bpy.ops.object.mode_set(mode='OBJECT')
```

## 게임엔진 익스포트 시 주의사항

### Godot용 (glTF)
```python
# Godot은 glTF/GLB 권장
bpy.ops.export_scene.gltf(
    filepath='character.glb',
    export_format='GLB',
    export_apply=True,
    export_animations=True,
    export_skins=True,
    export_morph=True,
    export_extras=True,    # 커스텀 프로퍼티
    export_yup=True,       # Godot은 Y-up
)
```

### Unity용 (FBX)
```python
# Unity는 FBX 권장
bpy.ops.export_scene.fbx(
    filepath='character.fbx',
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_ALL',
    use_mesh_modifiers=True,
    add_leaf_bones=False,
    bake_anim=True,
    bake_anim_use_all_bones=True,
    bake_anim_use_all_actions=True,
    primary_bone_axis='Y',
    secondary_bone_axis='X',
    axis_forward='-Z',
    axis_up='Y'
)
```

### Unreal Engine용 (FBX)
```python
bpy.ops.export_scene.fbx(
    filepath='character.fbx',
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_NONE',
    use_mesh_modifiers=True,
    add_leaf_bones=False,
    bake_anim=True,
    bake_anim_use_all_bones=True,
    bake_anim_force_startend_keying=True,
    primary_bone_axis='Y',
    secondary_bone_axis='X',
    axis_forward='X',
    axis_up='Z'  # UE는 Z-up
)
```
