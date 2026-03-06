#!/bin/bash
# ==============================================
#  MiniTimeBot macOS 打包脚本
#  生成 .app 应用包 + DMG/tar.gz
#  用法: bash packaging/build_dmg.sh
# ==============================================

set -e

# ---- 配置 ----
APP_NAME="MiniTimeBot"
VERSION="1.0.0"
BUNDLE_ID="com.minitimebot.app"
DMG_NAME="${APP_NAME}_${VERSION}.dmg"

# 项目根目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="${ROOT}/build/dmg"
APP_BUNDLE="${BUILD_DIR}/${APP_NAME}.app"
OUTPUT_DIR="${ROOT}/dist"

echo "============================================"
echo "  ${APP_NAME} macOS 打包工具 v${VERSION}"
echo "  生成 .app 应用包"
echo "============================================"
echo ""

# ---- 1. 检查运行平台 ----
if [[ "$(uname)" != "Darwin" ]]; then
    echo "⚠️  当前系统非 macOS ($(uname))，将生成 tar.gz 替代 DMG"
    echo "   DMG 格式仅支持在 macOS 上构建"
    echo "   .app 结构仍然会正确生成"
    USE_TAR=true
else
    USE_TAR=false
    if ! command -v hdiutil &>/dev/null; then
        echo "❌ 未找到 hdiutil，请确认 macOS 环境"
        exit 1
    fi
fi

# ---- 2. 清理旧构建 ----
echo "🧹 清理旧构建..."
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"
mkdir -p "${OUTPUT_DIR}"

# ---- 3. 构建 .app 应用包结构 ----
echo "📱 构建 ${APP_NAME}.app ..."

# macOS .app 标准目录结构
CONTENTS="${APP_BUNDLE}/Contents"
MACOS_DIR="${CONTENTS}/MacOS"
RESOURCES="${CONTENTS}/Resources"

mkdir -p "${MACOS_DIR}"
mkdir -p "${RESOURCES}"

# ---- 3a. 创建 Info.plist（应用元数据）----
cat > "${CONTENTS}/Info.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleDisplayName</key>
    <string>Mini TimeBot</string>
    <key>CFBundleIdentifier</key>
    <string>${BUNDLE_ID}</string>
    <key>CFBundleVersion</key>
    <string>${VERSION}</string>
    <key>CFBundleShortVersionString</key>
    <string>${VERSION}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>CFBundleExecutable</key>
    <string>launch</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.productivity</string>
    <key>NSAppleEventsUsageDescription</key>
    <string>MiniTimeBot 需要控制终端来启动服务</string>
</dict>
</plist>
PLIST

echo "  ✅ Info.plist"

# ---- 3b. 创建启动器脚本（Contents/MacOS/launch）----
cat > "${MACOS_DIR}/launch" << 'LAUNCHER'
#!/bin/bash
# MiniTimeBot .app 启动器
# 双击 .app 时 macOS 会执行此脚本

# 获取 Resources 目录（项目文件所在位置）
RESOURCES_DIR="$(dirname "$0")/../Resources"
RESOURCES_DIR="$(cd "$RESOURCES_DIR" && pwd)"

# 在 Terminal.app 中打开并运行 run.sh
osascript <<EOF
tell application "Terminal"
    activate
    do script "cd '${RESOURCES_DIR}' && bash run.sh"
end tell
EOF
LAUNCHER
chmod +x "${MACOS_DIR}/launch"
echo "  ✅ 启动器 (MacOS/launch)"

# ---- 3c. 复制项目文件到 Resources ----
echo "  📦 复制项目文件到 Resources..."

# 核心脚本
cp "${ROOT}/run.sh" "${RESOURCES}/"
chmod +x "${RESOURCES}/run.sh"

# scripts 目录（.sh + .py）
mkdir -p "${RESOURCES}/scripts"
for f in setup_env.sh start.sh adduser.sh setup_apikey.sh tunnel.sh tunnel.py launcher.py; do
    if [ -f "${ROOT}/scripts/${f}" ]; then
        cp "${ROOT}/scripts/${f}" "${RESOURCES}/scripts/"
        chmod +x "${RESOURCES}/scripts/${f}"
    fi
done

# 源码
cp -r "${ROOT}/src" "${RESOURCES}/src"

# 工具
if [ -d "${ROOT}/tools" ]; then
    cp -r "${ROOT}/tools" "${RESOURCES}/tools"
fi

# OASIS 论坛模块
if [ -d "${ROOT}/oasis" ]; then
    cp -r "${ROOT}/oasis" "${RESOURCES}/oasis"
fi

