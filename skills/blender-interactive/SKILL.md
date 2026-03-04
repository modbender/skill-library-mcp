---
name: blender-interactive
description: |
  Blender 양방향 소켓 통신 스킬. TCP 소켓 서버로 실시간 씬 조작, 상태 조회, Poly Haven/Sketchfab 에셋 통합.
  기존 blender-pipeline (배치 처리)와 상호보완 — 복잡한 씬 구축, 반복 조작, 실시간 피드백에 사용.
  트리거: Blender 실시간 조작, 씬 상태 확인, Poly Haven 에셋, Sketchfab 모델, 양방향 Blender 통신.
---

# Blender Interactive Socket Server

TCP 소켓 기반 양방향 통신으로 Blender를 실시간 조작하는 스킬.
MiniPC의 headless Blender 5.0.1에서 실행.

## 아키텍처

```
┌─────────────┐     nodes.run      ┌──────────────────────┐
│  Clawdbot   │ ──────────────────>│  MiniPC              │
│  (맥스튜디오)│                     │                      │
│             │     blender_client  │  ┌────────────────┐  │
│             │ ──────────────────>│  │ Blender 5.0.1  │  │
│             │     TCP :9876       │  │ (headless)     │  │
│             │ <──────────────────│  │                │  │
│             │     JSON response   │  │ socket_addon   │  │
└─────────────┘                     │  └────────────────┘  │
                                    └──────────────────────┘
```

## 기존 스킬과의 관계

| 스킬 | 용도 | 패턴 |
|------|------|------|
| **blender-pipeline** | 배치 변환, 스프라이트시트, 프로시저럴 | 1회성 스크립트 실행 |
| **blender-interactive** | 실시간 조작, 씬 구축, 상태 조회 | 상주 소켓 서버 |

**선택 기준:**
- 단순 변환/배치 → blender-pipeline
- 복잡한 씬 구축, 반복 조작, 상태 확인 필요 → blender-interactive

## 빠른 시작

### 1. 서버 시작 (MiniPC)

```bash
# nodes.run으로 서버 시작
nodes.run(node="MiniPC", command=[
    "bash", "-c",
    "blender -b --factory-startup --python /home/spritz/blender-interactive/blender_socket_addon.py -- --port 9876 &"
])

# 또는 start_server.sh 사용
nodes.run(node="MiniPC", command=[
    "bash", "/home/spritz/blender-interactive/scripts/start_server.sh", "--background"
])
```

### 2. 명령 전송

```bash
# ping
nodes.run(node="MiniPC", command=[
    "python3", "/home/spritz/blender-interactive/scripts/blender_client.py",
    "ping"
])

# 씬 정보 조회
nodes.run(node="MiniPC", command=[
    "python3", "/home/spritz/blender-interactive/scripts/blender_client.py",
    "get_scene_info", "--pretty"
])

# 오브젝트 생성
nodes.run(node="MiniPC", command=[
    "python3", "/home/spritz/blender-interactive/scripts/blender_client.py",
    "create_object", "--params", "{\"type\":\"SPHERE\",\"name\":\"Earth\",\"location\":[0,0,0]}"
])

# 머티리얼 설정
nodes.run(node="MiniPC", command=[
    "python3", "/home/spritz/blender-interactive/scripts/blender_client.py",
    "set_material", "--params", "{\"object_name\":\"Earth\",\"color\":[0.2,0.4,0.8],\"metallic\":0.0,\"roughness\":0.7}"
])

# 렌더링 프리뷰
nodes.run(node="MiniPC", command=[
    "python3", "/home/spritz/blender-interactive/scripts/blender_client.py",
    "render_preview", "--params", "{\"output_path\":\"/tmp/preview.png\",\"resolution_x\":512,\"resolution_y\":512,\"samples\":32}"
])
```

### 3. 서버 중지

```bash
nodes.run(node="MiniPC", command=[
    "bash", "/home/spritz/blender-interactive/scripts/start_server.sh", "--stop"
])
```

