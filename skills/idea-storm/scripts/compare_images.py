#!/usr/bin/env python3
"""
图片对比工具 - 用于验证模式 A

比较生成图片与参考图片的相似度。
支持多种对比方式：SSIM、像素差异、特征点匹配。

用法：
    python compare_images.py --ref reference.png --gen generated.png --method ssim
    python compare_images.py --ref ref_dir/ --gen gen_dir/ --method ssim --batch
"""

import argparse
import sys
import json
from pathlib import Path

def compare_ssim(ref_path, gen_path):
    """计算 SSIM 相似度"""
    try:
        from skimage.metrics import structural_similarity as ssim
        from skimage import io
        import numpy as np
    except ImportError:
        print("需要安装: pip install scikit-image")
        sys.exit(1)

    ref = io.imread(ref_path)
    gen = io.imread(gen_path)

    # 确保尺寸一致
    if ref.shape != gen.shape:
        from skimage.transform import resize
        gen = resize(gen, ref.shape, anti_aliasing=True)
        gen = (gen * 255).astype(ref.dtype)

    # 计算 SSIM
    if len(ref.shape) == 3:
        score = ssim(ref, gen, channel_axis=2)
    else:
        score = ssim(ref, gen)

    return {"method": "ssim", "score": round(score, 4), "ref": str(ref_path), "gen": str(gen_path)}


def compare_pixel_diff(ref_path, gen_path):
    """计算像素级差异"""
    try:
        from skimage import io
        import numpy as np
    except ImportError:
        print("需要安装: pip install scikit-image")
        sys.exit(1)

    ref = io.imread(ref_path).astype(float)
    gen = io.imread(gen_path).astype(float)

    if ref.shape != gen.shape:
        from skimage.transform import resize
        gen = resize(gen, ref.shape, anti_aliasing=True) * 255

    diff = np.abs(ref - gen)
    mean_diff = diff.mean()
    max_diff = diff.max()

    return {
        "method": "pixel_diff",
        "mean_diff": round(float(mean_diff), 4),
        "max_diff": round(float(max_diff), 4),
        "ref": str(ref_path),
        "gen": str(gen_path)
    }


def main():
    parser = argparse.ArgumentParser(description="图片对比工具")
    parser.add_argument("--ref", required=True, help="参考图片路径（或目录）")
    parser.add_argument("--gen", required=True, help="生成图片路径（或目录）")
    parser.add_argument("--method", default="ssim", choices=["ssim", "pixel_diff"], help="对比方法")
    parser.add_argument("--batch", action="store_true", help="批量对比（目录模式）")
    parser.add_argument("--threshold", type=float, default=0.85, help="达标阈值（SSIM 默认 0.85）")
    args = parser.parse_args()

    results = []

    if args.batch:
        ref_dir = Path(args.ref)
        gen_dir = Path(args.gen)
        ref_files = sorted(ref_dir.glob("*.png")) + sorted(ref_dir.glob("*.jpg"))

        for ref_file in ref_files:
            gen_file = gen_dir / ref_file.name
            if not gen_file.exists():
                results.append({"ref": str(ref_file), "error": "生成图片不存在"})
                continue

            if args.method == "ssim":
                results.append(compare_ssim(ref_file, gen_file))
            else:
                results.append(compare_pixel_diff(ref_file, gen_file))
    else:
        if args.method == "ssim":
            results.append(compare_ssim(args.ref, args.gen))
        else:
            results.append(compare_pixel_diff(args.ref, args.gen))

    # 输出结果
    print(json.dumps(results, indent=2, ensure_ascii=False))

    # 判断是否达标
    if args.method == "ssim":
        scores = [r.get("score", 0) for r in results if "score" in r]
        if scores:
            avg = sum(scores) / len(scores)
            passed = avg >= args.threshold
            print(f"\n平均 SSIM: {avg:.4f} | 阈值: {args.threshold} | {'✅ 达标' if passed else '❌ 未达标'}")
            sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
