#!/usr/bin/env python3
"""
Blender Interactive Socket Server — headless 환경용
Blender 내부에서 실행되어 TCP 소켓으로 외부 명령을 수신/실행.

사용법:
  blender -b --python blender_socket_addon.py -- --port 9876

영감: 소켓 기반 양방향 통신 패턴 (자체 구현, 외부 코드 무관)
환경: MiniPC Linux headless, Blender 5.0.1
"""

import bpy
import json
import socket
import threading
import traceback
import sys
import os
import io
import time
import signal
from contextlib import redirect_stdout


# ─── 설정 ───

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 9876
RECV_BUFFER = 16384
MAX_RESPONSE_SIZE = 10 * 1024 * 1024  # 10MB
SOCKET_TIMEOUT = 300  # 5분 (렌더링 등 오래 걸리는 작업 대비)


def parse_args():
    """Blender -- 뒤의 인자 파싱"""
    argv = sys.argv
    if "--" in argv:
        custom = argv[argv.index("--") + 1:]
    else:
        custom = []

    host = DEFAULT_HOST
    port = DEFAULT_PORT

    i = 0
    while i < len(custom):
        if custom[i] == "--host" and i + 1 < len(custom):
            host = custom[i + 1]
            i += 2
        elif custom[i] == "--port" and i + 1 < len(custom):
            port = int(custom[i + 1])
            i += 2
        else:
            i += 1

    return host, port


# ─── 명령 핸들러 ───

class CommandRouter:
    """명령 타입별 핸들러 라우팅"""

    def __init__(self):
        self._handlers = {}

    def register(self, cmd_type):
        """데코레이터로 핸들러 등록"""
        def decorator(fn):
            self._handlers[cmd_type] = fn
            return fn
        return decorator

    def execute(self, command):
        """명령 실행 — 반드시 Blender 메인 스레드에서 호출"""
        cmd_type = command.get("type", "")
        params = command.get("params", {})

        handler = self._handlers.get(cmd_type)
        if not handler:
            available = ", ".join(sorted(self._handlers.keys()))
            return {
                "status": "error",
                "message": f"Unknown command: {cmd_type}. Available: {available}"
            }

        try:
            result = handler(**params)
            return {"status": "success", "result": result}
        except Exception as exc:
            traceback.print_exc()
            return {"status": "error", "message": str(exc)}

    def list_commands(self):
        """등록된 명령 목록"""
        return sorted(self._handlers.keys())


router = CommandRouter()


# ─── 씬 조회 명령 ───

@router.register("ping")
def cmd_ping():
    """서버 상태 확인"""
    return {
        "alive": True,
        "blender_version": bpy.app.version_string,
        "scene": bpy.context.scene.name,
        "uptime_commands": list(router.list_commands()),
    }


@router.register("get_scene_info")
def cmd_get_scene_info():
    """현재 씬의 오브젝트, 머티리얼, 카메라 등 정보"""
    scene = bpy.context.scene

    objects = []
    for obj in scene.objects:
        obj_data = {
            "name": obj.name,
            "type": obj.type,
            "location": [round(v, 4) for v in obj.location],
            "rotation": [round(v, 4) for v in obj.rotation_euler],
            "scale": [round(v, 4) for v in obj.scale],
            "visible": obj.visible_get(),
        }
        if obj.type == "MESH" and obj.data:
            mesh = obj.data
            obj_data["mesh"] = {
                "vertices": len(mesh.vertices),
                "edges": len(mesh.edges),
                "polygons": len(mesh.polygons),
            }
        if obj.material_slots:
            obj_data["materials"] = [
                s.material.name for s in obj.material_slots if s.material
            ]
        objects.append(obj_data)

    cameras = [o.name for o in scene.objects if o.type == "CAMERA"]
    lights = [
        {"name": o.name, "type": o.data.type if o.data else "UNKNOWN"}
        for o in scene.objects if o.type == "LIGHT"
    ]

    return {
        "scene_name": scene.name,
        "object_count": len(scene.objects),
        "objects": objects,
        "cameras": cameras,
        "lights": lights,
        "materials_count": len(bpy.data.materials),
        "frame_current": scene.frame_current,
        "frame_range": [scene.frame_start, scene.frame_end],
        "render_engine": scene.render.engine,
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
    }


