#!/bin/bash

# 字幕下载脚本（含备选方案）
# 用途：自动为视频文件下载匹配的字幕
# 支持：subliminal / subfinder / OpenSubtitles API

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$(dirname "$SCRIPT_DIR")/config"

# OpenSubtitles API 配置（可选）
OPENSUBTITLES_API_KEY="${OPENSUBTITLES_API_KEY:-}"
OPENSUBTITLES_API="https://api.opensubtitles.com/api/v1"

# 如果没有环境变量，尝试从配置文件读取
if [[ -z "$OPENSUBTITLES_API_KEY" && -f "$CONFIG_DIR/opensubtitles.key" ]]; then
    OPENSUBTITLES_API_KEY=$(cat "$CONFIG_DIR/opensubtitles.key" | tr -d '[:space:]')
fi

# 默认语言：中文简体 + 英文
DEFAULT_LANGUAGES="zh-cn,en"

# 帮助信息
usage() {
    echo "用法: subtitle-download.sh [选项]"
    echo ""
    echo "选项："
    echo "  -f, --file <文件>      单个视频文件路径"
    echo "  -d, --directory <目录> 批量处理目录下的所有视频"
    echo "  -l, --languages <语言> 字幕语言，逗号分隔 (默认: $DEFAULT_LANGUAGES)"
    echo "  -k, --api-key <key>    OpenSubtitles API Key（可选）"
    echo "  -r, --recursive        递归处理子目录"
    echo "  --subliminal           强制使用 subliminal（推荐，无需API）"
    echo "  --subfinder            强制使用 subfinder（备选）"
    echo "  -h, --help             显示帮助信息"
    echo ""
    echo "语言代码："
    echo "  zh       中文（自动简/繁）"
    echo "  zh-cn    中文简体"
    echo "  zh-tw    中文繁体"
    echo "  en       英文"
    echo "  ja       日文"
    echo "  ko       韩文"
    echo ""
    echo "示例："
    echo "  subtitle-download.sh -f \"/path/to/movie.mkv\""
    echo "  subtitle-download.sh -d \"/path/to/tv/show\" -l zh,en"
    echo "  subtitle-download.sh -f \"video.mkv\" --subliminal"
    exit 1
}

# 检查 subliminal 是否安装
check_subliminal() {
    command -v subliminal >/dev/null 2>&1
}

# 检查 subfinder 是否安装
check_subfinder() {
    command -v subfinder >/dev/null 2>&1
}

# 解析视频文件名，提取剧集信息
parse_video_filename() {
    local filename="$1"
    local basename=$(basename "$filename")
    
    # 初始化变量
    local series_name=""
    local season=""
    local episode=""
    local year=""
    
    # 尝试匹配 TV 剧集格式: Name.S01E05.xxx 或 Name.S01E05E06.xxx
    if [[ "$basename" =~ ([^.]+)[.\s_-]*[Ss]([0-9]+)[Ee]([0-9]+) ]]; then
        series_name="${BASH_REMATCH[1]}"
        season="${BASH_REMATCH[2]}"
        episode="${BASH_REMATCH[3]}"
    # 尝试匹配: Name.1x05.xxx
    elif [[ "$basename" =~ ([^.]+)[.\s_-]*([0-9]+)x([0-9]+) ]]; then
        series_name="${BASH_REMATCH[1]}"
        season="${BASH_REMATCH[2]}"
        episode="${BASH_REMATCH[3]}"
    # 尝试匹配电影格式: Movie.Name.2023.xxx
    elif [[ "$basename" =~ ([^.]+\.[^.]+)\.([0-9]{4}) ]]; then
        series_name="${BASH_REMATCH[1]}"
        year="${BASH_REMATCH[2]}"
    # 默认使用文件名（去掉扩展名）
    else
        series_name="${basename%.*}"
    fi
    
    # 清理剧名中的点，替换为空格
    series_name=$(echo "$series_name" | sed 's/\./ /g' | sed 's/_/ /g' | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
    
    echo "$series_name|$season|$episode|$year"
}

# 转换语言代码到 subliminal 格式
convert_lang_to_subliminal() {
    local lang="$1"
    case "$lang" in
        zh|zh-cn|zh_cn) echo "zho" ;;
        zh-tw|zh_tw|zht) echo "zht" ;;
        en) echo "eng" ;;
        ja|jp) echo "jpn" ;;
        ko) echo "kor" ;;
        fr) echo "fra" ;;
        de) echo "deu" ;;
        es) echo "spa" ;;
        it) echo "ita" ;;
        ru) echo "rus" ;;
        *) echo "$lang" ;;
    esac
}

