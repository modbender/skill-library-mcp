---
name: trtc-config-inspector
description: "TRTC SDK configuration inspection and analysis tool. Downloads scene config template Excel, inspection result Excel, and project code from user-provided URLs, compares inspection results against target scene configurations, locates TRTC parameters in source code, and generates a structured modification report. The AI Agent then applies code changes based on the report. Supports live streaming, voice chat room, video call, and other scenarios. Triggers: TRTC config inspection, compare config and modify code, optimize TRTC scene configuration"
version: 2.1.0
author: CwlVincent
permissions: "Network access (download Excel and code files from user-provided URLs), file read access (parse config Excel and scan source code)"
---

# TRTC Config Inspector

Compares TRTC scene configuration templates against inspection results, generates a structured diff report, and guides the AI Agent or user to adjust source code accordingly.

## Description

This skill implements TRTC SDK configuration inspection analysis and modification suggestion generation:
1. **Download Resources**: Download scene config template Excel, inspection result Excel, and project code archive from user-provided URLs
2. **Parse & Compare**: Parse both Excel files, compare current configuration against target configuration item by item
3. **Locate Code**: Find corresponding TRTC API call sites in the project source code
4. **Generate Modification Plan**: Output structured modification suggestions (JSON format) including target values, code locations, and change recommendations for each diff item
5. **Output Report**: Generate a diff summary table; the AI Agent then uses code editing tools to apply the changes

> **Note**: The scripts themselves **do not modify any user code**. They only generate analysis reports and modification suggestions. Actual code changes are performed by the AI Agent using standard code editing tools (e.g., replace_in_file), and the user can review each modification step.

## When To Use

Trigger this skill when the user makes requests like:
- "Help me modify the code based on this inspection result and live streaming config"
- "Download these files and optimize code according to the TRTC config template"
- "Compare TRTC inspection config and modify code per the template"
- "Check if TRTC SDK config meets the scene requirements"
- User provides scene config Excel (scene_config_*.xlsx) and/or inspection result Excel (inspection_result_*.xlsx)

## How To Use

### Step 1: Collect User Input

Confirm the following information with the user (if not fully provided):

| Parameter | Description | Required |
|---|---|---|
| Scene Config Template | URL or local path to scene config Excel | Required |
| Inspection Result | URL or local path to inspection result Excel | Required (if absent, only output target config) |
| Code Download Link | URL to project code zip/tar.gz or local directory path | Required |

Users may provide input in various ways:
- Direct URL links
- Local file/directory paths
- Files already present in the workspace

### Step 2: Download Resource Files

Use the download script to fetch remote files:

```bash
python3 SKILL_BASE_DIR/scripts/download_files.py \
  --config-url "Scene config Excel URL" \
  --inspect-url "Inspection result Excel URL" \
  --code-url "Code archive URL" \
  --output-dir "SKILL_BASE_DIR/workspace"
```

This script will:
- Download scene config Excel to `workspace/config.xlsx`
- Download inspection result Excel to `workspace/inspect.xlsx`
- Download and extract code to `workspace/code/`
- Output JSON-formatted download results containing local paths for each file

If the user provides a local file path, skip the download for that file and use the local path directly.

### Step 3: Parse and Compare Configuration

Run the diff script to generate a difference report:

```bash
python3 SKILL_BASE_DIR/scripts/diff_config.py "inspection_result_excel_path" "scene_config_excel_path"
```

The JSON report output contains:
- `diffs` — Config items where current value differs from target value (code modification needed)
- `matches` — Config items that already match (no modification needed)
- `unable_to_compare` — Items that cannot be automatically compared (manual review needed)

If only the scene config template is available (no inspection result), parse the template directly:

```bash
python3 SKILL_BASE_DIR/scripts/parse_excel.py "scene_config_excel_path" --type config
```

### Step 4: Locate and Modify Code Based on Report

Based on the `diffs` array in the diff report, the AI Agent uses code editing tools to find corresponding API calls in the code and modify parameter values. Below are the mappings between config items and code APIs:

