#!/bin/bash
# UpNote CLI wrapper for x-callback-url operations

set -e

urlencode() {
    local string="${1}"
    local strlen=${#string}
    local encoded=""
    local pos c o

    for (( pos=0 ; pos<strlen ; pos++ )); do
        c=${string:$pos:1}
        case "$c" in
            [-_.~a-zA-Z0-9] ) o="${c}" ;;
            * ) printf -v o '%%%02x' "'$c"
        esac
        encoded+="${o}"
    done
    echo "${encoded}"
}

case "$1" in
    new|create)
        shift
        TITLE=""
        TEXT=""
        NOTEBOOK=""
        MARKDOWN="false"
        NEW_WINDOW="false"
        
        while [[ $# -gt 0 ]]; do
            case $1 in
                --title) TITLE="$2"; shift 2 ;;
                --text) TEXT="$2"; shift 2 ;;
                --notebook) NOTEBOOK="$2"; shift 2 ;;
                --markdown) MARKDOWN="true"; shift ;;
                --new-window) NEW_WINDOW="true"; shift ;;
                *) echo "Unknown option: $1"; exit 1 ;;
            esac
        done
        
        URL="upnote://x-callback-url/note/new?"
        [[ -n "$TITLE" ]] && URL+="title=$(urlencode "$TITLE")&"
        [[ -n "$TEXT" ]] && URL+="text=$(urlencode "$TEXT")&"
        [[ -n "$NOTEBOOK" ]] && URL+="notebook=$(urlencode "$NOTEBOOK")&"
        URL+="markdown=$MARKDOWN&new_window=$NEW_WINDOW"
        
        open "$URL"
        ;;
        
    open)
        shift
        NOTE_ID="$1"
        NEW_WINDOW="${2:-false}"
        
        if [[ -z "$NOTE_ID" ]]; then
            echo "Usage: upnote open <noteId> [true|false]"
            exit 1
        fi
        
        open "upnote://x-callback-url/openNote?noteId=$NOTE_ID&new_window=$NEW_WINDOW"
        ;;
        
    notebook)
        shift
        case "$1" in
            new|create)
                shift
                TITLE="$1"
                if [[ -z "$TITLE" ]]; then
                    echo "Usage: upnote notebook new <title>"
                    exit 1
                fi
                open "upnote://x-callback-url/notebook/new?title=$(urlencode "$TITLE")"
                ;;
            open)
                shift
                NOTEBOOK_ID="$1"
                if [[ -z "$NOTEBOOK_ID" ]]; then
                    echo "Usage: upnote notebook open <notebookId>"
                    exit 1
                fi
                open "upnote://x-callback-url/openNotebook?notebookId=$NOTEBOOK_ID"
                ;;
            *)
                echo "Usage: upnote notebook {new|open} ..."
                exit 1
                ;;
        esac
        ;;
        
    tag)
        shift
        TAG="$1"
        if [[ -z "$TAG" ]]; then
            echo "Usage: upnote tag <tagName>"
            exit 1
        fi
        open "upnote://x-callback-url/tag/view?tag=$(urlencode "$TAG")"
        ;;
        
    filter)
        shift
        FILTER_ID="$1"
        if [[ -z "$FILTER_ID" ]]; then
            echo "Usage: upnote filter <filterId>"
            exit 1
        fi
        open "upnote://x-callback-url/openFilter?filterId=$FILTER_ID"
        ;;
        
    view)
        shift
        MODE="$1"
        URL="upnote://x-callback-url/view?mode=$MODE"
        
        shift
        while [[ $# -gt 0 ]]; do
            case $1 in
                --note-id) URL+="&noteId=$2"; shift 2 ;;
                --notebook-id) URL+="&notebookId=$2"; shift 2 ;;
                --tag-id) URL+="&tagId=$2"; shift 2 ;;
                --filter-id) URL+="&filterId=$2"; shift 2 ;;
                --space-id) URL+="&spaceId=$2"; shift 2 ;;
                --query) URL+="&action=search&query=$(urlencode "$2")"; shift 2 ;;
                *) echo "Unknown option: $1"; exit 1 ;;
            esac
        done
        
        open "$URL"
        ;;
        
    *)
        echo "UpNote CLI wrapper"
        echo ""
        echo "Usage:"
        echo "  upnote new --title 'Title' --text 'Content' [--notebook 'Notebook'] [--markdown] [--new-window]"
        echo "  upnote open <noteId> [true|false]"
        echo "  upnote notebook new <title>"
        echo "  upnote notebook open <notebookId>"
        echo "  upnote tag <tagName>"
        echo "  upnote filter <filterId>"
        echo "  upnote view <mode> [--note-id ID] [--notebook-id ID] [--tag-id ID] [--filter-id ID] [--space-id ID] [--query 'search']"
        echo ""
        echo "View modes: all_notes, quick_access, templates, trash, notebooks, tags, filters, all_notebooks, all_tags"
        exit 1
        ;;
esac