# 使用 subliminal 下载字幕
download_with_subliminal() {
    local video_file="$1"
    local languages="$2"
    
    echo "   🛠️  使用 subliminal 下载字幕..."
    
    # 转换语言代码
    local subliminal_langs=""
    IFS=',' read -ra LANG_ARRAY <<< "$languages"
    for lang in "${LANG_ARRAY[@]}"; do
        local subliminal_lang=$(convert_lang_to_subliminal "$lang")
        subliminal_langs="$subliminal_langs -l $subliminal_lang"
    done
    
    # 运行 subliminal
    if subliminal download $subliminal_langs "$video_file" 2>/dev/null; then
        echo "   ✅ 字幕下载成功"
        return 0
    else
        echo "   ❌ subliminal 下载失败"
        return 1
    fi
}

# 使用 subfinder 下载字幕
download_with_subfinder() {
    local video_file="$1"
    local languages="$2"
    
    echo "   🛠️  使用 subfinder 下载字幕..."
    
    # subfinder 使用 --help 查看参数
    # 基本用法: subfinder -v video.mkv
    if subfinder -v "$video_file" 2>/dev/null; then
        echo "   ✅ 字幕下载成功"
        return 0
    else
        echo "   ❌ subfinder 下载失败"
        return 1
    fi
}

# 搜索 OpenSubtitles
search_opensubtitles() {
    local query="$1"
    local season="$2"
    local episode="$3"
    local languages="$4"
    
    local search_url="$OPENSUBTITLES_API/subtitles"
    local params="query=$(echo "$query" | jq -sRr @uri)"
    
    if [[ -n "$season" ]]; then
        params="$params&season_number=$season"
    fi
    
    if [[ -n "$episode" ]]; then
        params="$params&episode_number=$episode"
    fi
    
    if [[ -n "$languages" ]]; then
        params="$params&languages=$languages"
    fi
    
    curl -s -X GET "$search_url?$params" \
        -H "Api-Key: $OPENSUBTITLES_API_KEY" \
        -H "Content-Type: application/json" 2>/dev/null
}

# 从 OpenSubtitles 下载
download_from_opensubtitles() {
    local file_id="$1"
    local output_path="$2"
    
    local download_response=$(curl -s -X POST "$OPENSUBTITLES_API/download" \
        -H "Api-Key: $OPENSUBTITLES_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"file_id\": $file_id}" 2>/dev/null)
    
    local download_link=$(echo "$download_response" | jq -r '.link // empty')
    
    if [[ -z "$download_link" || "$download_link" == "null" ]]; then
        return 1
    fi
    
    curl -s -L "$download_link" -o "$output_path" 2>/dev/null
    [[ -f "$output_path" ]]
}