#### 4.1 Room Entry Mode (Scene / AppScene)

Find `enterRoom` calls, modify the second parameter.

| Config Value | Android Code Constant | iOS Code Constant |
|---|---|---|
| `Live` | `TRTCCloudDef.TRTC_APP_SCENE_LIVE` | `TRTCAppSceneLIVE` |
| `VideoCall` | `TRTCCloudDef.TRTC_APP_SCENE_VIDEOCALL` | `TRTCAppSceneVideoCall` |
| `AudioCall` | `TRTCCloudDef.TRTC_APP_SCENE_AUDIOCALL` | `TRTCAppSceneAudioCall` |
| `VoiceChatRoom` | `TRTCCloudDef.TRTC_APP_SCENE_VOICE_CHATROOM` | `TRTCAppSceneVoiceChatRoom` |

#### 4.2 Audio Quality

Find `startLocalAudio` calls.

| Config Value | Android Code Constant | iOS Code Constant |
|---|---|---|
| `MUSIC` | `TRTCCloudDef.TRTC_AUDIO_QUALITY_MUSIC` | `TRTCAudioQualityMusic` |
| `DEFAULT` | `TRTCCloudDef.TRTC_AUDIO_QUALITY_DEFAULT` | `TRTCAudioQualityDefault` |
| `SPEECH` | `TRTCCloudDef.TRTC_AUDIO_QUALITY_SPEECH` | `TRTCAudioQualitySpeech` |

#### 4.3 System Volume Type

Find `setSystemVolumeType` calls.

| Config Value | Android Code Constant | iOS Code Constant |
|---|---|---|
| `media` | `TRTCCloudDef.TRTCSystemVolumeTypeMedia` | `TRTCSystemVolumeTypeMedia` |
| `voip` | `TRTCCloudDef.TRTCSystemVolumeTypeVOIP` | `TRTCSystemVolumeTypeVOIP` |
| `auto` | `TRTCCloudDef.TRTCSystemVolumeTypeAuto` | `TRTCSystemVolumeTypeAuto` |

#### 4.4 Video Encoder Params

Find `setVideoEncoderParam` calls and `TRTCVideoEncParam` objects.

**CRITICAL — Video encoder params must be compared item by item; do not miss any sub-parameter:**

In the scene config Excel, video encoder params (resolution, FPS, bitrate) are split into **multiple rows**. The diff script outputs independent sub-parameter comparisons. **All video encoder sub-parameter diffs must be checked and applied**, including:
- **Resolution**: e.g., "recommended 720p" -> update `videoResolution`
- **FPS**: e.g., "25fps" -> update `videoFps` (**frequently missed!**)
- **Bitrate**: e.g., "720p-1800kbps" -> update `videoBitrate`

| Parameter | Field Name | Description |
|---|---|---|
| Resolution | `videoResolution` | e.g., `TRTC_VIDEO_RESOLUTION_1280_720` (720p) |
| FPS | `videoFps` | Integer, e.g., 15 or 25 |
| Bitrate | `videoBitrate` | Integer (kbps), e.g., 1800 |
| Min Bitrate | `minVideoBitrate` | Integer (kbps) |
| Resolution Mode | `videoResolutionMode` | `PORTRAIT` or `LANDSCAPE` |
| Adaptive Resolution | `enableAdjustRes` | Boolean |

Resolution constant mapping:
- 540p -> `TRTC_VIDEO_RESOLUTION_960_540`
- 720p -> `TRTC_VIDEO_RESOLUTION_1280_720`
- 1080p -> `TRTC_VIDEO_RESOLUTION_1920_1080`

Recommended bitrates:
- 540p -> 1300 kbps
- 720p -> 1800 kbps
- 1080p -> 3000 kbps

#### 4.5 Capture Volume / Remote Playback Volume

Find `setAudioCaptureVolume` and `setAudioPlayoutVolume` calls.

#### 4.6 Experimental APIs

Find `callExperimentalAPI` calls with JSON string parameters. The Excel `code_example` column provides the specific JSON structure.