@router.register("get_object_info")
def cmd_get_object_info(name):
    """특정 오브젝트의 상세 정보"""
    obj = bpy.data.objects.get(name)
    if not obj:
        raise ValueError(f"Object not found: {name}")

    info = {
        "name": obj.name,
        "type": obj.type,
        "location": list(obj.location),
        "rotation_euler": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "visible": obj.visible_get(),
        "parent": obj.parent.name if obj.parent else None,
        "children": [c.name for c in obj.children],
        "materials": [],
    }

    for slot in obj.material_slots:
        if slot.material:
            mat = slot.material
            info["materials"].append({
                "name": mat.name,
                "use_nodes": mat.use_nodes,
            })

    if obj.type == "MESH" and obj.data:
        mesh = obj.data
        info["mesh"] = {
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "polygons": len(mesh.polygons),
            "has_uv": len(mesh.uv_layers) > 0,
            "uv_layers": [uv.name for uv in mesh.uv_layers],
        }

        # 월드 좌표 바운딩박스
        import mathutils
        corners = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
        mins = [min(c[i] for c in corners) for i in range(3)]
        maxs = [max(c[i] for c in corners) for i in range(3)]
        info["world_bounds"] = {"min": mins, "max": maxs}

    if obj.type == "CAMERA" and obj.data:
        cam = obj.data
        info["camera"] = {
            "lens": cam.lens,
            "sensor_width": cam.sensor_width,
            "clip_start": cam.clip_start,
            "clip_end": cam.clip_end,
            "type": cam.type,
        }

    if obj.type == "LIGHT" and obj.data:
        light = obj.data
        info["light"] = {
            "type": light.type,
            "energy": light.energy,
            "color": list(light.color),
        }

    return info


# ─── 코드 실행 ───

@router.register("execute_code")
def cmd_execute_code(code):
    """임의 Python 코드를 Blender 내부에서 실행"""
    namespace = {"bpy": bpy, "__builtins__": __builtins__}
    capture = io.StringIO()
    with redirect_stdout(capture):
        exec(code, namespace)
    output = capture.getvalue()
    return {"executed": True, "stdout": output}


# ─── 오브젝트 조작 ───

@router.register("create_object")
def cmd_create_object(type="CUBE", name=None, location=None, scale=None):
    """기본 메시 오브젝트 생성"""
    creators = {
        "CUBE": bpy.ops.mesh.primitive_cube_add,
        "SPHERE": bpy.ops.mesh.primitive_uv_sphere_add,
        "PLANE": bpy.ops.mesh.primitive_plane_add,
        "CYLINDER": bpy.ops.mesh.primitive_cylinder_add,
        "CONE": bpy.ops.mesh.primitive_cone_add,
        "TORUS": bpy.ops.mesh.primitive_torus_add,
        "MONKEY": bpy.ops.mesh.primitive_monkey_add,
    }

    creator = creators.get(type.upper())
    if not creator:
        raise ValueError(f"Unknown type: {type}. Available: {list(creators.keys())}")

    kwargs = {}
    if location:
        kwargs["location"] = tuple(location)
    if scale:
        kwargs["scale"] = tuple(scale)

    creator(**kwargs)
    obj = bpy.context.active_object
    if name:
        obj.name = name
    return {"name": obj.name, "type": obj.type, "location": list(obj.location)}


@router.register("delete_object")
def cmd_delete_object(name):
    """오브젝트 삭제"""
    obj = bpy.data.objects.get(name)
    if not obj:
        raise ValueError(f"Object not found: {name}")
    bpy.data.objects.remove(obj, do_unlink=True)
    return {"deleted": name}


@router.register("modify_object")
def cmd_modify_object(name, location=None, rotation=None, scale=None, visible=None):
    """오브젝트 변환 수정"""
    obj = bpy.data.objects.get(name)
    if not obj:
        raise ValueError(f"Object not found: {name}")

    if location is not None:
        obj.location = tuple(location)
    if rotation is not None:
        obj.rotation_euler = tuple(rotation)
    if scale is not None:
        obj.scale = tuple(scale)
    if visible is not None:
        obj.hide_viewport = not visible
        obj.hide_render = not visible

    return {
        "name": obj.name,
        "location": list(obj.location),
        "rotation": list(obj.rotation_euler),
        "scale": list(obj.scale),
    }


# ─── 머티리얼 ───

@router.register("set_material")
def cmd_set_material(object_name, color=None, metallic=None, roughness=None, material_name=None):
    """오브젝트에 머티리얼 설정/생성"""
    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object not found: {object_name}")

    mat_name = material_name or f"{object_name}_material"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True

    # Principled BSDF 찾기
    bsdf = None
    if mat.use_nodes:
        for node in mat.node_tree.nodes:
            if node.type == "BSDF_PRINCIPLED":
                bsdf = node
                break

    if bsdf:
        if color is not None:
            # [R, G, B] 또는 [R, G, B, A]
            if len(color) == 3:
                color = color + [1.0]
            bsdf.inputs["Base Color"].default_value = tuple(color)
        if metallic is not None:
            bsdf.inputs["Metallic"].default_value = metallic
        if roughness is not None:
            bsdf.inputs["Roughness"].default_value = roughness

    # 오브젝트에 머티리얼 할당
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    return {"object": object_name, "material": mat.name}