# 使用 OpenSubtitles API 下载字幕
download_with_opensubtitles() {
    local video_file="$1"
    local languages="$2"
    
    echo "   🛠️  使用 OpenSubtitles API 下载字幕..."
    
    # 解析文件名
    local parsed=$(parse_video_filename "$video_file")
    local series_name=$(echo "$parsed" | cut -d'|' -f1)
    local season=$(echo "$parsed" | cut -d'|' -f2)
    local episode=$(echo "$parsed" | cut -d'|' -f3)
    
    # 搜索字幕
    local search_result=$(search_opensubtitles "$series_name" "$season" "$episode" "$languages")
    
    if [[ -z "$search_result" ]] || echo "$search_result" | grep -q '"error"'; then
        echo "   ❌ OpenSubtitles API 错误或不可用"
        return 1
    fi
    
    local data_count=$(echo "$search_result" | jq -r '.data | length // 0')
    
    if [[ "$data_count" -eq 0 ]]; then
        echo "   ❌ 未找到字幕"
        return 1
    fi
    
    local video_dir=$(dirname "$video_file")
    local video_basename=$(basename "$video_file")
    local video_name="${video_basename%.*}"
    local success=false
    
    # 按语言下载
    IFS=',' read -ra LANG_ARRAY <<< "$languages"
    for lang in "${LANG_ARRAY[@]}"; do
        lang=$(echo "$lang" | tr -d '[:space:]')
        
        local best_subtitle=$(echo "$search_result" | jq -r --arg lang "$lang" '
            .data | 
            map(select(.attributes.language == $lang)) | 
            sort_by(.attributes.ratings | tonumber // 0) | 
            reverse | 
            .[0] // empty
        ')
        
        if [[ -z "$best_subtitle" || "$best_subtitle" == "null" ]]; then
            continue
        fi
        
        local file_id=$(echo "$best_subtitle" | jq -r '.attributes.files[0].file_id // empty')
        local sub_format=$(echo "$best_subtitle" | jq -r '.attributes.format // "srt"')
        
        if [[ -z "$file_id" ]]; then
            continue
        fi
        
        local output_file="$video_dir/$video_name.$lang.$sub_format"
        
        if [[ -f "$output_file" ]]; then
            echo "   ⏭️  $lang 字幕已存在，跳过"
            success=true
            continue
        fi
        
        if download_from_opensubtitles "$file_id" "$output_file"; then
            echo "   ✅ 已下载 $lang 字幕"
            success=true
        fi
    done
    
    $success
}

# 智能下载字幕（自动选择最佳工具）
download_subtitle_smart() {
    local video_file="$1"
    local languages="$2"
    local force_tool="$3"
    
    local success=false
    
    case "$force_tool" in
        subliminal)
            if check_subliminal; then
                download_with_subliminal "$video_file" "$languages" && success=true
            else
                echo "   ❌ subliminal 未安装"
            fi
            ;;
        subfinder)
            if check_subfinder; then
                download_with_subfinder "$video_file" "$languages" && success=true
            else
                echo "   ❌ subfinder 未安装"
            fi
            ;;
        opensubtitles)
            if [[ -n "$OPENSUBTITLES_API_KEY" ]]; then
                download_with_opensubtitles "$video_file" "$languages" && success=true
            else
                echo "   ❌ OpenSubtitles API Key 未配置"
            fi
            ;;
        *)
            # 自动选择工具
            # 优先使用 subliminal（效果最好）
            if check_subliminal; then
                if download_with_subliminal "$video_file" "$languages"; then
                    success=true
                fi
            fi
            
            # 如果失败，尝试 subfinder
            if ! $success && check_subfinder; then
                if download_with_subfinder "$video_file" "$languages"; then
                    success=true
                fi
            fi
            
            # 最后尝试 OpenSubtitles API
            if ! $success && [[ -n "$OPENSUBTITLES_API_KEY" ]]; then
                if download_with_opensubtitles "$video_file" "$languages"; then
                    success=true
                fi
            fi
            ;;
    esac
    
    $success
}

