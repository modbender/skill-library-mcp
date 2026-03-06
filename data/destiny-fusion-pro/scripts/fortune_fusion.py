#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from collections import Counter

from iztro_py import astro
from lunar_python import Solar

GAN_WUXING = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
ZHI_WUXING = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}
BRANCHES = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]


def shichen_index(h, m):
    t = h * 60 + m
    if t >= 23*60 or t < 60:
        return 0
    return ((t - 60)//120) + 1


def apply_longitude(date_text: str, time_text: str, lng: float | None):
    dt = datetime.strptime(f"{date_text} {time_text}", "%Y-%m-%d %H:%M")
    if lng is None:
        return dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M'), 0
    off = int(round((lng - 120.0) * 4))
    ndt = dt + timedelta(minutes=off)
    return ndt.strftime('%Y-%m-%d'), ndt.strftime('%H:%M'), off


def zwds_block(date_text, time_text, gender, longitude, year):
    ndate, ntime, off = apply_longitude(date_text, time_text, longitude)
    h, m = map(int, ntime.split(':'))
    idx = shichen_index(h, m)
    g = '男' if str(gender).lower() in ('male','男','m','1') else '女'
    chart = astro.by_solar(ndate, idx, g)

    palaces = []
    for i in range(12):
        p = chart.palace(i)
        palaces.append({
            'name': p.translate_name(),
            'stem_branch': f"{p.translate_heavenly_stem()}{p.translate_earthly_branch()}",
            'major': [s.translate_name() for s in p.major_stars]
        })

    ming = next((p for p in palaces if p['name'] == '命宫'), None)
    body = chart.get_body_palace().translate_name()

    hblock = None
    if year:
        hs = chart.horoscope(f"{year}-06-01")
        d = chart.palace(hs.decadal.index)
        y = chart.palace(hs.yearly.index)
        a = chart.palace(hs.age.index)
        hblock = {
            'year': year,
            'decadal': {'palace': d.translate_name(), 'major': [s.translate_name() for s in d.major_stars]},
            'yearly': {'palace': y.translate_name(), 'major': [s.translate_name() for s in y.major_stars]},
            'age': {'name': hs.age.name, 'palace': a.translate_name()},
            'mutagen': hs.yearly.mutagen or []
        }

    return {
        'normalized': {'date': ndate, 'time': ntime, 'offset_min': off, 'hour_index': idx, 'hour_branch': BRANCHES[idx]},
        'five_elements_class': chart.five_elements_class,
        'body_palace': body,
        'ming_palace': ming,
        'horoscope': hblock,
        'palaces': palaces,
    }


def bazi_block(date_text, time_text, gender, sect, from_year, years):
    y,m,d = map(int, date_text.split('-'))
    hh,mm = map(int, time_text.split(':'))
    solar = Solar.fromYmdHms(y,m,d,hh,mm,0)
    lunar = solar.getLunar()
    ec = lunar.getEightChar(); ec.setSect(sect)

    pillars = {
        'year': ec.getYear(), 'month': ec.getMonth(), 'day': ec.getDay(), 'time': ec.getTime(),
    }

    cnt = Counter()
    for gz in pillars.values():
        cnt[GAN_WUXING.get(gz[0],'?')] += 1
        cnt[ZHI_WUXING.get(gz[1],'?')] += 1

    is_male = str(gender).lower() in ('male','男','m','1')
    yun = ec.getYun(1 if is_male else 0)
    dayun = []
    for dy in yun.getDaYun()[:8]:
        if dy.getIndex() == 0:
            continue
        dayun.append({'idx': dy.getIndex(), 'age': f"{dy.getStartAge()}-{dy.getEndAge()}", 'ganzhi': dy.getGanZhi()})

    start = from_year or datetime.now().year
    liunian = []
    for yy in range(start, start + max(1, years)):
        yl = Solar.fromYmdHms(yy,6,30,12,0,0).getLunar().getEightChar().getYear()
        liunian.append({'year': yy, 'ganzhi': yl})

    return {
        'lunar': f"{lunar.getYearInChinese()}年{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}",
        'pillars': pillars,
        'day_master': pillars['day'][0],
        'minggong': ec.getMingGong(),
        'shengong': ec.getShenGong(),
        'taiyuan': ec.getTaiYuan(),
        'wuxing_count': dict(cnt),
        'dayun': dayun,
        'liunian': liunian,
    }


def render_md(payload, template='pro'):
    z = payload['ziwei']; b = payload['bazi']; c = payload['consulting']
    lines = [
        '# Destiny Fusion Pro Report（紫微斗数 + 八字）','',
        f"- 输入：{payload['input']['date']} {payload['input']['time']} / {payload['input']['gender']}",
        f"- 紫微修正后时间：{z['normalized']['date']} {z['normalized']['time']}（{z['normalized']['offset_min']} 分钟）",
        '',
        '## A) 紫微斗数核心',
        f"- 五行局：{z['five_elements_class']}",
        f"- 身宫：{z['body_palace']}",
        f"- 命宫：{z['ming_palace']['stem_branch']}（主星：{', '.join(z['ming_palace']['major']) or '无'}）",
    ]
    if z.get('horoscope'):
        h = z['horoscope']
        lines += [
            f"- {h['year']} 锚点：大运宫={h['decadal']['palace']}，流年宫={h['yearly']['palace']}，岁位={h['age']['name']}@{h['age']['palace']}",
            f"- 四化键：{', '.join(h['mutagen']) if h['mutagen'] else '无'}",
        ]

    w = b['wuxing_count']
    lines += [
        '',
        '## B) 八字核心',
        f"- 四柱：{b['pillars']['year']} / {b['pillars']['month']} / {b['pillars']['day']} / {b['pillars']['time']}",
        f"- 日主：{b['day_master']}｜命宫：{b['minggong']}｜身宫：{b['shengong']}｜胎元：{b['taiyuan']}",
        f"- 五行：木{w.get('木',0)} 火{w.get('火',0)} 土{w.get('土',0)} 金{w.get('金',0)} 水{w.get('水',0)}",
        '',
    ]

    if template == 'lite':
        lines += [
            '## C) 快速结论（Lite）',
            f"- 一句话定位：{c['positioning']}",
            f"- 本期重点：{c['career']}",
            f"- 风险：{c['risk']}",
            '',
            '## D) 大运与流年（节选）',
        ]
    elif template == 'executive':
        lines += [
            '## C) 高净值咨询摘要（Executive）',
            f"- 战略定位：{c['positioning']}",
            f"- 事业/商业：{c['career']}",
            f"- 家庭/关系治理：{c['relationship']}",
            f"- 身心与节律：{c['health']}",
            f"- 资产与风控：{c['finance']}",
            f"- 关键风险：{c['risk']}",
            '',
            '## D) 大运与流年（节选）',
        ]
    else:
        lines += [
            '## C) 咨询交付摘要（Pro）',
            f"- 综合定位：{c['positioning']}",
            f"- 事业建议：{c['career']}",
            f"- 关系建议：{c['relationship']}",
            f"- 健康建议：{c['health']}",
            f"- 财务建议：{c['finance']}",
            f"- 风险提示：{c['risk']}",
            '',
            '## D) 大运与流年（节选）',
        ]
    for d in b['dayun'][:5]:
        lines.append(f"- 大运{d['idx']}：{d['age']}岁 {d['ganzhi']}")
    for ly in b['liunian'][:5]:
        lines.append(f"- 流年：{ly['year']} {ly['ganzhi']}")
    lines += ['', '- 免责声明：本报告属于传统命理研究与咨询辅助，不构成医疗、法律、投资建议。']
    return '\n'.join(lines)


def consulting_template(ziwei, bazi):
    dm = bazi['day_master']
    ming_star = ','.join(ziwei['ming_palace']['major']) if ziwei['ming_palace'] else ''
    return {
        'positioning': f"日主{dm}，命宫主星{ming_star or '未见主星'}，适合走“长期主义 + 专业壁垒”路径。",
        'career': '优先布局可复利的专业能力，年度目标以“可量化产出”拆解执行。',
        'relationship': '减少高压沟通，采用“事实-感受-需求”三段表达，稳定关系质量。',
        'health': '作息比强度更重要，建议固定睡眠窗口与低冲击运动（普拉提/步行）。',
        'finance': '分层仓位与止损纪律并行，避免单一高波动资产过度集中。',
        'risk': '若出生时刻靠近时辰边界，建议双盘复核；重大决策需结合现实数据。'
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date', required=True)
    ap.add_argument('--time', required=True)
    ap.add_argument('--gender', required=True)
    ap.add_argument('--longitude', type=float, default=None)
    ap.add_argument('--year', type=int, default=None)
    ap.add_argument('--sect', type=int, default=2)
    ap.add_argument('--from-year', type=int, default=None)
    ap.add_argument('--years', type=int, default=10)
    ap.add_argument('--template', choices=['lite','pro','executive'], default='pro')
    ap.add_argument('--format', choices=['markdown','json'], default='markdown')
    args = ap.parse_args()

    z = zwds_block(args.date, args.time, args.gender, args.longitude, args.year)
    b = bazi_block(args.date, args.time, args.gender, args.sect, args.from_year, args.years)
    payload = {
        'input': {'date': args.date, 'time': args.time, 'gender': args.gender, 'longitude': args.longitude},
        'ziwei': z,
        'bazi': b,
        'consulting': consulting_template(z, b)
    }

    if args.format == 'json':
        payload['template'] = args.template
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_md(payload, args.template))


if __name__ == '__main__':
    main()