## 명령어 레퍼런스

### 시스템
| 명령 | 파라미터 | 설명 |
|------|----------|------|
| `ping` | — | 서버 상태 확인 + 명령 목록 |

### 씬 조회
| 명령 | 파라미터 | 설명 |
|------|----------|------|
| `get_scene_info` | — | 전체 씬 상태 (오브젝트, 카메라, 라이트, 해상도 등) |
| `get_object_info` | `name` | 특정 오브젝트 상세 (메시, 머티리얼, 바운딩박스) |

### 오브젝트 조작
| 명령 | 파라미터 | 설명 |
|------|----------|------|
| `create_object` | `type`, `name?`, `location?`, `scale?` | 기본 메시 생성 (CUBE/SPHERE/PLANE/CYLINDER/CONE/TORUS/MONKEY) |
| `delete_object` | `name` | 오브젝트 삭제 |
| `modify_object` | `name`, `location?`, `rotation?`, `scale?`, `visible?` | 변환 수정 |

### 머티리얼
| 명령 | 파라미터 | 설명 |
|------|----------|------|
| `set_material` | `object_name`, `color?`, `metallic?`, `roughness?`, `material_name?` | PBR 머티리얼 설정 |

### 렌더링
| 명령 | 파라미터 | 설명 |
|------|----------|------|
| `render_preview` | `output_path?`, `resolution_x?`, `resolution_y?`, `samples?`, `engine?` | 빠른 프리뷰 (512x512, 32 samples) |
| `render_to_file` | `output_path`, `format?`, `resolution_x?`, `resolution_y?`, `samples?`, `engine?` | 고품질 렌더 |

### 파일 관리
| 명령 | 파라미터 | 설명 |
|------|----------|------|
| `save_blend` | `filepath` | .blend 저장 |
| `load_blend` | `filepath` | .blend 로드 |
| `import_model` | `filepath`, `format?` | 모델 임포트 (glTF/FBX/OBJ/STL/PLY) |
| `export_model` | `filepath`, `format?`, `selected_only?` | 모델 내보내기 |
| `clear_scene` | `keep_camera?`, `keep_lights?` | 씬 초기화 |

### 코드 실행
| 명령 | 파라미터 | 설명 |
|------|----------|------|
| `execute_code` | `code` | 임의 Python 코드 실행 (최대 유연성) |

## Poly Haven 에셋 통합

CC0 무료 에셋 (HDRI, 텍스처, 3D 모델) 검색/다운로드.

```bash
# 텍스처 카테고리 조회
nodes.run(node="MiniPC", command=[
    "python3", "/home/spritz/blender-interactive/scripts/polyhaven.py",
    "categories", "textures"
])

# 벽돌 텍스처 검색
nodes.run(node="MiniPC", command=[
    "python3", "/home/spritz/blender-interactive/scripts/polyhaven.py",
    "search", "--type", "textures", "--categories", "brick"
])

# 텍스처 다운로드 (1k 해상도)
nodes.run(node="MiniPC", command=[
    "python3", "/home/spritz/blender-interactive/scripts/polyhaven.py",
    "download", "rock_wall_08", "--type", "textures", "--resolution", "1k",
    "--output", "/tmp/polyhaven/textures/"
])

# HDRI 다운로드
nodes.run(node="MiniPC", command=[
    "python3", "/home/spritz/blender-interactive/scripts/polyhaven.py",
    "download", "meadow", "--type", "hdris", "--resolution", "2k",
    "--format", "hdr", "--output", "/tmp/polyhaven/hdri/"
])

# 3D 모델 다운로드
nodes.run(node="MiniPC", command=[
    "python3", "/home/spritz/blender-interactive/scripts/polyhaven.py",
    "download", "food_apple_01", "--type", "models", "--resolution", "1k",
    "--format", "gltf", "--output", "/tmp/polyhaven/models/"
])
```