# 处理单个视频文件
process_video_file() {
    local video_file="$1"
    local languages="$2"
    local force_tool="$3"
    
    echo ""
    echo "📁 处理: $(basename "$video_file")"
    
    if [[ ! -f "$video_file" ]]; then
        echo "   ❌ 文件不存在"
        return 1
    fi
    
    # 解析文件名信息
    local parsed=$(parse_video_filename "$video_file")
    local series_name=$(echo "$parsed" | cut -d'|' -f1)
    local season=$(echo "$parsed" | cut -d'|' -f2)
    local episode=$(echo "$parsed" | cut -d'|' -f3)
    
    echo "   📺 识别: $series_name"
    [[ -n "$season" ]] && echo "   📅 季: $season"
    [[ -n "$episode" ]] && echo "   🎬 集: $episode"
    
    # 下载字幕
    if download_subtitle_smart "$video_file" "$languages" "$force_tool"; then
        return 0
    else
        echo "   ❌ 所有字幕源都失败"
        return 1
    fi
}

# 批量处理目录
process_directory() {
    local directory="$1"
    local languages="$2"
    local force_tool="$3"
    local recursive="$4"
    
    echo ""
    echo "📂 批量处理目录: $directory"
    
    if [[ ! -d "$directory" ]]; then
        echo "❌ 目录不存在"
        exit 1
    fi
    
    local find_depth=""
    [[ "$recursive" == "true" ]] || find_depth="-maxdepth 1"
    
    local video_extensions="mp4|mkv|avi|mov|wmv|flv|webm|m4v|ts"
    local count=0
    local success=0
    
    while IFS= read -r -d '' video_file; do
        if process_video_file "$video_file" "$languages" "$force_tool"; then
            ((success++))
        fi
        ((count++))
    done < <(find "$directory" $find_depth -type f -regextype posix-extended -iregex ".*\.($video_extensions)$" -print0 2>/dev/null)
    
    echo ""
    echo "✅ 完成！成功: $success / $count"
}

# 主程序
main() {
    local file=""
    local directory=""
    local languages="$DEFAULT_LANGUAGES"
    local api_key=""
    local force_tool=""
    local recursive="false"
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--file)
                file="$2"
                shift 2
                ;;
            -d|--directory)
                directory="$2"
                shift 2
                ;;
            -l|--languages)
                languages="$2"
                shift 2
                ;;
            -k|--api-key)
                api_key="$2"
                shift 2
                ;;
            --subliminal)
                force_tool="subliminal"
                shift
                ;;
            --subfinder)
                force_tool="subfinder"
                shift
                ;;
            -r|--recursive)
                recursive="true"
                shift
                ;;
            -h|--help)
                usage
                ;;
            *)
                echo "未知参数: $1"
                usage
                ;;
        esac
    done
    
    # 使用命令行提供的 API Key
    if [[ -n "$api_key" ]]; then
        OPENSUBTITLES_API_KEY="$api_key"
    fi
    
    echo "=== 字幕下载助手 ==="
    echo "语言: $languages"
    
    # 显示可用工具
    echo ""
    echo "可用工具："
    check_subliminal && echo "  ✅ subliminal" || echo "  ❌ subliminal (未安装)"
    check_subfinder && echo "  ✅ subfinder" || echo "  ❌ subfinder (未安装)"
    [[ -n "$OPENSUBTITLES_API_KEY" ]] && echo "  ✅ OpenSubtitles API" || echo "  ❌ OpenSubtitles API (未配置)"
    
    # 执行处理
    if [[ -n "$file" ]]; then
        process_video_file "$file" "$languages" "$force_tool"
    elif [[ -n "$directory" ]]; then
        process_directory "$directory" "$languages" "$force_tool" "$recursive"
    else
        echo ""
        echo "❌ 错误：需要提供文件 (-f) 或目录 (-d)"
        usage
    fi
    
    echo ""
    echo "🎉 全部完成！"
    
    # 提示安装工具
    if ! check_subliminal && ! check_subfinder && [[ -z "$OPENSUBTITLES_API_KEY" ]]; then
        echo ""
        echo "💡 提示：安装字幕下载工具以获得更好体验："
        echo "    pip install subliminal"
        echo "  或"
        echo "    pip install subfinder"
    fi
}

# 运行主程序
main "$@"
