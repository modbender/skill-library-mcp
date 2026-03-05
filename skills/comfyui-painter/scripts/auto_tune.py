#!/usr/bin/env python3
"""Auto-tune generation parameters based on CivitAI model metadata.

Fetches recommended settings (sampler, steps, CFG, size, negative prompt)
from CivitAI sample images and applies them to generation.
"""

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from civitai import get_recommended_params, _load_config, _save_config, _api_get


# Fallback defaults per base model type
BASE_MODEL_DEFAULTS = {
    "Illustrious": {
        "steps": 20,
        "cfg": 7,
        "sampler": "euler_a",
        "scheduler": "normal",
        "width": 832,
        "height": 1216,
        "negative_prompt": "worst quality, bad quality, lowres, bad anatomy, bad hands, text, error"
    },
    "SDXL 1.0": {
        "steps": 25,
        "cfg": 5,
        "sampler": "dpmpp_2m",
        "scheduler": "karras",
        "width": 1024,
        "height": 1536,
        "negative_prompt": "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality"
    },
    "Flux.1 D": {
        "steps": 20,
        "cfg": 1,
        "sampler": "euler",
        "scheduler": "simple",
        "width": 1024,
        "height": 1024,
        "negative_prompt": ""
    },
    "Pony": {
        "steps": 25,
        "cfg": 7,
        "sampler": "euler_a",
        "scheduler": "normal",
        "width": 832,
        "height": 1216,
        "negative_prompt": "score_4, score_3, score_2, score_1, worst quality"
    },
    "NoobAI": {
        "steps": 28,
        "cfg": 5.5,
        "sampler": "euler_a",
        "scheduler": "normal",
        "width": 832,
        "height": 1216,
        "negative_prompt": "worst quality, bad quality, lowres"
    }
}

# Known model ID mapping (local alias -> CivitAI model ID)
KNOWN_MODELS = {
    "hassaku": 140272,
    "janku": 1277670,
    "noobv4": 1045588,
    "noobv6": 1045588,
    "sdxlv8": 82543,
    "nova3d": 715287,
    "unholy": 1307857,
    "flux": 638187,
}

# Sampler name mapping: CivitAI -> ComfyUI
SAMPLER_MAP = {
    "euler a": "euler_ancestral",
    "euler": "euler",
    "dpm++ 2m": "dpmpp_2m",
    "dpm++ 2m karras": "dpmpp_2m",
    "dpm++ sde": "dpmpp_sde",
    "dpm++ sde karras": "dpmpp_sde",
    "dpm++ 2m sde": "dpmpp_2m_sde",
    "dpm++ 2s a": "dpmpp_2s_ancestral",
    "ddim": "ddim",
    "lcm": "lcm",
    "heun": "heun",
    "uni_pc": "uni_pc",
}

SCHEDULER_MAP = {
    "automatic": "normal",
    "karras": "karras",
    "exponential": "exponential",
    "sgm uniform": "sgm_uniform",
    "simple": "simple",
    "normal": "normal",
    "ddim": "ddim_uniform",
}


def _normalize_sampler(name):
    """Convert CivitAI sampler name to ComfyUI sampler name."""
    if not name:
        return None
    return SAMPLER_MAP.get(name.lower().strip(), name.lower().replace(" ", "_"))


def _normalize_scheduler(name):
    """Convert CivitAI scheduler name to ComfyUI scheduler name."""
    if not name:
        return None
    return SCHEDULER_MAP.get(name.lower().strip(), "normal")


def _parse_size(size_str):
    """Parse size string like '832x1216' into (width, height)."""
    if not size_str or "x" not in str(size_str):
        return None, None
    try:
        parts = str(size_str).split("x")
        return int(parts[0]), int(parts[1])
    except (ValueError, IndexError):
        return None, None


def get_tuned_params(model_alias):
    """Get auto-tuned parameters for a model alias.
    
    Tries CivitAI first, falls back to base model defaults.
    
    Returns:
        dict with keys: steps, cfg, sampler, scheduler, width, height, negative_prompt
    """
    model_id = KNOWN_MODELS.get(model_alias)
    
    if model_id:
        try:
            civitai_params = get_recommended_params(model_id)
            
            # Also get base model type
            model_data = _api_get(f"models/{model_id}")
            base_model = model_data["modelVersions"][0].get("baseModel", "")
            defaults = BASE_MODEL_DEFAULTS.get(base_model, BASE_MODEL_DEFAULTS["Illustrious"])
            
            # Build params, preferring CivitAI data over defaults
            params = {}
            
            sampler = _normalize_sampler(civitai_params.get("sampler"))
            params["sampler"] = sampler or defaults["sampler"]
            
            scheduler = _normalize_scheduler(civitai_params.get("scheduler"))
            params["scheduler"] = scheduler or defaults["scheduler"]
            
            steps = civitai_params.get("steps")
            params["steps"] = int(steps) if steps else defaults["steps"]
            
            cfg = civitai_params.get("cfg")
            params["cfg"] = float(cfg) if cfg else defaults["cfg"]
            
            w, h = _parse_size(civitai_params.get("size"))
            params["width"] = w or defaults["width"]
            params["height"] = h or defaults["height"]
            
            neg = civitai_params.get("negative_prompt")
            params["negative_prompt"] = neg if neg else defaults["negative_prompt"]
            
            params["source"] = "civitai"
            params["model_name"] = civitai_params.get("model_name", "")
            params["samples_analyzed"] = civitai_params.get("samples_analyzed", 0)
            
            return params
            
        except Exception as e:
            print(f"CivitAI lookup failed for {model_alias}: {e}", file=sys.stderr)
    
    # Fallback to config defaults
    cfg = _load_config()
    defaults = cfg.get("defaults", {})
    return {
        "steps": defaults.get("steps", 20),
        "cfg": defaults.get("cfg", 5),
        "sampler": defaults.get("sampler", "dpmpp_2m"),
        "scheduler": defaults.get("scheduler", "normal"),
        "width": defaults.get("width", 1024),
        "height": defaults.get("height", 1536),
        "negative_prompt": defaults.get("negative_prompt", ""),
        "source": "config_default",
    }


def update_config_with_tuned_params(model_alias):
    """Fetch tuned params and update config.json model_params section."""
    params = get_tuned_params(model_alias)
    
    cfg = _load_config()
    if "model_params" not in cfg:
        cfg["model_params"] = {}
    
    cfg["model_params"][model_alias] = {
        "steps": params["steps"],
        "cfg": params["cfg"],
        "sampler": params["sampler"],
        "scheduler": params["scheduler"],
        "width": params["width"],
        "height": params["height"],
        "negative_prompt": params["negative_prompt"],
    }
    
    _save_config(cfg)
    return params


# CLI
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    
    g = sub.add_parser("get", help="Get tuned params for a model alias")
    g.add_argument("alias")
    
    u = sub.add_parser("update-all", help="Update config with tuned params for all known models")
    
    args = parser.parse_args()
    
    if args.cmd == "get":
        result = get_tuned_params(args.alias)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.cmd == "update-all":
        for alias in KNOWN_MODELS:
            print(f"Tuning {alias}...")
            result = update_config_with_tuned_params(alias)
            print(f"  → {result.get('source')}: steps={result['steps']} cfg={result['cfg']} sampler={result['sampler']}")
        print("Done! Config updated.")
    
    else:
        parser.print_help()
