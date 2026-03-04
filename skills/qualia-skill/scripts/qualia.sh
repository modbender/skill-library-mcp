#!/usr/bin/env bash
set -euo pipefail

# Qualia CLI - VLA fine-tuning platform
# Requires: QUALIA_API_KEY, curl, jq

API="https://api.qualiastudios.dev"

if [[ -z "${QUALIA_API_KEY:-}" ]]; then
  echo "Error: QUALIA_API_KEY not set" >&2
  exit 1
fi

qapi() {
  local method="$1"
  local path="$2"
  local body="${3:-}"
  if [[ -n "$body" ]]; then
    curl -s -X "$method" "${API}${path}" \
      -H "Content-Type: application/json" \
      -H "X-API-Key: $QUALIA_API_KEY" \
      -d "$body"
  else
    curl -s -X "$method" "${API}${path}" \
      -H "X-API-Key: $QUALIA_API_KEY"
  fi
}

cmd="${1:-help}"
shift || true

case "$cmd" in
  credits)
    qapi GET /v1/credits | jq -r '"Credits: \(.balance)"'
    ;;

  models)
    qapi GET /v1/models | jq -r '.data[] |
      "[\(.id)] \(.name)\n  \(.description)\n  camera slots: \(.camera_slots | join(", "))\(if .base_model_id then "\n  base model: " + .base_model_id else "" end)\(if .supports_custom_model == false then "\n  ⚠ custom model_id not supported" else "" end)\n"'
    ;;

  instances)
    qapi GET /v1/instances | jq -r '.data[] |
      "[\(.id)] \(.gpu_description) — \(.credits_per_hour) credits/hr\n  \(.specs.gpu_count)x \(.specs.gpu_type) | \(.specs.memory_gib)GB RAM | \(.specs.storage_gib)GB storage | \(.specs.vcpus) vCPUs\n  regions: \([.regions[].name] | join(", "))\n"'
    ;;

  projects)
    qapi GET /v1/projects | jq -r '.data[] |
      "[\(.project_id)] \(.name)\(if .description then " — " + .description else "" end)\n  created: \(.created_at | split("T")[0]) | jobs: \(.jobs | length)\(
        if (.jobs | length) > 0 then
          "\n" + (.jobs[] | "  · \(.job_id) [\(.status // "unknown")] \(.name // .model // "") \(if .dataset then "on " + .dataset else "" end)" | gsub("  +"; " "))
        else "" end
      )\n"'
    ;;

  project-create)
    name="${1:-}"
    description="${2:-}"
    if [[ -z "$name" ]]; then
      echo "Usage: qualia.sh project-create <name> [description]" >&2
      exit 1
    fi
    body=$(jq -n --arg name "$name" --arg desc "$description" \
      'if $desc != "" then {name: $name, description: $desc} else {name: $name} end')
    result=$(qapi POST /v1/projects "$body")
    echo "$result" | jq -r 'if .created then "Created project: \(.project_id)" else "Failed to create project" end'
    ;;

  project-delete)
    project_id="${1:-}"
    if [[ -z "$project_id" ]]; then
      echo "Usage: qualia.sh project-delete <project_id>" >&2
      exit 1
    fi
    result=$(qapi DELETE "/v1/projects/${project_id}")
    echo "$result" | jq -r 'if .deleted then "Deleted project: \(.project_id)" else "Failed to delete project" end'
    ;;

  dataset-keys)
    dataset_id="${1:-}"
    if [[ -z "$dataset_id" ]]; then
      echo "Usage: qualia.sh dataset-keys <huggingface_dataset_id>" >&2
      echo "  e.g. qualia.sh dataset-keys lerobot/aloha_sim_insertion_human" >&2
      exit 1
    fi
    result=$(qapi GET "/v1/datasets/${dataset_id}/image-keys")
    echo "Image keys for $dataset_id:"
    echo "$result" | jq -r '.image_keys[] | "  \(.)"'
    ;;

  hyperparams)
    # Usage: qualia.sh hyperparams <vla_type> [model_id]
    # model_id is required for smolvla, pi0, pi05
    vla_type="${1:-}"
    model_id="${2:-}"
    if [[ -z "$vla_type" ]]; then
      echo "Usage: qualia.sh hyperparams <act|smolvla|pi0|pi05|gr00t_n1_5> [model_id]" >&2
      echo "  model_id required for: smolvla, pi0, pi05" >&2
      exit 1
    fi
    path="/v1/finetune/hyperparams/defaults?vla_type=${vla_type}"
    if [[ -n "$model_id" ]]; then
      path="${path}&model_id=${model_id}"
    fi
    result=$(qapi GET "$path")
    echo "Defaults for $vla_type${model_id:+ ($model_id)}:"
    echo "$result" | jq '.data'
    ;;

  hyperparams-validate)
    # Usage: qualia.sh hyperparams-validate <vla_type> '<hyperparams_json>'
    # vla_type goes as query param; hyperparams JSON is sent as the request body directly
    vla_type="${1:-}"
    hyper_json="${2:-}"
    if [[ -z "$vla_type" || -z "$hyper_json" ]]; then
      echo "Usage: qualia.sh hyperparams-validate <vla_type> '<hyperparams_json>'" >&2
      exit 1
    fi
    result=$(qapi POST "/v1/finetune/hyperparams/validate?vla_type=${vla_type}" "$hyper_json")
    if echo "$result" | jq -e '.valid' > /dev/null 2>&1; then
      echo "$result" | jq -r 'if .valid then "✓ Valid" else "✗ Invalid\n" + (.issues // [] | map("  · \(.field): \(.message)") | join("\n")) end'
    else
      echo "$result" | jq '.'
    fi
    ;;

  finetune)
    # Required positional args
    project_id="${1:-}"
    vla_type="${2:-}"
    dataset_id="${3:-}"
    hours="${4:-}"
    camera_mappings="${5:-}"

    # Optional named flags (--key value or --key=value)
    model_id=""
    job_name=""
    instance_type=""
    region=""
    batch_size=""
    hyper_spec=""
    rabc_model=""
    rabc_image_key=""
    rabc_head_mode=""

    shift 5 2>/dev/null || true
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --model=*)    model_id="${1#*=}" ;;
        --model)      model_id="$2"; shift ;;
        --name=*)     job_name="${1#*=}" ;;
        --name)       job_name="$2"; shift ;;
        --instance=*) instance_type="${1#*=}" ;;
        --instance)   instance_type="$2"; shift ;;
        --region=*)   region="${1#*=}" ;;
        --region)     region="$2"; shift ;;
        --batch-size=*) batch_size="${1#*=}" ;;
        --batch-size) batch_size="$2"; shift ;;
        --hyper-spec=*) hyper_spec="${1#*=}" ;;
        --hyper-spec) hyper_spec="$2"; shift ;;
        --rabc=*)     rabc_model="${1#*=}" ;;
        --rabc)       rabc_model="$2"; shift ;;
        --rabc-image-key=*) rabc_image_key="${1#*=}" ;;
        --rabc-image-key)   rabc_image_key="$2"; shift ;;
        --rabc-head-mode=*) rabc_head_mode="${1#*=}" ;;
        --rabc-head-mode)   rabc_head_mode="$2"; shift ;;
        *) echo "Unknown flag: $1" >&2; exit 1 ;;
      esac
      shift
    done

    if [[ -z "$project_id" || -z "$vla_type" || -z "$dataset_id" || -z "$hours" || -z "$camera_mappings" ]]; then
      echo "Usage: qualia.sh finetune <project_id> <vla_type> <dataset_id> <hours> '<camera_mappings_json>' [flags]" >&2
      echo "" >&2
      echo "  Required:" >&2
      echo "    project_id       UUID from 'qualia.sh projects'" >&2
      echo "    vla_type         act | smolvla | pi0 | pi05 | gr00t_n1_5" >&2
      echo "    dataset_id       HuggingFace dataset ID (e.g. lerobot/pusht)" >&2
      echo "    hours            Training duration (max 168)" >&2
      echo "    camera_mappings  JSON: slot name → dataset image key" >&2
      echo "                     e.g. '{\"cam_1\": \"observation.images.top\"}'" >&2
      echo "" >&2
      echo "  Optional flags:" >&2
      echo "    --model <id>         Base model (required for smolvla/pi0/pi05)" >&2
      echo "    --name <str>         Job display name" >&2
      echo "    --instance <id>      GPU instance (from 'qualia.sh instances')" >&2
      echo "    --region <name>      Cloud region" >&2
      echo "    --batch-size <n>     Training batch size (1-512, default 32)" >&2
      echo "    --hyper-spec '<json>' Advanced hyperparameters (from 'qualia.sh hyperparams')" >&2
      echo "" >&2
      echo "  Tip: run 'qualia.sh dataset-keys <dataset_id>' to discover image key names" >&2
      exit 1
    fi

    body=$(jq -n \
      --arg project_id "$project_id" \
      --arg vla_type "$vla_type" \
      --arg dataset_id "$dataset_id" \
      --argjson hours "$hours" \
      --argjson camera_mappings "$camera_mappings" \
      '{
        project_id: $project_id,
        vla_type: $vla_type,
        dataset_id: $dataset_id,
        hours: $hours,
        camera_mappings: $camera_mappings
      }')

    [[ -n "$model_id" ]]      && body=$(echo "$body" | jq --arg v "$model_id" '. + {model_id: $v}')
    [[ -n "$job_name" ]]      && body=$(echo "$body" | jq --arg v "$job_name" '. + {name: $v}')
    [[ -n "$instance_type" ]] && body=$(echo "$body" | jq --arg v "$instance_type" '. + {instance_type: $v}')
    [[ -n "$region" ]]        && body=$(echo "$body" | jq --arg v "$region" '. + {region: $v}')
    [[ -n "$batch_size" ]]    && body=$(echo "$body" | jq --argjson v "$batch_size" '. + {batch_size: $v}')
    [[ -n "$hyper_spec" ]]    && body=$(echo "$body" | jq --argjson v "$hyper_spec" '. + {vla_hyper_spec: $v}')
    if [[ -n "$rabc_model" ]]; then
      body=$(echo "$body" | jq --arg m "$rabc_model" '. + {use_rabc: true, sarm_reward_model_path: $m}')
      [[ -n "$rabc_image_key" ]] && body=$(echo "$body" | jq --arg v "$rabc_image_key" '. + {sarm_image_observation_key: $v}')
      [[ -n "$rabc_head_mode" ]] && body=$(echo "$body" | jq --arg v "$rabc_head_mode" '. + {rabc_head_mode: $v}')
    fi

    result=$(qapi POST /v1/finetune "$body")
    echo "$result" | jq -r '"Job created: \(.job_id)\nStatus: \(.status)\(if .message then "\nMessage: " + .message else "" end)"'
    ;;

  status)
    job_id="${1:-}"
    if [[ -z "$job_id" ]]; then
      echo "Usage: qualia.sh status <job_id>" >&2
      exit 1
    fi
    result=$(qapi GET "/v1/finetune/${job_id}")
    echo "$result" | jq -r '"Job \(.job_id)\nStatus: \(.status) | Phase: \(.current_phase)\n"'
    echo "$result" | jq -r '
      .phases[] |
      "[\(.status | ascii_upcase)] \(.name)" +
      (if .started_at then " (started \(.started_at | split("T")[0]))" else "" end) +
      (if .error then "\n  Error: \(.error)" else "" end) +
      (if (.events | length) > 0 then
        "\n" + (.events[] |
          "  → [\(.status // "?")] \(.message // "")" +
          (if .error then " | \(.error)" else "" end) +
          (if (.retry_attempt // 0) > 0 then " (retry \(.retry_attempt))" else "" end)
        )
       else "" end)'
    ;;

  cancel)
    job_id="${1:-}"
    if [[ -z "$job_id" ]]; then
      echo "Usage: qualia.sh cancel <job_id>" >&2
      exit 1
    fi
    result=$(qapi POST "/v1/finetune/${job_id}/cancel")
    echo "$result" | jq -r '"Job \(.job_id): \(if .cancelled then "cancelled" else "cancellation failed" end)\(if .message then " — " + .message else "" end)"'
    ;;

  help|*)
    echo "Qualia CLI - VLA fine-tuning platform"
    echo ""
    echo "Commands:"
    echo "  credits                                    Check credit balance"
    echo "  models                                     List VLA types, camera slots, base models"
    echo "  instances                                  List GPU instances with specs and pricing"
    echo ""
    echo "  projects                                   List projects with jobs"
    echo "  project-create <name> [description]        Create a project"
    echo "  project-delete <project_id>                Delete a project (no active jobs)"
    echo ""
    echo "  dataset-keys <dataset_id>                  List image keys in a HuggingFace dataset"
    echo "  hyperparams <vla_type> [model_id]          Get default hyperparameters"
    echo "  hyperparams-validate <vla_type> '<json>'   Validate custom hyperparameters"
    echo ""
    echo "  finetune <project_id> <vla_type> <dataset_id> <hours> '<cameras>' [--flags]"
    echo "    --model <id>         Base model ID (required for smolvla/pi0/pi05)"
    echo "    --name <str>         Job display name"
    echo "    --instance <id>      GPU instance type"
    echo "    --region <name>      Cloud region"
    echo "    --batch-size <n>     Batch size (1-512)"
    echo "    --hyper-spec '<json>' Custom hyperparameters"
    echo "    --rabc <model_path>  Enable RA-BC with SARM reward model (HF path)"
    echo "    --rabc-image-key <k> Image key for reward annotations"
    echo "    --rabc-head-mode <m> RA-BC head mode (e.g. sparse)"
    echo ""
    echo "  status <job_id>                            Check job status and phase history"
    echo "  cancel <job_id>                            Cancel a running job"
    echo ""
    echo "VLA types: act, smolvla, pi0, pi05, gr00t_n1_5, sarm"
    echo "  model_id REQUIRED for: smolvla, pi0, pi05"
    echo "  model_id NOT supported for: act, gr00t_n1_5, sarm"
    echo "  RA-BC supported for: smolvla, pi0, pi05"
    ;;
esac
