#!/usr/bin/env python3
"""八字排盘（增强版）

功能：
- 四柱（年/月/日/时）
- 日主、十神（天干+地支藏干）
- 纳音、旬空
- 五行统计（天干+地支主气+藏干）
- 命宫/身宫/胎元
- 大运起运信息 + 前8步大运
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from typing import Dict, Any, List
from datetime import datetime

from lunar_python import Solar

GAN_WUXING = {
    '甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'
}
ZHI_WUXING = {
    '子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'
}


def pillar_bundle(ec, key: str) -> Dict[str, Any]:
    title = key.capitalize()
    gz = getattr(ec, f"get{title}")()
    gan = getattr(ec, f"get{title}Gan")()
    zhi = getattr(ec, f"get{title}Zhi")()
    return {
        "ganzhi": gz,
        "gan": gan,
        "zhi": zhi,
        "wuxing": getattr(ec, f"get{title}WuXing")(),
        "nayin": getattr(ec, f"get{title}NaYin")(),
        "xun": getattr(ec, f"get{title}Xun")(),
        "xunkong": getattr(ec, f"get{title}XunKong")(),
        "dishi": getattr(ec, f"get{title}DiShi")(),
        "shishen_gan": getattr(ec, f"get{title}ShiShenGan")(),
        "shishen_zhi": getattr(ec, f"get{title}ShiShenZhi")(),
        "hide_gan": getattr(ec, f"get{title}HideGan")(),
    }


def _season_by_month_zhi(month_zhi: str) -> str:
    if month_zhi in ('寅','卯','辰'):
        return 'spring'
    if month_zhi in ('巳','午','未'):
        return 'summer'
    if month_zhi in ('申','酉','戌'):
        return 'autumn'
    return 'winter'


def _yong_ji_shen(day_master: str, month_zhi: str) -> Dict[str, List[str]]:
    """简化版用忌神建议（工程规则，不替代专业人工断盘）"""
    season = _season_by_month_zhi(month_zhi)
    group = 'metal_water' if day_master in ('庚','辛','壬','癸') else 'wood_fire'
    if group == 'metal_water':
        if season == 'autumn':
            return {'yongshen':['火','木'], 'jishen':['金','水'], 'reason':'秋金偏旺，宜火制金、木疏土生火'}
        if season == 'winter':
            return {'yongshen':['火','土'], 'jishen':['水','金'], 'reason':'冬水寒，宜火暖局、土制水'}
        if season == 'spring':
            return {'yongshen':['土','金'], 'jishen':['木','火'], 'reason':'春木旺，宜土金平衡木势'}
        return {'yongshen':['水','木'], 'jishen':['火','土'], 'reason':'夏火旺，宜水润木生'}
    else:
        if season == 'spring':
            return {'yongshen':['金','土'], 'jishen':['木','水'], 'reason':'春木旺，宜金土制衡'}
        if season == 'summer':
            return {'yongshen':['水','金'], 'jishen':['火','木'], 'reason':'夏火旺，宜水金调候'}
        if season == 'autumn':
            return {'yongshen':['木','火'], 'jishen':['金','土'], 'reason':'秋金燥，宜木火通关'}
        return {'yongshen':['火','木'], 'jishen':['水','土'], 'reason':'冬寒湿，宜火木扶阳'}


def build(date_text: str, time_text: str, gender: str, sect: int, from_year: int | None, years: int) -> Dict[str, Any]:
    y,m,d = map(int, date_text.split('-'))
    hh,mm = map(int, time_text.split(':'))

    solar = Solar.fromYmdHms(y,m,d,hh,mm,0)
    lunar = solar.getLunar()
    ec = lunar.getEightChar()
    ec.setSect(sect)

    pillars = {
        'year': pillar_bundle(ec, 'year'),
        'month': pillar_bundle(ec, 'month'),
        'day': pillar_bundle(ec, 'day'),
        'time': pillar_bundle(ec, 'time'),
    }

    # 五行统计：天干 + 地支主五行 + 藏干
    cnt = Counter()
    for k in ['year','month','day','time']:
        g = pillars[k]['gan']
        z = pillars[k]['zhi']
        cnt[GAN_WUXING.get(g,'?')] += 1
        cnt[ZHI_WUXING.get(z,'?')] += 1
        for hg in pillars[k]['hide_gan']:
            if hg:
                cnt[GAN_WUXING.get(hg,'?')] += 1

    is_male = gender.lower() in ('male','男','m','1')
    yun = ec.getYun(1 if is_male else 0)
    dayun = []
    for dy in yun.getDaYun()[:8]:
        if dy.getIndex() == 0:
            continue
        dayun.append({
            'index': dy.getIndex(),
            'start_age': dy.getStartAge(),
            'end_age': dy.getEndAge(),
            'ganzhi': dy.getGanZhi(),
            'xun': dy.getXun(),
            'xunkong': dy.getXunKong(),
        })

    yj = _yong_ji_shen(pillars['day']['gan'], pillars['month']['zhi'])

    start_year = from_year or datetime.now().year
    liunian = []
    for yy in range(start_year, start_year + max(1, years)):
        # 按公历年中点推流年干支
        ysolar = Solar.fromYmdHms(yy, 6, 30, 12, 0, 0)
        yl = ysolar.getLunar().getEightChar().getYear()
        liunian.append({'year': yy, 'ganzhi': yl})

    return {
        'input': {'date': date_text, 'time': time_text, 'gender': gender, 'sect': sect},
        'solar': f"{y:04d}-{m:02d}-{d:02d} {hh:02d}:{mm:02d}",
        'lunar': f"{lunar.getYearInChinese()}年{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}",
        'pillars': pillars,
        'day_master': pillars['day']['gan'],
        'taiyuan': ec.getTaiYuan(),
        'minggong': ec.getMingGong(),
        'shengong': ec.getShenGong(),
        'taixi': ec.getTaiXi(),
        'wuxing_count': dict(cnt),
        'yun': {
            'start_offset': {
                'year': yun.getStartYear(),
                'month': yun.getStartMonth(),
                'day': yun.getStartDay(),
                'hour': yun.getStartHour(),
            },
            'start_solar': str(yun.getStartSolar()),
            'dayun': dayun,
            'liunian': liunian,
        },
        'yong_ji_shen': yj,
        'note': '本结果为传统命理分析，不构成医疗、法律或投资建议。'
    }


def to_md(p: Dict[str, Any]) -> str:
    lines = []
    i = p['input']
    lines += [
        '# 八字排盘结果（增强版）','',
        f"- 输入：{i['date']} {i['time']} / {i['gender']} / sect={i['sect']}",
        f"- 农历：{p['lunar']}",
        f"- 年柱：{p['pillars']['year']['ganzhi']}",
        f"- 月柱：{p['pillars']['month']['ganzhi']}",
        f"- 日柱：{p['pillars']['day']['ganzhi']}（日主：{p['day_master']}）",
        f"- 时柱：{p['pillars']['time']['ganzhi']}",
        f"- 命宫：{p['minggong']} / 身宫：{p['shengong']} / 胎元：{p['taiyuan']}",
        ''
    ]
    lines.append('## 十神与藏干')
    for k, cn in [('year','年柱'),('month','月柱'),('day','日柱'),('time','时柱')]:
        x = p['pillars'][k]
        lines.append(f"- {cn}：{x['ganzhi']}｜天干十神={x['shishen_gan']}｜地支十神={','.join(x['shishen_zhi'])}｜藏干={','.join(x['hide_gan'])}")

    w = p['wuxing_count']
    lines += [
        '',
        '## 五行统计（含藏干）',
        f"- 木：{w.get('木',0)}",
        f"- 火：{w.get('火',0)}",
        f"- 土：{w.get('土',0)}",
        f"- 金：{w.get('金',0)}",
        f"- 水：{w.get('水',0)}",
        ''
    ]

    y = p['yun']
    o = y['start_offset']
    yj = p['yong_ji_shen']
    lines += [
        '## 用神/忌神（规则引擎建议）',
        f"- 用神建议：{', '.join(yj['yongshen'])}",
        f"- 忌神提醒：{', '.join(yj['jishen'])}",
        f"- 依据：{yj['reason']}",
        '',
        '## 大运',
        f"- 起运偏移：{o['year']}年{o['month']}个月{o['day']}天{o['hour']}小时",
        f"- 起运公历：{y['start_solar']}",
        ''
    ]
    for d in y['dayun']:
        lines.append(f"- 第{d['index']}步：{d['start_age']}-{d['end_age']}岁｜{d['ganzhi']}（旬：{d['xun']}，空亡：{d['xunkong']}）")

    lines += ['', '## 近年流年（干支）']
    for ly in y['liunian']:
        lines.append(f"- {ly['year']}：{ly['ganzhi']}")

    lines += ['', f"- 备注：{p['note']}"]
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date', required=True, help='YYYY-MM-DD')
    ap.add_argument('--time', required=True, help='HH:MM')
    ap.add_argument('--gender', required=True, help='male/female/男/女')
    ap.add_argument('--sect', type=int, choices=[1,2], default=2, help='八字流派参数，默认2')
    ap.add_argument('--from-year', type=int, default=None, help='流年起始年份，默认当前年')
    ap.add_argument('--years', type=int, default=10, help='生成流年年数，默认10')
    ap.add_argument('--format', choices=['markdown','json'], default='markdown')
    args = ap.parse_args()

    payload = build(args.date, args.time, args.gender, args.sect, args.from_year, args.years)
    if args.format == 'json':
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(to_md(payload))


if __name__ == '__main__':
    main()
