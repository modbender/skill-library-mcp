#!/usr/bin/env python3
# Wav2Lip - 让照片说话
import cv2
import sys
import os

def create_talking_video(image_path, audio_path, output_path="output.mp4"):
    """
    简易版：将图片和音频合并成视频
    注意：这是简化版本，完整的 Wav2Lip 需要深度学习模型
    """
    
    print(f"📸 加载图片: {image_path}")
    img = cv2.imread(image_path)
    
    if img is None:
        print(f"❌ 无法加载图片: {image_path}")
        return None
    
    height, width, _ = img.shape
    
    # 创建视频写入器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 25
    video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # 计算音频时长（秒）
    # 简化版：假设 3 秒
    duration = 3
    total_frames = int(fps * duration)
    
    print(f"🎬 生成视频帧...")
    for i in range(total_frames):
        video.write(img)
    
    video.release()
    print(f"✅ 视频已生成: {output_path}")
    print(f"⚠️  注意：这是静态图片视频，完整的嘴型同步需要 Wav2Lip 模型")
    
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 wav2lip_simple.py <图片> <音频> [输出视频]")
        sys.exit(1)
    
    image = sys.argv[1]
    audio = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) > 3 else "talking.mp4"
    
    create_talking_video(image, audio, output)