### Poly Haven + Blender 통합 워크플로우

```bash
# 1. 텍스처 다운로드
polyhaven.py download rock_wall_08 --type textures --resolution 1k --output /tmp/ph/

# 2. Blender에서 평면 생성 + 텍스처 적용 (execute_code 사용)
blender_client.py execute_code --params '{
  "code": "import bpy\nimport os\n\n# 평면 생성\nbpy.ops.mesh.primitive_plane_add(size=10)\nplane = bpy.context.active_object\nplane.name = \"Ground\"\n\n# 머티리얼 + 텍스처\nmat = bpy.data.materials.new(\"RockWall\")\nmat.use_nodes = True\nnodes = mat.node_tree.nodes\nlinks = mat.node_tree.links\n\nbsdf = nodes[\"Principled BSDF\"]\ntex = nodes.new(\"ShaderNodeTexImage\")\ntex.image = bpy.data.images.load(\"/tmp/ph/rock_wall_08_Diffuse_1k.jpg\")\nlinks.new(tex.outputs[\"Color\"], bsdf.inputs[\"Base Color\"])\n\nplane.data.materials.append(mat)"
}'
```

## 프로토콜 상세

### 요청 형식
```json
{
  "type": "command_name",
  "params": {
    "key": "value"
  }
}
```

### 응답 형식
```json
{
  "status": "success",
  "result": { ... }
}
```

```json
{
  "status": "error",
  "message": "Error description"
}
```

### 통신 방식
- **전송:** TCP 소켓, JSON over TCP
- **포트:** 9876 (기본)
- **타임아웃:** 300초 (렌더링 등 대비)
- **스레드 안전:** 명령은 Blender 메인 스레드에서 실행 (bpy.app.timers)
- **동시 접속:** 다중 클라이언트 지원 (순차 처리)

## MiniPC 배포

### 파일 전송 (맥스튜디오 → MiniPC)

```bash
# 1. 스킬 폴더를 MiniPC에 복사
# nodes.run으로 base64 전송 또는 scp
scp -r skills/blender-interactive/ spritz@100.80.169.94:/home/spritz/blender-interactive/
```

### 자동 시작 (systemd)

```ini
# /home/spritz/.config/systemd/user/blender-socket.service
[Unit]
Description=Blender Interactive Socket Server
After=network.target

[Service]
Type=simple
ExecStart=/snap/bin/blender -b --factory-startup --python /home/spritz/blender-interactive/blender_socket_addon.py -- --port 9876
ExecStop=/bin/kill -TERM $MAINPID
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable blender-socket
systemctl --user start blender-socket
```

## 제한사항

### Headless 제한
- **뷰포트 스크린샷 불가** — 대신 `render_preview`로 Cycles CPU 렌더링 (느리지만 정확)
- **EEVEE 불가** — headless에서 GPU 필요. Cycles CPU만 사용
- **실시간 미리보기 없음** — 렌더링 결과로 확인

### 성능
- **MiniPC (8GB RAM)** — 로우폴리 씬 권장. 복잡한 씬은 메모리 부족 가능
- **Cycles CPU 렌더** — 512x512, 32 samples ≈ 5-15초
- **대용량 Poly Haven 에셋** — 4k 텍스처는 RAM 부담. 1k-2k 권장

### 보안
- `execute_code`는 임의 코드 실행 가능 — 우리 환경(제어된 MiniPC)에서는 OK
- 외부 노출 시 `--host 127.0.0.1`로 로컬만 바인딩

## 파일 구조

```
blender-interactive/
├── SKILL.md                       # 이 문서
├── blender_socket_addon.py        # Blender 소켓 서버 (핵심)
└── scripts/
    ├── blender_client.py          # 명령 전송 클라이언트
    ├── polyhaven.py               # Poly Haven API 클라이언트
    └── start_server.sh            # 서버 시작/중지 스크립트
```
