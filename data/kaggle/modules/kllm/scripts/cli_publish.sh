#!/usr/bin/env bash
# Publish private datasets, notebooks, and models to Kaggle using kaggle-cli.
#
# kaggle-cli supports:
#   kaggle datasets create   — create a new private dataset
#   kaggle datasets version  — create a new version of an existing dataset
#   kaggle datasets init     — generate dataset-metadata.json template
#   kaggle kernels push      — publish a notebook (private by default)
#   kaggle kernels init      — generate kernel-metadata.json template
#   kaggle models create     — create a new model
#   kaggle models instances versions create — upload model files
#
# NOT directly supported:
#   Benchmark publishing — use the Kaggle UI
#
# Prerequisites:
#   pip install kaggle
#   Credentials configured in ~/.kaggle/kaggle.json
#
# Usage:
#   bash scripts/cli_publish.sh dataset <data-dir>
#   bash scripts/cli_publish.sh notebook <notebook-dir>
#   bash scripts/cli_publish.sh model <model-dir> <model-handle>

set -euo pipefail

ACTION="${1:?Usage: cli_publish.sh <dataset|notebook|model> <dir> [model-handle]}"
DIR="${2:?Usage: cli_publish.sh <dataset|notebook|model> <dir> [model-handle]}"

case "${ACTION}" in
    dataset)
        echo "============================================================"
        echo "Publish a Private Dataset"
        echo "============================================================"

        echo "--- Ensure dataset-metadata.json exists ---"
        if [ ! -f "${DIR}/dataset-metadata.json" ]; then
            echo "Initializing metadata..."
            kaggle datasets init -p "${DIR}"
            echo "Edit ${DIR}/dataset-metadata.json before continuing."
            exit 1
        fi

        echo "--- Creating dataset ---"
        kaggle datasets create \
            -p "${DIR}" \
            --dir-mode zip

        echo "Dataset created! It is private by default."
        ;;

    notebook)
        echo "============================================================"
        echo "Publish a Private Notebook"
        echo "============================================================"

        echo "--- Ensure kernel-metadata.json exists ---"
        if [ ! -f "${DIR}/kernel-metadata.json" ]; then
            echo "Initializing metadata..."
            kaggle kernels init -p "${DIR}"
            echo "Edit ${DIR}/kernel-metadata.json before continuing."
            exit 1
        fi

        echo "--- Pushing notebook ---"
        kaggle kernels push -p "${DIR}"

        echo "Notebook published (private) and execution triggered on KKB."
        ;;

    model)
        MODEL_HANDLE="${3:?Usage: cli_publish.sh model <model-dir> <model-handle>}"

        echo "============================================================"
        echo "Publish a Private Model"
        echo "============================================================"

        echo "--- Ensure model-metadata.json exists ---"
        if [ ! -f "${DIR}/model-metadata.json" ]; then
            echo "Initializing metadata..."
            kaggle models init -p "${DIR}"
            echo "Edit ${DIR}/model-metadata.json before continuing."
            exit 1
        fi

        echo "--- Creating model container ---"
        kaggle models create -p "${DIR}"
        echo "Model container created."

        echo "--- Uploading model files ---"
        kaggle models instances versions create \
            "${MODEL_HANDLE}" \
            -p "${DIR}" \
            -n "Upload via kaggle-cli"
        echo "Model files uploaded."
        ;;

    *)
        echo "Unknown action: ${ACTION}"
        echo "Usage: cli_publish.sh <dataset|notebook|model> <dir> [model-handle]"
        exit 1
        ;;
esac
