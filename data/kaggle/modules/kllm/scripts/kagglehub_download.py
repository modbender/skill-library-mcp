"""Download datasets and models from Kaggle using kagglehub.

Usage:
    python kagglehub_download.py                           # default example dataset
    python kagglehub_download.py --dataset heptapod/titanic
    python kagglehub_download.py --model google/gemma/transformers/2b
"""

import argparse
import kagglehub


def download_dataset(handle: str) -> str:
    """Download a dataset. Returns the local path."""
    path = kagglehub.dataset_download(handle)
    print(f"Dataset downloaded to: {path}")
    return path


def download_model(handle: str) -> str:
    """Download a model. Returns the local path."""
    path = kagglehub.model_download(handle)
    print(f"Model downloaded to: {path}")
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download from Kaggle via kagglehub")
    parser.add_argument("--dataset", default=None, help="Dataset handle (owner/name)")
    parser.add_argument("--model", default=None, help="Model handle (owner/name/framework/variation)")
    args = parser.parse_args()

    if args.dataset:
        download_dataset(args.dataset)
    elif args.model:
        download_model(args.model)
    else:
        # Default example
        print("No --dataset or --model specified. Downloading example dataset...")
        download_dataset("heptapod/titanic")