# 配置模板
mkdir -p "${RESOURCES}/config"
cp "${ROOT}/config/requirements.txt" "${RESOURCES}/config/"
[ -f "${ROOT}/config/.env.example" ] && cp "${ROOT}/config/.env.example" "${RESOURCES}/config/"
[ -f "${ROOT}/config/users.json.example" ] && cp "${ROOT}/config/users.json.example" "${RESOURCES}/config/"

# 数据目录结构
mkdir -p "${RESOURCES}/data/timeset"
mkdir -p "${RESOURCES}/data/user_files"
mkdir -p "${RESOURCES}/data/bark"
mkdir -p "${RESOURCES}/data/oasis_user_experts"

# 核心数据：prompts（系统 prompt + 专家定义，必需）
if [ -d "${ROOT}/data/prompts" ]; then
    cp -r "${ROOT}/data/prompts" "${RESOURCES}/data/prompts"
fi

# 调度示例模板
if [ -d "${ROOT}/data/schedules" ]; then
    cp -r "${ROOT}/data/schedules" "${RESOURCES}/data/schedules"
fi

# 许可证
[ -f "${ROOT}/LICENSE" ] && cp "${ROOT}/LICENSE" "${RESOURCES}/"

echo "  ✅ 项目文件复制完成"

# ---- 3d. 生成应用图标 ----
ICON_SRC="${ROOT}/packaging/icon.png"
if [ -f "$ICON_SRC" ]; then
    if [[ "$(uname)" == "Darwin" ]]; then
        # macOS: 用 sips + iconutil 生成标准 .icns
        echo "  🎨 生成应用图标 (.icns)..."
        ICONSET="${BUILD_DIR}/AppIcon.iconset"
        mkdir -p "$ICONSET"
        for size in 16 32 64 128 256 512; do
            sips -z $size $size "$ICON_SRC" --out "${ICONSET}/icon_${size}x${size}.png" &>/dev/null
            double=$((size * 2))
            sips -z $double $double "$ICON_SRC" --out "${ICONSET}/icon_${size}x${size}@2x.png" &>/dev/null
        done
        iconutil -c icns "$ICONSET" -o "${RESOURCES}/AppIcon.icns"
        rm -rf "$ICONSET"
        echo "  ✅ 应用图标已生成 (icns)"
    else
        # Linux: 尝试用 Pillow 生成 .icns，回退则直接复制 PNG
        echo "  🎨 处理应用图标..."
        if python3 -c "
from PIL import Image
import struct, io

img = Image.open('${ICON_SRC}').convert('RGBA')
sizes = [(16,'icp4'), (32,'icp5'), (64,'icp6'), (128,'ic07'), (256,'ic08'), (512,'ic09')]
entries = []
for sz, ostype in sizes:
    resized = img.resize((sz, sz), Image.LANCZOS)
    buf = io.BytesIO()
    resized.save(buf, format='PNG')
    data = buf.getvalue()
    entry = ostype.encode('ascii') + struct.pack('>I', len(data) + 8) + data
    entries.append(entry)

body = b''.join(entries)
header = b'icns' + struct.pack('>I', len(body) + 8)
with open('${RESOURCES}/AppIcon.icns', 'wb') as f:
    f.write(header + body)
print('ok')
" 2>/dev/null; then
            echo "  ✅ 应用图标已生成 (icns via Pillow)"
        else
            # 最后回退：直接复制 PNG 作为图标
            cp "$ICON_SRC" "${RESOURCES}/AppIcon.png"
            echo "  ✅ 应用图标已复制 (png fallback)"
        fi
    fi
else
    echo "  ℹ️  未找到 packaging/icon.png，使用默认图标"
    echo "     提示：放一张正方形 PNG 到 packaging/icon.png 可自定义图标"
fi

# ---- 3e. 生成使用说明 ----
cat > "${BUILD_DIR}/使用说明.txt" << 'GUIDE'
==========================================
  MiniTimeBot macOS 使用说明
==========================================

【安装】
  将 MiniTimeBot.app 拖到「应用程序」文件夹
  （或任意你喜欢的位置）

【首次启动】
  1. 双击 MiniTimeBot.app
  2. 如果弹出"无法验证开发者"提示：
     → 右键点击 app → 选择「打开」→ 点击「打开」
     → 或在终端执行: xattr -cr /path/to/MiniTimeBot.app
  3. 首次运行会自动在终端中打开，按提示配置

【日常启动】
  双击 MiniTimeBot.app 即可

【访问地址】
  启动后浏览器打开: http://127.0.0.1:51209
  （端口可在 config/.env 中自定义 PORT_FRONTEND）

【停止服务】
  在终端中按 Ctrl+C

==========================================
GUIDE

