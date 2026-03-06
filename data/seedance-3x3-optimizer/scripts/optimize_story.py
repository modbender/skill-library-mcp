#!/usr/bin/env python3
import argparse
import json


def build_action(story: str, title: str, style: str):
    s = story.strip()
    return [
        f"【段落01｜对峙】{title}。场景先给出极端尺度对比：主角立于边缘地带，远处威胁体从高空/黑云中显形，阴影先到，压住地面与人群。整体风格为{style}。",
        "【段落02｜对峙】镜头压低，主角起势：握紧武器或收紧拳峰，呼吸可见，衣角与发丝被无形气流牵动，脚下出现细密裂纹与微小碎石浮动。",
        "【段落03｜对峙】反派先手试探：重击或能量压制落下，周边建筑/地面产生真实反馈（崩落、震颤、烟尘），让危险先被看见再被解释。",
        "【段落04｜爆发】主角高速闪避并反击，动作带清晰轨迹线与残影；镜头跟随半弧运动，保留空间方位，避免“站桩对轰”。",
        "【段落05｜爆发】切情绪特写：瞳孔收缩、汗珠滑落、下颌收紧，呼吸节奏可见；把“愤怒/恐惧/决心”变成可拍到的生理细节。",
        "【段落06｜爆发】绝技蓄力：武器符文逐点亮起，能量向中心聚拢，空气出现折射与微粒回卷，短暂停顿制造爆发前真空。",
        "【段落07｜终结】终极对撞使用双色冲突（如金 vs 紫、冷蓝 vs 暖红）；碰撞点先白化后扩散，冲击波分层推开云层/尘土。",
        "【段落08｜终结】破碎反馈进入慢动作：敌方护甲或巨构表面出现蛛网裂纹并分片剥落，碎片与火星沿透视线飞散。",
        "【段落09｜终结】尘埃落定：环境由高对比回归平静，光线转暖或回冷；主角收势离场，留下可记忆的余韵画面（裂地、残光、长影）。",
    ]


def build_emotion(story: str, title: str, style: str):
    s = story.strip()
    return [
        f"【段落01｜和谐】{title}。先建立温暖关系场：两人同框且有自然互动，阳光/室内暖光包裹人物，氛围基调为{style}。",
        "【段落02｜和谐】细节定格到手部或信物：交握、递交、触碰停顿。背景虚化，突出“关系证据”，让观众先相信他们曾亲密。",
        "【段落03｜和谐→裂痕】光线与天气先变：云层压下、色温变冷、风声或雨点进入画面；其中一人率先收回动作，形成第一道心理距离。",
        "【段落04｜裂痕】争执爆发但避免喊口号：用站位变化表达冲突（并肩→对立），再给到拳头、肩线、下唇咬紧等压抑动作。",
        "【段落05｜裂痕】眼神特写承载情绪：瞳孔震颤、眼眶泛红、泪水停在睫毛边缘；把“委屈/失望”翻译为微表情与呼吸停顿。",
        "【段落06｜裂痕】物理距离继续拉开：背对背、隔门/隔雨幕、明暗分区。两人处在同一场景，却被光线切成两个世界。",
        "【段落07｜决裂】关键选择必须可视化：放下、撕毁或摔碎一个象征关系的物件，让抽象‘结束’变成可被镜头记录的事件。",
        "【段落08｜决裂】最后一瞥：一人离场的背影逐步消失，另一人停在原地，伸手但没有挽留，动作在半空中停住。",
        "【段落09｜余韵】空镜收尾：雨、风、树影、遗留物。不给解释台词，只给环境反应，让情绪在静止画面里继续回响。",
    ]


def main():
    p = argparse.ArgumentParser(description="Rewrite plain story into Seedance 3x3 visual script")
    p.add_argument("--story", required=True, help="原始剧情，1-3 句即可")
    p.add_argument("--mode", choices=["action", "emotion"], default="action")
    p.add_argument("--title", default="3x3 剧情优化")
    p.add_argument("--style", default="电影感")
    p.add_argument("--json", action="store_true", help="输出 JSON")
    args = p.parse_args()

    paragraphs = build_action(args.story, args.title, args.style) if args.mode == "action" else build_emotion(args.story, args.title, args.style)

    payload = {
        "mode": args.mode,
        "title": args.title,
        "original_story": args.story.strip(),
        "seedance_3x3": paragraphs,
        "tips": [
            "每段建议 50-120 字，避免纯抽象形容词。",
            "至少包含一个镜头指令 + 一个环境反馈 + 一个人物生理细节。",
            "可在 Seedance 中把 9 段串行生成，再做节奏微调。",
        ],
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print(f"# {args.title}（{args.mode}）\n")
    print("## 原始剧情")
    print(args.story.strip() + "\n")
    print("## 3x3 优化稿")
    for row in paragraphs:
        print(f"- {row}")
    print("\n## 使用建议")
    for t in payload["tips"]:
        print(f"- {t}")


if __name__ == "__main__":
    main()
