#!/bin/bash
# Godot 신규 프로젝트 생성 스크립트 (MiniPC용)

set -e

PROJECT_NAME=$1
PROJECT_DIR=${2:-$HOME/godot-projects}

if [ -z "$PROJECT_NAME" ]; then
    echo "Usage: $0 <project_name> [project_dir]"
    echo "Example: $0 MyGame \$HOME/games"
    exit 1
fi

FULL_PATH="$PROJECT_DIR/$PROJECT_NAME"

echo "Creating Godot project: $PROJECT_NAME"
echo "Location: $FULL_PATH"

# 디렉토리 생성
mkdir -p "$FULL_PATH"

# project.godot 생성
cat > "$FULL_PATH/project.godot" << EOF
; Engine configuration file.

config_version=5

[application]

config/name="$PROJECT_NAME"
run/main_scene="res://scenes/main.tscn"
config/features=PackedStringArray("4.6", "Forward Plus")
boot_splash/bg_color=Color(0.141176, 0.141176, 0.141176, 1)
boot_splash/image="res://boot_splash.png"
config/icon="res://icon.svg"

[display]

window/size/viewport_width=1280
window/size/viewport_height=720
window/stretch/mode="canvas_items"

[input]

ui_left={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":65,"key_label":0,"unicode":0,"echo":false,"script":null)
, Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":4194319,"key_label":0,"unicode":0,"echo":false,"script":null)
]
}
ui_right={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":68,"key_label":0,"unicode":0,"echo":false,"script":null)
, Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":4194321,"key_label":0,"unicode":0,"echo":false,"script":null)
]
}
ui_up={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":87,"key_label":0,"unicode":0,"echo":false,"script":null)
, Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":4194320,"key_label":0,"unicode":0,"echo":false,"script":null)
]
}
ui_down={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":83,"key_label":0,"unicode":0,"echo":false,"script":null)
, Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":4194322,"key_label":0,"unicode":0,"echo":false,"script":null)
]
}

[rendering]

textures/canvas_textures/default_texture_filter=0
EOF

# 폴더 구조 생성
mkdir -p "$FULL_PATH"/{scenes,scripts,assets/{sprites,sounds,fonts}}

# East Sea Games 부트 스플래시 복사 (있을 경우)
if [ -f "$HOME/godot-demo/boot_splash.png" ]; then
    cp "$HOME/godot-demo/boot_splash.png" "$FULL_PATH/"
    echo "✓ Copied East Sea Games boot splash"
fi

# 기본 아이콘 생성 (SVG)
cat > "$FULL_PATH/icon.svg" << 'EOF'
<svg height="128" width="128" xmlns="http://www.w3.org/2000/svg">
  <rect fill="#4a90e2" height="128" rx="16" width="128"/>
  <text fill="#ffffff" font-family="Arial" font-size="80" font-weight="bold" text-anchor="middle" x="64" y="95">G</text>
</svg>
EOF

echo "✓ Project created successfully!"
echo ""
echo "Next steps:"
echo "  cd $FULL_PATH"
echo "  godot4 -e .  # Open in editor"
echo "  godot4 .     # Run project"