# ─── 렌더링 (headless용) ───

@router.register("render_preview")
def cmd_render_preview(output_path="/tmp/blender_preview.png",
                       resolution_x=512, resolution_y=512,
                       samples=32, engine="CYCLES"):
    """오프스크린 렌더링으로 프리뷰 이미지 생성 (headless 호환)"""
    scene = bpy.context.scene

    # 렌더 설정
    scene.render.engine = engine
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = output_path

    # Cycles 설정
    if engine == "CYCLES":
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True
        scene.cycles.device = "CPU"

    # 카메라 확인
    if not scene.camera:
        # 카메라 없으면 자동 생성
        cam_data = bpy.data.cameras.new("AutoCamera")
        cam_obj = bpy.data.objects.new("AutoCamera", cam_data)
        bpy.context.collection.objects.link(cam_obj)
        cam_obj.location = (7, -7, 5)
        cam_obj.rotation_euler = (1.1, 0, 0.8)
        scene.camera = cam_obj

    # 렌더
    bpy.ops.render.render(write_still=True)

    return {
        "rendered": True,
        "path": output_path,
        "resolution": [resolution_x, resolution_y],
        "engine": engine,
        "samples": samples,
    }


@router.register("render_to_file")
def cmd_render_to_file(output_path, format="PNG",
                       resolution_x=1920, resolution_y=1080,
                       samples=128, engine="CYCLES"):
    """고품질 렌더링"""
    scene = bpy.context.scene
    scene.render.engine = engine
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = format
    scene.render.filepath = output_path

    if engine == "CYCLES":
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True

    if not scene.camera:
        raise ValueError("No camera in scene. Add a camera first.")

    bpy.ops.render.render(write_still=True)

    return {
        "rendered": True,
        "path": output_path,
        "resolution": [resolution_x, resolution_y],
    }


# ─── 씬 관리 ───

@router.register("clear_scene")
def cmd_clear_scene(keep_camera=True, keep_lights=True):
    """씬 초기화"""
    to_remove = []
    for obj in bpy.data.objects:
        if keep_camera and obj.type == "CAMERA":
            continue
        if keep_lights and obj.type == "LIGHT":
            continue
        to_remove.append(obj)

    for obj in to_remove:
        bpy.data.objects.remove(obj, do_unlink=True)

    # 고아 데이터 정리
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

    return {"cleared": True, "remaining": len(bpy.data.objects)}


@router.register("save_blend")
def cmd_save_blend(filepath):
    """현재 씬을 .blend 파일로 저장"""
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=filepath)
    return {"saved": filepath}


@router.register("load_blend")
def cmd_load_blend(filepath):
    """blend 파일 로드"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    bpy.ops.wm.open_mainfile(filepath=filepath)
    return {"loaded": filepath, "objects": len(bpy.data.objects)}


@router.register("import_model")
def cmd_import_model(filepath, format=None):
    """외부 모델 파일 임포트"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    ext = os.path.splitext(filepath)[1].lower()
    if format:
        ext = f".{format.lower()}"

    before = set(bpy.data.objects.keys())

    if ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=filepath)
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=filepath)
    elif ext == ".obj":
        bpy.ops.wm.obj_import(filepath=filepath)
    elif ext == ".stl":
        bpy.ops.wm.stl_import(filepath=filepath)
    elif ext == ".ply":
        bpy.ops.wm.ply_import(filepath=filepath)
    else:
        raise ValueError(f"Unsupported format: {ext}")

    after = set(bpy.data.objects.keys())
    new_objects = list(after - before)

    return {"imported": filepath, "new_objects": new_objects}


@router.register("export_model")
def cmd_export_model(filepath, format=None, selected_only=False):
    """모델 내보내기"""
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)

    ext = os.path.splitext(filepath)[1].lower()
    if format:
        ext = f".{format.lower()}"

    if ext in (".glb", ".gltf"):
        bpy.ops.export_scene.gltf(
            filepath=filepath,
            use_selection=selected_only,
            export_format="GLB" if ext == ".glb" else "GLTF_SEPARATE",
        )
    elif ext == ".fbx":
        bpy.ops.export_scene.fbx(filepath=filepath, use_selection=selected_only)
    elif ext == ".obj":
        bpy.ops.wm.obj_export(filepath=filepath)
    elif ext == ".stl":
        bpy.ops.wm.stl_export(filepath=filepath)
    else:
        raise ValueError(f"Unsupported export format: {ext}")

    return {"exported": filepath}


# ─── 소켓 서버 ───

