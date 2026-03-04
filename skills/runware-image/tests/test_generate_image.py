import json
from pathlib import Path
import os
import pytest

from scripts import generate_image as gi


@pytest.mark.skipif(os.getenv("RUNWARE_API_KEY") is None, reason="Integration test requires RUNWARE_API_KEY")
def test_integration_generate_and_save(tmp_path):
    # This is an integration-style smoke test. It will only run if RUNWARE_API_KEY is set.
    api_key = os.getenv("RUNWARE_API_KEY")
    prompt = "A small test image, photorealistic"

    cfg_path = Path(gi.CONFIG_PATH)
    original_cfg = None
    if cfg_path.exists():
        original_cfg = cfg_path.read_text()
    try:
        cfg_path.write_text(json.dumps({"default_size": "64x64", "default_format": "png", "default_output_dir": str(tmp_path)}))
        out_file = tmp_path / "out.png"

        # Call Runware API (real) and save
        resp = gi.call_runware_generate(api_key, prompt, size="64x64", output_format="png", sync=True)
        b64 = gi.extract_base64_from_response(resp)
        gi.save_output_image(b64, out_file)

        assert out_file.exists()
        assert out_file.stat().st_size > 0
    finally:
        if original_cfg is not None:
            cfg_path.write_text(original_cfg)
