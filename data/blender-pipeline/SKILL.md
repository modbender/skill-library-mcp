---
name: blender-pipeline
description: |
  Blender 헤드리스 게임 에셋 파이프라인. 3D 모델 제작/가공/변환/렌더링을 Blender Python API(bpy)로 자동화.
  트리거: 3D 모델링, 에셋 변환, 스프라이트 시트, 리깅, Mixamo, FBX/glTF 변환, 프로시저럴 에셋 생성 관련 요청.
---

# Blender Headless Game Asset Pipeline

게임 개발에 필요한 3D 에셋 제작/가공을 Blender Python API(bpy)로 자동화하는 스킬.

## 설치

### Linux (MiniPC / 서버)
```bash
# Snap (권장 — 최신 버전)
sudo snap install blender --classic

# APT (구버전일 수 있음)
sudo apt install blender

# 직접 다운로드 (가장 유연)
wget https://download.blender.org/release/Blender4.4/blender-4.4.0-linux-x64.tar.xz
tar xf blender-4.4.0-linux-x64.tar.xz
sudo ln -s $(pwd)/blender-4.4.0-linux-x64/blender /usr/local/bin/blender
```

### macOS
```bash
# Homebrew
brew install --cask blender

# 또는 직접 다운로드
# CLI 경로: /Applications/Blender.app/Contents/MacOS/Blender
```

### 설치 확인
```bash
blender --version
blender -b --python-expr "import bpy; print('bpy OK:', bpy.app.version_string)"
```

## 헤드리스 실행 패턴

### 기본 구조
```bash
# 스크립트 실행 (새 씬)
blender -b --python script.py

# .blend 파일 로드 후 스크립트 실행
blender -b scene.blend --python script.py

# 인자 전달 (-- 이후)
blender -b --python script.py -- --arg1 value1 --arg2 value2

# 팩토리 설정으로 실행 (사용자 설정 무시)
blender --factory-startup -b --python script.py

# 애드온 활성화
blender -b --addons "rigify,io_scene_gltf2" --python script.py
```

### 인자 순서 중요!
```bash
# ✅ 올바름: blend 로드 → 출력 설정 → 렌더
blender -b scene.blend -o /tmp/output -F PNG -f 1

# ❌ 잘못됨: 출력 설정이 blend 로드 전
blender -b -o /tmp/output scene.blend -f 1
```

### GPU 렌더링 (headless)
```python
# gpu_setup.py — headless에서 GPU 활성화
import bpy
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'CUDA'  # 또는 OPTIX, HIP, METAL
prefs.get_devices()
for device in prefs.devices:
    device.use = True
bpy.context.scene.cycles.device = 'GPU'
```
```bash
blender -b scene.blend -E CYCLES -P gpu_setup.py -f 1 -- --cycles-device CUDA
```

## 스크립트 사용법

### 1. 포맷 변환 (convert_format.py)
```bash
# FBX → glTF
blender -b --python scripts/convert_format.py -- \
  --input model.fbx --output model.glb --format GLB

# OBJ → FBX
blender -b --python scripts/convert_format.py -- \
  --input model.obj --output model.fbx --format FBX

# glTF → OBJ
blender -b --python scripts/convert_format.py -- \
  --input model.gltf --output model.obj --format OBJ

# 배치 변환 (폴더 내 모든 FBX → glTF)
blender -b --python scripts/convert_format.py -- \
  --input-dir ./models/ --output-dir ./converted/ \
  --input-ext .fbx --format GLB
```

### 2. 스프라이트 시트 렌더링 (render_sprite_sheet.py)
```bash
# 8방향 스프라이트 시트
blender -b character.blend --python scripts/render_sprite_sheet.py -- \
  --angles 8 --size 128 --output sprites/character.png

# 아이소메트릭 뷰 (카메라 각도 지정)
blender -b character.blend --python scripts/render_sprite_sheet.py -- \
  --angles 8 --size 256 --camera-angle 30 --output sprites/iso_char.png

# 애니메이션 스프라이트 시트 (모든 프레임)
blender -b character.blend --python scripts/render_sprite_sheet.py -- \
  --angles 4 --size 64 --animated --output sprites/anim_sheet.png
```

### 3. 프로시저럴 소품 생성 (procedural_props.py)
```bash
# 나무 생성
blender -b --python scripts/procedural_props.py -- \
  --type tree --style low-poly --seed 42 --output props/tree.glb

# 바위 생성
blender -b --python scripts/procedural_props.py -- \
  --type rock --style low-poly --count 5 --output props/rocks.glb

# 상자/크레이트
blender -b --python scripts/procedural_props.py -- \
  --type crate --style wooden --output props/crate.glb

# 건물 외형
blender -b --python scripts/procedural_props.py -- \
  --type building --floors 3 --style medieval --output props/building.glb
```

### 4. 간단한 리깅 (simple_rig.py)
```bash
# Rigify 메타리그로 자동 리깅
blender -b character.blend --python scripts/simple_rig.py -- \
  --target CharacterMesh --type rigify --output rigged_character.blend

# 심플 본 리그 (2D 게임용)
blender -b character.blend --python scripts/simple_rig.py -- \
  --target CharacterMesh --type simple --bones spine,arm_l,arm_r,leg_l,leg_r \
  --output rigged_simple.blend
```