class BlenderSocketServer:
    """TCP 소켓 서버 — Blender 메인 스레드와 안전하게 통신"""

    def __init__(self, host, port, router):
        self.host = host
        self.port = port
        self.router = router
        self.running = False
        self.sock = None
        self.thread = None
        self._pending = []  # (command, client_socket) 큐
        self._lock = threading.Lock()

    def start(self):
        if self.running:
            print(f"[BlenderSocket] Already running on {self.host}:{self.port}")
            return

        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(2.0)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)

        self.thread = threading.Thread(target=self._accept_loop, daemon=True)
        self.thread.start()

        print(f"[BlenderSocket] Server started on {self.host}:{self.port}")

    def stop(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None
        print("[BlenderSocket] Server stopped")

    def _accept_loop(self):
        """별도 스레드: 연결 수락 + 데이터 수신"""
        while self.running:
            try:
                client, addr = self.sock.accept()
                print(f"[BlenderSocket] Client connected: {addr}")
                handler = threading.Thread(
                    target=self._client_handler,
                    args=(client, addr),
                    daemon=True,
                )
                handler.start()
            except socket.timeout:
                continue
            except OSError:
                if self.running:
                    traceback.print_exc()
                break

    def _client_handler(self, client, addr):
        """클라이언트 소켓에서 JSON 명령 수신"""
        client.settimeout(SOCKET_TIMEOUT)
        buf = b""

        try:
            while self.running:
                chunk = client.recv(RECV_BUFFER)
                if not chunk:
                    break

                buf += chunk

                # 여러 명령이 한 번에 올 수 있으므로 줄 단위 분리
                # 또는 JSON 완성 시도
                try:
                    command = json.loads(buf.decode("utf-8"))
                    buf = b""

                    # 결과를 받을 이벤트
                    result_event = threading.Event()
                    result_holder = [None]

                    def callback():
                        result_holder[0] = self.router.execute(command)
                        result_event.set()

                    # 메인 스레드 큐에 추가
                    with self._lock:
                        self._pending.append(callback)

                    # 결과 대기
                    result_event.wait(timeout=SOCKET_TIMEOUT)

                    response = result_holder[0]
                    if response is None:
                        response = {"status": "error", "message": "Execution timeout"}

                    resp_bytes = json.dumps(response, ensure_ascii=False).encode("utf-8")
                    client.sendall(resp_bytes)

                except json.JSONDecodeError:
                    # 아직 완전한 JSON이 아님 — 더 기다림
                    if len(buf) > MAX_RESPONSE_SIZE:
                        buf = b""
                        err = {"status": "error", "message": "Request too large"}
                        client.sendall(json.dumps(err).encode("utf-8"))

        except socket.timeout:
            print(f"[BlenderSocket] Client timeout: {addr}")
        except ConnectionResetError:
            print(f"[BlenderSocket] Client disconnected: {addr}")
        except Exception:
            traceback.print_exc()
        finally:
            try:
                client.close()
            except Exception:
                pass
            print(f"[BlenderSocket] Client handler ended: {addr}")

    def _process_pending(self):
        """Blender 메인 스레드에서 실행 — 큐에 쌓인 콜백 처리"""
        with self._lock:
            callbacks = list(self._pending)
            self._pending.clear()

        for cb in callbacks:
            try:
                cb()
            except Exception:
                traceback.print_exc()

        # 서버가 살아있으면 타이머 계속
        if self.running:
            return 0.05  # 50ms 간격으로 재실행
        return None  # 타이머 종료

    def run_blocking(self):
        """headless 모드용 — 메인 스레드에서 블로킹 루프로 명령 처리.
        bpy.app.timers 대신 직접 루프를 돌려서 Blender가 종료하지 않게 함."""
        print("[BlenderSocket] Entering blocking main loop (headless mode)")
        while self.running:
            with self._lock:
                callbacks = list(self._pending)
                self._pending.clear()

            for cb in callbacks:
                try:
                    cb()
                except Exception:
                    traceback.print_exc()

            time.sleep(0.05)


# ─── 메인 ───

def main():
    host, port = parse_args()

    server = BlenderSocketServer(host, port, router)
    server.start()

    print(f"[BlenderSocket] Ready. Commands: {router.list_commands()}")
    print(f"[BlenderSocket] Send JSON to {host}:{port}")
    print(f"[BlenderSocket] Example: {{\"type\": \"ping\"}}")

    # SIGINT/SIGTERM 처리
    def shutdown(signum, frame):
        print(f"\n[BlenderSocket] Received signal {signum}, shutting down...")
        server.stop()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # headless 모드(-b): 블로킹 루프로 Blender가 종료하지 않게 유지.
    # bpy.app.timers는 배치 모드에서 이벤트 루프가 없어 작동하지 않으므로,
    # 메인 스레드에서 직접 명령 큐를 처리하는 루프를 실행.
    server.run_blocking()


if __name__ == "__main__":
    main()