### Step 5: Ensure Correct API Call Order

When the AI Agent modifies code, TRTC API calls must follow this order:

1. `TRTCCloud.sharedInstance()` — Create instance
2. `setListener()` — Set callback listener
3. `setSystemVolumeType()` — Set volume type (before enterRoom)
4. `callExperimentalAPI()` — Experimental settings (before enterRoom)
5. `setVideoEncoderParam()` — Set video encoder params
6. `startLocalPreview()` — Start local camera preview
7. `startLocalAudio()` — Start local audio capture
8. `enterRoom()` — Enter room

### Step 6: Output Modification Report

After completing all modifications, output a summary table:

| Config Item | Before | After | Status |
|---|---|---|---|
| Room Entry Mode | VideoCall | Live | Modified |
| Audio Quality | DEFAULT | MUSIC | Modified |
| System Volume Type | VOIP | Media | Modified |
| Video Resolution | 640x480 | 1280x720 | Modified |
| Video FPS | 15fps | 25fps | Modified |
| Video Bitrate | 900kbps | 1800kbps | Modified |

For items marked as "optional", inform the user and let them decide whether to apply.

## Implementation

### Dependencies

- Python 3.8+
- `openpyxl` (auto-installed if missing)
- `requests` (auto-installed if missing)

### Script Inventory

| Script | Purpose |
|---|---|
| `scripts/download_files.py` | Download scene config, inspection result, and code archive from URLs and extract |
| `scripts/parse_excel.py` | Parse a single Excel file (scene config or inspection result) and output structured JSON |
| `scripts/diff_config.py` | Compare inspection result against scene config template and output diff report |
| `scripts/run_inspector.py` | End-to-end inspector entry point: download -> parse -> diff -> analyze code -> generate modification plan |

### Core Functions

- `download_files.py::download_and_extract(config_url, inspect_url, code_url, output_dir)` — Download and extract all resource files
- `parse_excel.py::parse_config_excel(filepath)` — Parse scene config Excel
- `parse_excel.py::parse_inspect_excel(filepath)` — Parse inspection result Excel
- `diff_config.py::diff_configs(inspect_data, config_data)` — Compare and output diffs

## Edge Cases

- **URL inaccessible**: Prompt user to verify the link is valid or whether login authorization is required
- **Abnormal Excel format**: Catch parsing exceptions, prompt user to confirm the file format matches TRTC platform export standards
- **API call not found in code**: Mark as "new" in the report; the AI Agent adds it at the appropriate position following the API call order
- **Optional config items**: Items marked "optional" are not modified automatically; prompt user to decide
- **Multi-platform code**: Automatically detect code language (Kotlin/Java/Swift/ObjC) and adapt syntax accordingly
- **Code archive format**: Supports .zip and .tar.gz formats

## Important Notes

- Excel files are exported by TRTC platform inspection tools and scene configuration tools
- When modifying code, preserve the existing code structure and only change specific parameter values
- For Kotlin projects, convert Java example code from Excel to Kotlin syntax
- The `code_example` column provides reference implementations; adapt to the project's actual code style
- **Video encoder params must be checked item by item**: The diff script outputs independent diffs for each sub-parameter (resolution, FPS, bitrate); all must be applied. FPS is the most commonly missed item

## Security

- **Scripts do not modify code**: All Python scripts (download_files.py, parse_excel.py, diff_config.py, run_inspector.py) only perform download, parse, compare, and analyze operations. **They do not directly modify any user source code files.** Code modifications are performed by the AI Agent using standard editing tools, and the user can review each step
- **URLs are user-controlled**: Scripts only download files from URLs explicitly provided by the user; no hardcoded external addresses are accessed
- **Extraction limited to workspace**: Code archives are only extracted to the specified workspace output directory
- **No credential storage**: Scripts do not read, store, or transmit any keys, tokens, or user credentials
- **Runtime dependencies**: Only auto-installs `openpyxl` (Excel parsing) and `requests` (HTTP download), both standard PyPI packages
