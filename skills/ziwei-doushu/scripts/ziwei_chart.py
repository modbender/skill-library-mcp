#!/usr/bin/env python3
"""
Ziwei Doushu chart generator (enhanced, iztro-py based)

Example:
  python scripts/ziwei_chart.py --date 1989-10-17 --time 12:00 --gender male --longitude 117.9 --year 2026
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

from iztro_py import astro

BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

MUTAGEN_LABELS = ["化禄", "化权", "化科", "化忌"]
STAR_KEY_CN = {
    'taiyinMaj':'太阴','tiantongMaj':'天同','tianjiMaj':'天机','jumenMaj':'巨门','wuquMaj':'武曲','tanlangMaj':'贪狼','tianliangMaj':'天梁','wenquMin':'文曲',
    'pojunMaj':'破军','wenchangMin':'文昌','lianzhenMaj':'廉贞','ziweiMaj':'紫微'
}



def parse_time_hhmm(text: str) -> tuple[int, int]:
    dt = datetime.strptime(text, "%H:%M")
    return dt.hour, dt.minute


def to_shichen_index(hour: int, minute: int) -> int:
    total_min = hour * 60 + minute
    if total_min >= 23 * 60 or total_min < 60:
        return 0
    return ((total_min - 60) // 120) + 1


def apply_longitude_correction(date_text: str, time_text: str, longitude: float | None) -> tuple[str, str, int]:
    dt = datetime.strptime(f"{date_text} {time_text}", "%Y-%m-%d %H:%M")
    if longitude is None:
        return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M"), 0
    offset_minutes = int(round((longitude - 120.0) * 4))
    corrected = dt + timedelta(minutes=offset_minutes)
    return corrected.strftime("%Y-%m-%d"), corrected.strftime("%H:%M"), offset_minutes


def trans_stars(stars: List[Any]) -> List[str]:
    out = []
    for s in stars:
        try:
            out.append(s.translate_name())
        except Exception:
            out.append(str(s))
    return out


def build_chart(date_text: str, time_text: str, gender: str, longitude: float | None, year: int | None) -> Dict[str, Any]:
    corrected_date, corrected_time, offset_minutes = apply_longitude_correction(date_text, time_text, longitude)
    h, m = parse_time_hhmm(corrected_time)
    hour_index = to_shichen_index(h, m)

    gender_map = {"male": "男", "female": "女", "男": "男", "女": "女"}
    g = gender_map.get(gender.lower() if isinstance(gender, str) else gender, gender)
    if g not in ("男", "女"):
        raise ValueError("gender 仅支持 male/female/男/女")

    chart = astro.by_solar(corrected_date, hour_index, g)

    palaces = []
    decadals = []
    for i in range(12):
        p = chart.palace(i)
        item = {
            "index": i,
            "name": p.translate_name(),
            "stem": p.translate_heavenly_stem(),
            "branch": p.translate_earthly_branch(),
            "major_stars": trans_stars(p.major_stars),
            "minor_stars": trans_stars(p.minor_stars),
            "adjective_stars": trans_stars(p.adjective_stars),
        }
        palaces.append(item)
        try:
            r = p.decadal.range
            decadals.append({
                "palace": p.translate_name(),
                "stem_branch": f"{p.translate_heavenly_stem()}{p.translate_earthly_branch()}",
                "start_age": r[0],
                "end_age": r[1],
                "major_stars": item["major_stars"],
            })
        except Exception:
            pass

    decadals.sort(key=lambda x: x["start_age"])

    ming = next((x for x in palaces if x["name"] == "命宫"), None)
    body_palace = chart.get_body_palace().translate_name()

    ming_context = None
    if ming:
        i = ming['index']
        idxs = [i, (i + 4) % 12, (i + 8) % 12, (i + 6) % 12]
        names = ['本宫','三方一','三方二','对宫']
        related = []
        for tag, idx in zip(names, idxs):
            p = palaces[idx]
            related.append({'tag': tag, 'palace': p['name'], 'stem_branch': f"{p['stem']}{p['branch']}", 'major_stars': p['major_stars']})
        ming_context = {'indices': idxs, 'related': related}

    horoscope = None
    if year:
        hs = chart.horoscope(f"{year}-06-01")
        decadal_palace = chart.palace(hs.decadal.index)
        yearly_palace = chart.palace(hs.yearly.index)
        age_palace = chart.palace(hs.age.index)
        muta = []
        for idx, key in enumerate(hs.yearly.mutagen or []):
            muta.append({'type': MUTAGEN_LABELS[idx] if idx < 4 else f'化{idx+1}', 'star_key': key, 'star': STAR_KEY_CN.get(key, key)})

        horoscope = {
            "year": year,
            "decadal": {
                "palace": decadal_palace.translate_name(),
                "stem_branch": f"{decadal_palace.translate_heavenly_stem()}{decadal_palace.translate_earthly_branch()}",
                "major_stars": trans_stars(decadal_palace.major_stars),
            },
            "yearly": {
                "palace": yearly_palace.translate_name(),
                "stem_branch": f"{yearly_palace.translate_heavenly_stem()}{yearly_palace.translate_earthly_branch()}",
                "major_stars": trans_stars(yearly_palace.major_stars),
                "mutagen": muta,
            },
            "age": {
                "name": hs.age.name,
                "palace": age_palace.translate_name(),
                "branch": age_palace.translate_earthly_branch(),
            },
        }

    return {
        "input": {"date": date_text, "time": time_text, "gender": g, "longitude": longitude},
        "normalized": {
            "date": corrected_date,
            "time": corrected_time,
            "hour_index": hour_index,
            "hour_branch": BRANCHES[hour_index],
            "offset_minutes": offset_minutes,
        },
        "summary": {
            "five_elements_class": chart.five_elements_class,
            "body_palace": body_palace,
            "ming_palace": ming,
        },
        "ming_context": ming_context,
        "decadals": decadals,
        "horoscope": horoscope,
        "palaces": palaces,
    }


def to_markdown(payload: Dict[str, Any]) -> str:
    lines = []
    inp = payload["input"]
    norm = payload["normalized"]
    summary = payload["summary"]

    lines.append("# 紫微斗数排盘结果（增强版）")
    lines.append("")
    lines.append(f"- 输入：{inp['date']} {inp['time']} / {inp['gender']}")
    if inp["longitude"] is not None:
        lines.append(f"- 经度修正：{inp['longitude']}° -> {norm['date']} {norm['time']}（{norm['offset_minutes']} 分钟）")
    lines.append(f"- 时辰索引：{norm['hour_index']}（{norm['hour_branch']}时）")
    lines.append(f"- 五行局：{summary['five_elements_class']}")
    lines.append(f"- 身宫：{summary['body_palace']}")

    ming = summary.get("ming_palace")
    if ming:
        lines.append(f"- 命宫：{ming['stem']}{ming['branch']}（主星：{', '.join(ming['major_stars']) if ming['major_stars'] else '无'}）")

    if payload.get("horoscope"):
        h = payload["horoscope"]
        lines.append("")
        lines.append(f"## {h['year']} 年运势锚点")
        lines.append(f"- 大运宫：{h['decadal']['palace']}（{h['decadal']['stem_branch']}）主星：{', '.join(h['decadal']['major_stars']) or '无'}")
        lines.append(f"- 流年宫：{h['yearly']['palace']}（{h['yearly']['stem_branch']}）主星：{', '.join(h['yearly']['major_stars']) or '无'}")
        if h['yearly'].get('mutagen'):
            lines.append("- 四化：" + '，'.join([f"{m['type']}->{m['star']}" for m in h['yearly']['mutagen']]))
        lines.append(f"- 当年岁位：{h['age']['name']}，落{h['age']['palace']}（{h['age']['branch']}宫）")

    if payload.get('ming_context'):
        lines.append('')
        lines.append('## 命宫三方四正')
        for r in payload['ming_context']['related']:
            lines.append(f"- {r['tag']}：{r['palace']}（{r['stem_branch']}）主星：{', '.join(r['major_stars']) or '无'}")

    if payload.get("decadals"):
        lines.append("")
        lines.append("## 大运列表")
        for d in payload["decadals"]:
            lines.append(f"- {d['start_age']}-{d['end_age']}岁：{d['palace']}（{d['stem_branch']}）主星：{', '.join(d['major_stars']) or '无'}")

    lines.append("")
    lines.append("## 十二宫")
    lines.append("")
    for p in payload["palaces"]:
        lines.append(f"### {p['name']}（{p['stem']}{p['branch']}）")
        lines.append(f"- 主星：{', '.join(p['major_stars']) if p['major_stars'] else '无'}")
        lines.append(f"- 辅星：{', '.join(p['minor_stars']) if p['minor_stars'] else '无'}")
        lines.append(f"- 杂曜：{', '.join(p['adjective_stars']) if p['adjective_stars'] else '无'}")
        lines.append("")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--time", required=True, help="HH:MM")
    ap.add_argument("--gender", required=True, help="male/female/男/女")
    ap.add_argument("--longitude", type=float, default=None, help="出生地经度，用于真太阳时近似修正")
    ap.add_argument("--year", type=int, default=None, help="可选：输出指定年份的流年锚点")
    ap.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = ap.parse_args()

    payload = build_chart(args.date, args.time, args.gender, args.longitude, args.year)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(to_markdown(payload))


if __name__ == "__main__":
    main()
