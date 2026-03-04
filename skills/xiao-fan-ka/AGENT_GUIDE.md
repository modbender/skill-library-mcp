# 小饭卡 - Agent技术指引（内部）

## 首次使用

```bash
python3 {baseDir}/scripts/onboard.py init --city 北京 --areas "三里屯,工体"
python3 {baseDir}/scripts/onboard.py add-fav "鲤承" --reason "精致小馆" --price 200 --area "三里屯"
python3 {baseDir}/scripts/onboard.py add-dislike "小吊梨汤" --reason "太连锁"
python3 {baseDir}/scripts/onboard.py finish
```

add-fav之前必须先搜索确认店名。

## 搜索

```bash
python3 {baseDir}/scripts/search.py "三里屯 创意菜" [--city 北京] [--max 20] [--json]
python3 {baseDir}/scripts/search_xhs.py "三里屯 宝藏餐厅" [--max 10] [--json]
python3 {baseDir}/scripts/search_all.py "三里屯 创意菜" [--city 北京] [--max 10]
```

## 画像管理

```bash
python3 {baseDir}/scripts/profile.py add "餐厅名" --tags "标签" --feeling "喜欢" --price 200 --area "三里屯"
python3 {baseDir}/scripts/profile.py remove "餐厅名"
python3 {baseDir}/scripts/profile.py list
python3 {baseDir}/scripts/profile.py analyze
python3 {baseDir}/scripts/profile.py export
python3 {baseDir}/scripts/profile.py reset
```

## 推荐原则

- 像朋友聊天，2-3句话，不写报告
- 2+1模式：2家精准 + 1家有根据的冒险
- 场景感知：能推断就别问
- 搜索确认再记录，不瞎记
- 没好的就说没有，不凑数
- 警惕刷评：新店全好评长文要提醒；街边小店3.5-4分才真实（陈晓卿定律）

## 依赖

- ddgs (`pip3 install ddgs`)
- 代理：`DDGS_PROXY` 环境变量

## 数据

- `{baseDir}/data/taste-profile.json`
