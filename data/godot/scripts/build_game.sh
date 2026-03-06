#!/bin/bash
# Godot 게임 빌드 스크립트 (헤드리스 모드)

set -e

PROJECT_PATH=${1:-.}
EXPORT_PRESET=${2:-Web}
OUTPUT_DIR=${3:-export}

if [ ! -f "$PROJECT_PATH/project.godot" ]; then
    echo "Error: project.godot not found in $PROJECT_PATH"
    exit 1
fi

echo "Building Godot project..."
echo "  Project: $PROJECT_PATH"
echo "  Preset: $EXPORT_PRESET"
echo "  Output: $OUTPUT_DIR"

# export_presets.cfg 생성 (없을 경우)
PRESETS_FILE="$PROJECT_PATH/export_presets.cfg"
if [ ! -f "$PRESETS_FILE" ]; then
    echo "Creating export_presets.cfg..."
    cat > "$PRESETS_FILE" << 'EOF'
[preset.0]

name="Web"
platform="Web"
runnable=true
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="export/web/index.html"
encryption_include_filters=""
encryption_exclude_filters=""
encrypt_pck=false
encrypt_directory=false

[preset.0.options]

custom_template/debug=""
custom_template/release=""
variant/extensions_support=false
vram_texture_compression/for_desktop=true
vram_texture_compression/for_mobile=false
html/export_icon=true
html/custom_html_shell=""
html/head_include=""
html/canvas_resize_policy=2
html/focus_canvas_on_start=true
html/experimental_virtual_keyboard=false
progressive_web_app/enabled=false
progressive_web_app/offline_page=""
progressive_web_app/display=1
progressive_web_app/orientation=0
progressive_web_app/icon_144x144=""
progressive_web_app/icon_180x180=""
progressive_web_app/icon_512x512=""
progressive_web_app/background_color=Color(0, 0, 0, 1)

[preset.1]

name="Linux"
platform="Linux/X11"
runnable=true
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="export/linux/game.x86_64"
encryption_include_filters=""
encryption_exclude_filters=""
encrypt_pck=false
encrypt_directory=false

[preset.1.options]

custom_template/debug=""
custom_template/release=""
debug/export_console_wrapper=1
binary_format/embed_pck=false
texture_format/bptc=true
texture_format/s3tc=true
texture_format/etc=false
texture_format/etc2=false
binary_format/architecture="x86_64"
ssh_remote_deploy/enabled=false
ssh_remote_deploy/host="user@host_ip"
ssh_remote_deploy/port="22"
ssh_remote_deploy/extra_args_ssh=""
ssh_remote_deploy/extra_args_scp=""
ssh_remote_deploy/run_script="#!/usr/bin/env bash
export DISPLAY=:0
unzip -o -q \"{temp_dir}/{archive_name}\" -d \"{temp_dir}\"
\"{temp_dir}/{exe_name}\" {cmd_args}"
ssh_remote_deploy/cleanup_script="#!/usr/bin/env bash
kill $(pgrep -x -f \"{temp_dir}/{exe_name} {cmd_args}\")
rm -rf \"{temp_dir}\""

[preset.2]

name="Android"
platform="Android"
runnable=true
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="export/android/game.apk"
encryption_include_filters=""
encryption_exclude_filters=""
encrypt_pck=false
encrypt_directory=false

[preset.2.options]

custom_template/debug=""
custom_template/release=""
gradle_build/use_gradle_build=true
gradle_build/export_format=0
gradle_build/min_sdk=""
gradle_build/target_sdk=""
architectures/armeabi-v7a=false
architectures/arm64-v8a=true
architectures/x86=false
architectures/x86_64=false
version/code=1
version/name="1.0"
package/unique_name="com.eastsea.game"
package/name=""
package/signed=true
launcher_icons/main_192x192=""
launcher_icons/adaptive_foreground_432x432=""
launcher_icons/adaptive_background_432x432=""
EOF
    echo "✓ Created export_presets.cfg"
fi

# 출력 디렉토리 생성
mkdir -p "$OUTPUT_DIR"

# 빌드 실행
case "$EXPORT_PRESET" in
    Web|web)
        echo "Building for Web..."
        "$HOME/godot4/Godot_v4.6-stable_linux.x86_64" --headless --path "$PROJECT_PATH" --export-release "Web" "$OUTPUT_DIR/web/index.html"
        echo "✓ Web build complete: $OUTPUT_DIR/web/index.html"
        ;;
    Linux|linux)
        echo "Building for Linux..."
        "$HOME/godot4/Godot_v4.6-stable_linux.x86_64" --headless --path "$PROJECT_PATH" --export-release "Linux" "$OUTPUT_DIR/linux/game.x86_64"
        echo "✓ Linux build complete: $OUTPUT_DIR/linux/game.x86_64"
        ;;
    Android|android)
        echo "Building for Android..."
        "$HOME/godot4/Godot_v4.6-stable_linux.x86_64" --headless --path "$PROJECT_PATH" --export-release "Android" "$OUTPUT_DIR/android/game.apk"
        echo "✓ Android build complete: $OUTPUT_DIR/android/game.apk"
        ;;
    *)
        echo "Error: Unknown preset '$EXPORT_PRESET'"
        echo "Available presets: Web, Linux, Android"
        exit 1
        ;;
esac

echo ""
echo "Build complete!"