echo ""
echo "📱 ${APP_NAME}.app 构建完成！"
echo "   结构:"
echo "   ${APP_NAME}.app/"
echo "   └── Contents/"
echo "       ├── Info.plist"
echo "       ├── MacOS/launch      ← 启动器"
echo "       └── Resources/        ← 项目文件"
echo ""

# ---- 4. 生成安装包 ----
if [ "$USE_TAR" = true ]; then
    # 非 macOS 环境：生成 tar.gz（保留 .app 目录结构）
    ARCHIVE_NAME="${APP_NAME}_${VERSION}_macos.tar.gz"
    echo "📦 生成 ${ARCHIVE_NAME}..."
    cd "${BUILD_DIR}"
    tar -czf "${OUTPUT_DIR}/${ARCHIVE_NAME}" "${APP_NAME}.app" "使用说明.txt"
    cd "${ROOT}"

    FINAL_PATH="${OUTPUT_DIR}/${ARCHIVE_NAME}"
    echo ""
    echo "============================================"
    echo "  ✅ 打包完成！"
    echo "  📦 文件: ${FINAL_PATH}"
    echo "  📏 大小: $(du -sh "${FINAL_PATH}" | cut -f1)"
    echo ""
    echo "  包含: ${APP_NAME}.app + 使用说明.txt"
    echo ""
    echo "  macOS 用户使用方式："
    echo "  1. 解压 tar.gz"
    echo "  2. 将 ${APP_NAME}.app 拖到「应用程序」文件夹"
    echo "  3. 首次打开：右键 → 打开（绕过 Gatekeeper）"
    echo "  4. 双击即可启动"
    echo ""
    echo "  ⚠️  在 macOS 上运行此脚本可生成 .dmg 格式"
    echo "============================================"
else
    # macOS 环境：生成 DMG
    DMG_PATH="${OUTPUT_DIR}/${DMG_NAME}"
    rm -f "${DMG_PATH}"

    echo "💿 创建 DMG: ${DMG_NAME}..."

    # 创建 DMG 内容目录（包含 .app 和 Applications 快捷方式）
    DMG_CONTENT="${BUILD_DIR}/dmg_content"
    mkdir -p "${DMG_CONTENT}"
    cp -r "${APP_BUNDLE}" "${DMG_CONTENT}/"
    cp "${BUILD_DIR}/使用说明.txt" "${DMG_CONTENT}/"

    # 创建 Applications 文件夹的符号链接（方便用户拖拽安装）
    ln -s /Applications "${DMG_CONTENT}/Applications"

    # 计算所需空间
    SIZE_KB=$(du -sk "${DMG_CONTENT}" | cut -f1)
    SIZE_MB=$(( (SIZE_KB / 1024) + 10 ))

    # 创建临时 DMG
    TEMP_DMG="${BUILD_DIR}/temp.dmg"
    hdiutil create \
        -srcfolder "${DMG_CONTENT}" \
        -volname "${APP_NAME}" \
        -fs HFS+ \
        -fsargs "-c c=64,a=16,e=16" \
        -format UDRW \
        -size "${SIZE_MB}m" \
        "${TEMP_DMG}"

    # 挂载临时 DMG
    MOUNT_DIR=$(hdiutil attach -readwrite -noverify -noautoopen "${TEMP_DMG}" | \
        grep "/Volumes/" | sed 's/.*\/Volumes/\/Volumes/')

    # 设置 DMG 窗口样式
    echo "🎨 设置 DMG 窗口样式..."
    osascript << EOF
tell application "Finder"
    tell disk "${APP_NAME}"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {200, 120, 800, 460}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 100
        -- 排列图标位置：左边 app，右边 Applications
        set position of item "${APP_NAME}.app" of container window to {180, 160}
        set position of item "Applications" of container window to {420, 160}
        close
    end tell
end tell
EOF

    # 卸载
    hdiutil detach "${MOUNT_DIR}" -quiet

    # 压缩为最终 DMG
    hdiutil convert "${TEMP_DMG}" \
        -format UDZO \
        -imagekey zlib-level=9 \
        -o "${DMG_PATH}"

    rm -f "${TEMP_DMG}"

    echo ""
    echo "============================================"
    echo "  ✅ DMG 打包完成！"
    echo "  💿 文件: ${DMG_PATH}"
    echo "  📏 大小: $(du -sh "${DMG_PATH}" | cut -f1)"
    echo ""
    echo "  用户使用方式："
    echo "  1. 双击 .dmg 挂载"
    echo "  2. 将 ${APP_NAME}.app 拖到 Applications"
    echo "  3. 首次打开：右键 → 打开"
    echo "  4. 之后双击图标即可启动"
    echo "============================================"
fi

# ---- 5. 清理暂存目录 ----
echo ""
echo "🧹 清理暂存文件..."
rm -rf "${BUILD_DIR}"
echo "✅ 完成"