### 5. Mixamo 임포트 (mixamo_import.py)
```bash
# 단일 Mixamo FBX 임포트 + glTF 변환
blender -b --python scripts/mixamo_import.py -- \
  --input mixamo_character.fbx --output character.glb --fix-scale --fix-rotation

# 여러 Mixamo 애니메이션 병합
blender -b --python scripts/mixamo_import.py -- \
  --input-dir ./mixamo_anims/ --merge-animations \
  --output character_animated.glb

# Mixamo → NLA 트랙 정리
blender -b --python scripts/mixamo_import.py -- \
  --input-dir ./mixamo_anims/ --nla-tracks \
  --output character_nla.blend
```

## 워크플로우

### 워크플로우 1: Mixamo → Blender → 게임엔진
```
1. Mixamo에서 캐릭터 리깅 + 애니메이션 다운로드 (FBX)
2. mixamo_import.py로 Blender에 임포트 (스케일/회전 보정)
3. 필요시 애니메이션 NLA 트랙 정리
4. convert_format.py로 glTF/GLB 변환
5. 게임엔진(Godot/Unity)에서 임포트
```

### 워크플로우 2: 프로시저럴 에셋 → 스프라이트 시트
```
1. procedural_props.py로 3D 에셋 생성
2. 또는 기존 .blend 파일의 모델 사용
3. render_sprite_sheet.py로 다방향 스프라이트 시트 생성
4. 2D 게임에서 스프라이트 시트 사용
```

### 워크플로우 3: 에셋 배치 파이프라인
```bash
#!/bin/bash
# batch_pipeline.sh — 전체 파이프라인 자동화

INPUT_DIR="./raw_models"
OUTPUT_DIR="./game_assets"

# 1. 모든 FBX를 glTF로 변환
blender -b --python scripts/convert_format.py -- \
  --input-dir "$INPUT_DIR" --output-dir "$OUTPUT_DIR/models" \
  --input-ext .fbx --format GLB

# 2. 각 모델의 스프라이트 시트 생성
for blend in "$OUTPUT_DIR"/models/*.glb; do
  name=$(basename "$blend" .glb)
  blender -b --python scripts/render_sprite_sheet.py -- \
    --import "$blend" --angles 8 --size 128 \
    --output "$OUTPUT_DIR/sprites/${name}_sheet.png"
done
```

## MiniPC에서 실행 (nodes.run)

### Clawdbot에서 MiniPC로 실행
```
# nodes.run으로 Blender 스크립트 실행
nodes.run(node="MiniPC", command=[
    "blender", "-b", "--factory-startup",
    "--python", "/path/to/script.py",
    "--", "--arg1", "value1"
])
```

### MiniPC에 Blender 설치
```bash
# MiniPC SSH 접속 후
sudo snap install blender --classic

# 또는 직접 다운로드
wget https://download.blender.org/release/Blender4.4/blender-4.4.0-linux-x64.tar.xz
tar xf blender-4.4.0-linux-x64.tar.xz
echo 'export PATH="$HOME/blender-4.4.0-linux-x64:$PATH"' >> ~/.bashrc
```

### 파일 전송
```bash
# MiniPC → 맥스튜디오 (HTTP 서버)
# MiniPC에서:
cd /output/dir && python3 -m http.server 9877
# 맥스튜디오에서:
curl -O http://<MINIPC_IP>:9877/output_file.glb
```

## 제한사항 / 주의사항

### 렌더링 엔진
| 엔진 | Headless 지원 | GPU 필요 | 비고 |
|------|:---:|:---:|------|
| **Cycles** | ✅ 완전 지원 | 선택 | CPU/GPU 모두 가능. 기본 선택. |
| **EEVEE** | ⚠️ Linux만 | 필수 | Linux 3.4+ GPU 필수. macOS/Windows headless 불가. |
| **Workbench** | ⚠️ Linux만 | 필수 | EEVEE와 같은 제한. |

### 알려진 제한
- **EEVEE headless**: Linux + GPU + display 환경 필요. `Xvfb`로 가상 디스플레이 생성 가능:
  ```bash
  sudo apt install xvfb
  xvfb-run blender -b scene.blend -E BLENDER_EEVEE -f 1
  ```
- **GPU 자동 감지 안 됨**: headless 모드에서 GPU를 수동으로 활성화해야 함 (위 gpu_setup.py 참조)
- **bpy 단일 임포트**: Python에서 `import bpy`는 프로세스당 한 번만 가능. 여러 작업은 서브프로세스로 분리.
- **메모리**: 복잡한 씬은 상당한 RAM 필요. MiniPC(8GB)에서는 로우폴리 위주.
- **Grease Pencil**: headless GPU 없는 환경에서 렌더 불가.
- **Snap 경로**: snap으로 설치 시 `pip install` 경로가 제한적. 추가 패키지 필요 시 tarball 설치 권장.
- **Blender 버전 호환**: bpy API는 버전 간 변경 가능. 스크립트는 Blender 4.x 기준.

### 성능 팁
- `--factory-startup`: 불필요한 사용자 설정 로드 방지
- `--threads N`: CPU 스레드 수 지정 (0 = 전체)
- 로우폴리 에셋은 Cycles보다 Workbench가 빠름
- 배치 작업은 xargs/parallel로 병렬화 가능

## 레퍼런스

- [references/bpy-api.md](references/bpy-api.md) — Blender Python API 핵심 레퍼런스
- [references/rigging.md](references/rigging.md) — 리깅 가이드 (Rigify, Mixamo)
- [references/procedural.md](references/procedural.md) — 프로시저럴 모델링 패턴
- [references/rendering.md](references/rendering.md) — 스프라이트 시트/렌더링 가이드
