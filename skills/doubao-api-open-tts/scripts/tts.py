#!/usr/bin/env python3
"""
火山引擎语音合成 (TTS) 工具
支持通过HTTP API将文字转换为语音 - V3接口
"""

import os
import sys
import json
import base64
import hashlib
import hmac
import time
import uuid
import requests
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

# API配置 - 火山引擎语音合成HTTP API V1
API_HOST = "openspeech.bytedance.com"
TTS_ENDPOINT = f"https://{API_HOST}/api/v1/tts"


# 默认音色 - 通用场景（豆包语音合成模型1.0）
DEFAULT_VOICE_TYPE = "zh_female_cancan_mars_bigtts"

# 支持的音色列表（通用场景 - 豆包语音合成模型1.0）
VOICE_TYPES = {
    # 通用场景 - 多情感音色
    "zh_male_lengkugege_emo_v2_mars_bigtts": "冷酷哥哥（多情感）",
    "zh_female_tianxinxiaomei_emo_v2_mars_bigtts": "甜心小美（多情感）",
    "zh_female_gaolengyujie_emo_v2_mars_bigtts": "高冷御姐（多情感）",
    "zh_male_aojiaobazong_emo_v2_mars_bigtts": "傲娇霸总（多情感）",
    "zh_male_guangzhoudege_emo_mars_bigtts": "广州德哥（多情感）",
    "zh_male_jingqiangkanye_emo_mars_bigtts": "京腔侃爷（多情感）",
    "zh_female_linjuayi_emo_v2_mars_bigtts": "邻居阿姨（多情感）",
    "zh_male_yourougongzi_emo_v2_mars_bigtts": "优柔公子（多情感）",
    "zh_male_ruyayichen_emo_v2_mars_bigtts": "儒雅男友（多情感）",
    "zh_male_junlangnanyou_emo_v2_mars_bigtts": "俊朗男友（多情感）",
    "zh_male_beijingxiaoye_emo_v2_mars_bigtts": "北京小爷（多情感）",
    "zh_female_roumeinvyou_emo_v2_mars_bigtts": "柔美女友（多情感）",
    "zh_male_yangguangqingnian_emo_v2_mars_bigtts": "阳光青年（多情感）",
    "zh_female_meilinvyou_emo_v2_mars_bigtts": "魅力女友（多情感）",
    "zh_female_shuangkuaisisi_emo_v2_mars_bigtts": "爽快思思（多情感）",
    "en_female_candice_emo_v2_mars_bigtts": "Candice（多情感）",
    "en_female_skye_emo_v2_mars_bigtts": "Serena（多情感）",
    "en_male_glen_emo_v2_mars_bigtts": "Glen（多情感）",
    "en_male_sylus_emo_v2_mars_bigtts": "Sylus（多情感）",
    "en_male_corey_emo_v2_mars_bigtts": "Corey（多情感）",
    "en_female_nadia_tips_emo_v2_mars_bigtts": "Nadia（多情感）",
    "zh_male_shenyeboke_emo_v2_mars_bigtts": "深夜播客（多情感）",
    
    # 通用场景 - 普通音色
    "zh_female_yingyujiaoyu_mars_bigtts": "Tina老师",
    "ICL_zh_female_wenrounvshen_239eff5e8ffa_tob": "温柔女神",
    "zh_female_vv_mars_bigtts": "Vivi",
    "zh_female_qinqienvsheng_moon_bigtts": "亲切女声",
    "ICL_zh_male_shenmi_v1_tob": "机灵小伙",
    "ICL_zh_female_wuxi_tob": "元气甜妹",
    "ICL_zh_female_wenyinvsheng_v1_tob": "知心姐姐",
    "zh_male_qingyiyuxuan_mars_bigtts": "阳光阿辰",
    "zh_male_xudong_conversation_wvae_bigtts": "快乐小东",
    "ICL_zh_male_lengkugege_v1_tob": "冷酷哥哥",
    "ICL_zh_female_feicui_v1_tob": "纯澈女生",
    "ICL_zh_female_yuxin_v1_tob": "初恋女友",
    "ICL_zh_female_xnx_tob": "贴心闺蜜",
    "ICL_zh_female_yry_tob": "温柔白月光",
    "ICL_zh_male_BV705_streaming_cs_tob": "炀炀",
    "en_male_jason_conversation_wvae_bigtts": "开朗学长",
    "zh_female_sophie_conversation_wvae_bigtts": "魅力苏菲",
    "ICL_zh_female_yilin_tob": "贴心妹妹",
    "zh_female_tianmeitaozi_mars_bigtts": "甜美桃子",
    "zh_female_qingxinnvsheng_mars_bigtts": "清新女声",
    "zh_female_zhixingnvsheng_mars_bigtts": "知性女声",
    "zh_male_qingshuangnanda_mars_bigtts": "清爽男大",
    "zh_female_linjianvhai_moon_bigtts": "邻家女孩",
    "zh_male_yuanboxiaoshu_moon_bigtts": "渊博小叔",
    "zh_male_yangguangqingnian_moon_bigtts": "阳光青年",
    "zh_female_tianmeixiaoyuan_moon_bigtts": "甜美小源",
    "zh_female_qingchezizi_moon_bigtts": "清澈梓梓",
    "zh_male_jieshuoxiaoming_moon_bigtts": "解说小明",
    "zh_female_kailangjiejie_moon_bigtts": "开朗姐姐",
    "zh_male_linjiananhai_moon_bigtts": "邻家男孩",
    "zh_female_tianmeiyueyue_moon_bigtts": "甜美悦悦",
    "zh_female_xinlingjitang_moon_bigtts": "心灵鸡汤",
    "ICL_zh_female_zhixingwenwan_tob": "知性温婉",
    "ICL_zh_male_nuanxintitie_tob": "暖心体贴",
    "ICL_zh_male_kailangqingkuai_tob": "开朗轻快",
    "ICL_zh_male_huoposhuanglang_tob": "活泼爽朗",
    "ICL_zh_male_shuaizhenxiaohuo_tob": "率真小伙",
    "zh_male_wenrouxiaoge_mars_bigtts": "温柔小哥",
    "zh_female_cancan_mars_bigtts": "灿灿/Shiny",
    "zh_female_shuangkuaisisi_moon_bigtts": "爽快思思/Skye",
    "zh_male_wennuanahu_moon_bigtts": "温暖阿虎/Alvin",
    "zh_male_shaonianzixin_moon_bigtts": "少年梓辛/Brayan",
    "ICL_zh_female_wenrouwenya_tob": "温柔文雅",
    
    # IP仿音
    "zh_male_hupunan_mars_bigtts": "沪普男",
    "zh_male_lubanqihao_mars_bigtts": "鲁班七号",
    "zh_female_yangmi_mars_bigtts": "林潇",
    "zh_female_linzhiling_mars_bigtts": "玲玲姐姐",
    "zh_female_jiyejizi2_mars_bigtts": "春日部姐姐",
    "zh_male_tangseng_mars_bigtts": "唐僧",
    "zh_male_zhuangzhou_mars_bigtts": "庄周",
    "zh_male_zhubajie_mars_bigtts": "猪八戒",
    "zh_female_ganmaodianyin_mars_bigtts": "感冒电音姐姐",
    "zh_female_naying_mars_bigtts": "直率英子",
    "zh_female_leidian_mars_bigtts": "女雷神",
    
    # 趣味口音
    "zh_female_yueyunv_mars_bigtts": "粤语小溏",
    "zh_male_yuzhouzixuan_moon_bigtts": "豫州子轩",
    "zh_female_daimengchuanmei_moon_bigtts": "呆萌川妹",
    "zh_male_guangxiyuanzhou_moon_bigtts": "广西远舟",
    "zh_male_zhoujielun_emo_v2_mars_bigtts": "双节棍小哥",
    "zh_female_wanwanxiaohe_moon_bigtts": "湾湾小何",
    "zh_female_wanqudashu_moon_bigtts": "湾区大叔",
    "zh_male_guozhoudege_moon_bigtts": "广州德哥",
    "zh_male_haoyuxiaoge_moon_bigtts": "浩宇小哥",
    "zh_male_beijingxiaoye_moon_bigtts": "北京小爷",
    "zh_male_jingqiangkanye_moon_bigtts": "京腔侃爷/Harmony",
    "zh_female_meituojieer_moon_bigtts": "妹坨洁儿",
    
    # 角色扮演
    "ICL_zh_female_chunzhenshaonv_e588402fb8ad_tob": "纯真少女",
    "ICL_zh_male_xiaonaigou_edf58cf28b8b_tob": "奶气小生",
    "ICL_zh_female_jinglingxiangdao_1beb294a9e3e_tob": "精灵向导",
    "ICL_zh_male_menyoupingxiaoge_ffed9fc2fee7_tob": "闷油瓶小哥",
    "ICL_zh_male_anrenqinzhu_cd62e63dcdab_tob": "黯刃秦主",
    "ICL_zh_male_badaozongcai_v1_tob": "霸道总裁",
    "ICL_zh_female_ganli_v1_tob": "妩媚可人",
    "ICL_zh_female_xiangliangya_v1_tob": "邪魅御姐",
    "ICL_zh_male_ms_tob": "嚣张小哥",
    "ICL_zh_male_you_tob": "油腻大叔",
    "ICL_zh_male_guaogongzi_v1_tob": "孤傲公子",
    "ICL_zh_male_huzi_v1_tob": "胡子叔叔",
    "ICL_zh_female_luoqing_v1_tob": "性感魅惑",
    "ICL_zh_male_bingruogongzi_tob": "病弱公子",
    "ICL_zh_female_bingjiao3_tob": "邪魅女王",
    "ICL_zh_male_aomanqingnian_tob": "傲慢青年",
    "ICL_zh_male_cujingnansheng_tob": "醋精男生",
    "ICL_zh_male_shuanglangshaonian_tob": "爽朗少年",
    "ICL_zh_male_sajiaonanyou_tob": "撒娇男友",
    "ICL_zh_male_wenrounanyou_tob": "温柔男友",
    "ICL_zh_male_wenshunshaonian_tob": "温顺少年",
    "ICL_zh_male_naigounanyou_tob": "粘人男友",
    "ICL_zh_male_sajiaonansheng_tob": "撒娇男生",
    "ICL_zh_male_huoponanyou_tob": "活泼男友",
    "ICL_zh_male_tianxinanyou_tob": "甜系男友",
    "ICL_zh_male_huoliqingnian_tob": "活力青年",
    "ICL_zh_male_kailangqingnian_tob": "开朗青年",
    "ICL_zh_male_lengmoxiongzhang_tob": "冷漠兄长",
    "ICL_zh_male_tiancaitongzhuo_tob": "天才同桌",
    "ICL_zh_male_pianpiangongzi_tob": "翩翩公子",
    "ICL_zh_male_mengdongqingnian_tob": "懵懂青年",
    "ICL_zh_male_lenglianxiongzhang_tob": "冷脸兄长",
    "ICL_zh_male_bingjiaoshaonian_tob": "病娇少年",
    "ICL_zh_male_bingjiaonanyou_tob": "病娇男友",
    "ICL_zh_male_bingruoshaonian_tob": "病弱少年",
    "ICL_zh_male_yiqishaonian_tob": "意气少年",
    "ICL_zh_male_ganjingshaonian_tob": "干净少年",
    "ICL_zh_male_lengmonanyou_tob": "冷漠男友",
    "ICL_zh_male_jingyingqingnian_tob": "精英青年",
    "ICL_zh_male_rexueshaonian_tob": "热血少年",
    "ICL_zh_male_qingshuangshaonian_tob": "清爽少年",
    "ICL_zh_male_zhongerqingnian_tob": "中二青年",
    "ICL_zh_male_lingyunqingnian_tob": "凌云青年",
    "ICL_zh_male_zifuqingnian_tob": "自负青年",
    "ICL_zh_male_bujiqingnian_tob": "不羁青年",
    "ICL_zh_male_ruyajunzi_tob": "儒雅君子",
    "ICL_zh_male_diyinchenyu_tob": "低音沉郁",
    "ICL_zh_male_lenglianxueba_tob": "冷脸学霸",
    "ICL_zh_male_ruyazongcai_tob": "儒雅总裁",
    "ICL_zh_male_shenchenzongcai_tob": "深沉总裁",
    "ICL_zh_male_xiaohouye_tob": "小侯爷",
    "ICL_zh_male_gugaogongzi_tob": "孤高公子",
    "ICL_zh_male_zhangjianjunzi_tob": "仗剑君子",
    "ICL_zh_male_wenrunxuezhe_tob": "温润学者",
    "ICL_zh_male_qinqieqingnian_tob": "亲切青年",
    "ICL_zh_male_wenrouxuezhang_tob": "温柔学长",
    "ICL_zh_male_gaolengzongcai_tob": "高冷总裁",
    "ICL_zh_male_lengjungaozhi_tob": "冷峻高智",
    "ICL_zh_male_chanruoshaoye_tob": "孱弱少爷",
    "ICL_zh_male_zixinqingnian_tob": "自信青年",
    "ICL_zh_male_qingseqingnian_tob": "青涩青年",
    "ICL_zh_male_xuebatongzhuo_tob": "学霸同桌",
    "ICL_zh_male_lengaozongcai_tob": "冷傲总裁",
    "ICL_zh_male_yuanqishaonian_tob": "元气少年",
    "ICL_zh_male_satuoqingnian_tob": "洒脱青年",
    "ICL_zh_male_zhishuaiqingnian_tob": "直率青年",
    "ICL_zh_male_siwenqingnian_tob": "斯文青年",
    "ICL_zh_male_junyigongzi_tob": "俊逸公子",
    "ICL_zh_male_zhangjianxiake_tob": "仗剑侠客",
    "ICL_zh_male_jijiaozhineng_tob": "机甲智能",
    "zh_male_naiqimengwa_mars_bigtts": "奶气萌娃",
    "zh_female_popo_mars_bigtts": "婆婆",
    "zh_female_gaolengyujie_moon_bigtts": "高冷御姐",
    "zh_male_aojiaobazong_moon_bigtts": "傲娇霸总",
    "zh_female_meilinvyou_moon_bigtts": "魅力女友",
    "zh_male_shenyeboke_moon_bigtts": "深夜播客",
    "zh_female_sajiaonvyou_moon_bigtts": "柔美女友",
    "zh_female_yuanqinvyou_moon_bigtts": "撒娇学妹",
    "ICL_zh_female_bingruoshaonv_tob": "病弱少女",
    "ICL_zh_female_huoponvhai_tob": "活泼女孩",
    "zh_male_dongfanghaoran_moon_bigtts": "东方浩然",
    "ICL_zh_male_lvchaxiaoge_tob": "绿茶小哥",
    "ICL_zh_female_jiaoruoluoli_tob": "娇弱萝莉",
    "ICL_zh_male_lengdanshuli_tob": "冷淡疏离",
    "ICL_zh_male_hanhoudunshi_tob": "憨厚敦实",
    "ICL_zh_female_huopodiaoman_tob": "活泼刁蛮",
    "ICL_zh_male_guzhibingjiao_tob": "固执病娇",
    "ICL_zh_male_sajiaonianren_tob": "撒娇粘人",
    "ICL_zh_female_aomanjiaosheng_tob": "傲慢娇声",
    "ICL_zh_male_xiaosasuixing_tob": "潇洒随性",
    "ICL_zh_male_guiyishenmi_tob": "诡异神秘",
    "ICL_zh_male_ruyacaijun_tob": "儒雅才俊",
    "ICL_zh_male_zhengzhiqingnian_tob": "正直青年",
    "ICL_zh_female_jiaohannvwang_tob": "娇憨女王",
    "ICL_zh_female_bingjiaomengmei_tob": "病娇萌妹",
    "ICL_zh_male_qingsenaigou_tob": "青涩小生",
    "ICL_zh_male_chunzhenxuedi_tob": "纯真学弟",
    "ICL_zh_male_youroubangzhu_tob": "优柔帮主",
    "ICL_zh_male_yourougongzi_tob": "优柔公子",
    "ICL_zh_female_tiaopigongzhu_tob": "调皮公主",
    "ICL_zh_male_tiexinnanyou_tob": "贴心男友",
    "ICL_zh_male_shaonianjiangjun_tob": "少年将军",
    "ICL_zh_male_bingjiaogege_tob": "病娇哥哥",
    "ICL_zh_male_xuebanantongzhuo_tob": "学霸男同桌",
    "ICL_zh_male_youmoshushu_tob": "幽默叔叔",
    "ICL_zh_female_jiaxiaozi_tob": "假小子",
    "ICL_zh_male_wenrounantongzhuo_tob": "温柔男同桌",
    "ICL_zh_male_youmodaye_tob": "幽默大爷",
    "ICL_zh_male_asmryexiu_tob": "枕边低语",
    "ICL_zh_male_shenmifashi_tob": "神秘法师",
    "zh_female_jiaochuan_mars_bigtts": "娇喘女声",
    "zh_male_livelybro_mars_bigtts": "开朗弟弟",
    "zh_female_flattery_mars_bigtts": "谄媚女声",
    "ICL_zh_male_lengjunshangsi_tob": "冷峻上司",
    "ICL_zh_male_xiaoge_v1_tob": "寡言小哥",
    "ICL_zh_male_renyuwangzi_v1_tob": "清朗温润",
    "ICL_zh_male_xiaosha_v1_tob": "潇洒随性",
    "ICL_zh_male_liyisheng_v1_tob": "清冷矜贵",
    "ICL_zh_male_qinglen_v1_tob": "沉稳优雅",
    "ICL_zh_male_chongqingzhanzhan_v1_tob": "清逸苏感",
    "ICL_zh_male_xingjiwangzi_v1_tob": "温柔内敛",
    "ICL_zh_male_sigeshiye_v1_tob": "低沉缱绻",
    "ICL_zh_male_lanyingcaohunshi_v1_tob": "蓝银草魂师",
    "ICL_zh_female_liumengdie_v1_tob": "清冷高雅",
    "ICL_zh_female_linxueying_v1_tob": "甜美娇俏",
    "ICL_zh_female_rouguhunshi_v1_tob": "柔骨魂师",
    "ICL_zh_female_tianmei_v1_tob": "甜美活泼",
    "ICL_zh_female_chengshu_v1_tob": "成熟温柔",
    "ICL_zh_female_xnx_v1_tob": "贴心闺蜜",
    "ICL_zh_female_yry_v1_tob": "温柔白月光",
    "zh_male_bv139_audiobook_ummv3_bigtts": "高冷沉稳",
    "ICL_zh_male_cujingnanyou_tob": "醋精男友",
    "ICL_zh_male_fengfashaonian_tob": "风发少年",
    "ICL_zh_male_cixingnansang_tob": "磁性男嗓",
    "ICL_zh_male_chengshuzongcai_tob": "成熟总裁",
    "ICL_zh_male_aojiaojingying_tob": "傲娇精英",
    "ICL_zh_male_aojiaogongzi_tob": "傲娇公子",
    "ICL_zh_male_badaoshaoye_tob": "霸道少爷",
    "ICL_zh_male_fuheigongzi_tob": "腹黑公子",
    "ICL_zh_female_nuanxinxuejie_tob": "暖心学姐",
    "ICL_zh_female_keainvsheng_tob": "可爱女生",
    "ICL_zh_female_chengshujiejie_tob": "成熟姐姐",
    "ICL_zh_female_bingjiaojiejie_tob": "病娇姐姐",
    "ICL_zh_female_wumeiyujie_tob": "妩媚御姐",
    "ICL_zh_female_aojiaonvyou_tob": "傲娇女友",
    "ICL_zh_female_tiexinnvyou_tob": "贴心女友",
    "ICL_zh_female_xingganyujie_tob": "性感御姐",
    "ICL_zh_male_bingjiaodidi_tob": "病娇弟弟",
    "ICL_zh_male_aomanshaoye_tob": "傲慢少爷",
    "ICL_zh_male_aiqilingren_tob": "傲气凌人",
    "ICL_zh_male_bingjiaobailian_tob": "病娇白莲",
    
    # 多语种
    "en_female_lauren_moon_bigtts": "Lauren",
    "en_male_campaign_jamal_moon_bigtts": "Energetic Male II",
    "en_male_chris_moon_bigtts": "Gotham Hero",
    "en_female_product_darcie_moon_bigtts": "Flirty Female",
    "en_female_emotional_moon_bigtts": "Peaceful Female",
    "en_female_nara_moon_bigtts": "Nara",
    "en_male_bruce_moon_bigtts": "Bruce",
    "en_male_michael_moon_bigtts": "Michael",
    "ICL_en_male_cc_sha_v1_tob": "Cartoon Chef",
    "zh_male_M100_conversation_wvae_bigtts": "Lucas",
    "zh_female_sophie_conversation_wvae_bigtts": "Sophie",
    "en_female_dacey_conversation_wvae_bigtts": "Daisy",
    "en_male_charlie_conversation_wvae_bigtts": "Owen",
    "en_female_sarah_new_conversation_wvae_bigtts": "Luna",
    "ICL_en_male_michael_tob": "Michael",
    "ICL_en_female_cc_cm_v1_tob": "Charlie",
    "ICL_en_male_oogie2_tob": "Big Boogie",
    "ICL_en_male_frosty1_tob": "Frosty Man",
    "ICL_en_male_grinch2_tob": "The Grinch",
    "ICL_en_male_zayne_tob": "Zayne",
    "ICL_en_male_cc_jigsaw_tob": "Jigsaw",
    "ICL_en_male_cc_chucky_tob": "Chucky",
    "ICL_en_male_cc_penny_v1_tob": "Clown Man",
    "ICL_en_male_kevin2_tob": "Kevin McCallister",
    "ICL_en_male_xavier1_v1_tob": "Xavier",
    "ICL_en_male_cc_dracula_v1_tob": "Noah",
    "en_male_adam_mars_bigtts": "Adam",
    "en_female_amanda_mars_bigtts": "Amanda",
    "en_male_jackson_mars_bigtts": "Jackson",
    "en_female_daisy_moon_bigtts": "Delicate Girl",
    "en_male_dave_moon_bigtts": "Dave",
    "en_male_hades_moon_bigtts": "Hades",
    "en_female_onez_moon_bigtts": "Onez",
    "en_female_emily_mars_bigtts": "Emily",
    "zh_male_xudong_conversation_wvae_bigtts": "Daniel",
    "ICL_en_male_cc_alastor_tob": "Alastor",
    "en_male_smith_mars_bigtts": "Smith",
    "en_female_anna_mars_bigtts": "Anna",
    "ICL_en_male_aussie_v1_tob": "Ethan",
    "en_female_sarah_mars_bigtts": "Sarah",
    "en_male_dryw_mars_bigtts": "Dryw",
    "multi_female_maomao_conversation_wvae_bigtts": "Diana",
    "multi_male_M100_conversation_wvae_bigtts": "Lucía",
    "multi_female_sophie_conversation_wvae_bigtts": "Sofía",
    "multi_male_xudong_conversation_wvae_bigtts": "Daníel",
    "multi_zh_male_youyoujunzi_moon_bigtts": "ひかる（光）",
    "multi_female_sophie_conversation_wvae_bigtts": "さとみ（智美）",
    "multi_male_xudong_conversation_wvae_bigtts": "まさお（正男）",
    "multi_female_maomao_conversation_wvae_bigtts": "つき（月）",
    "multi_female_gaolengyujie_moon_bigtts": "あけみ（朱美）",
    "multi_male_jingqiangkanye_moon_bigtts": "かずね（和音）",
    "multi_female_shuangkuaisisi_moon_bigtts": "はるこ（晴子）",
    "multi_male_wanqudashu_moon_bigtts": "ひろし（広志）",
    
    # 客服场景
    "ICL_zh_female_lixingyuanzi_cs_tob": "理性圆子",
    "ICL_zh_female_qingtiantaotao_cs_tob": "清甜桃桃",
    "ICL_zh_female_qingxixiaoxue_cs_tob": "清晰小雪",
    "ICL_zh_female_qingtianmeimei_cs_tob": "清甜莓莓",
    "ICL_zh_female_kailangtingting_cs_tob": "开朗婷婷",
    "ICL_zh_male_qingxinmumu_cs_tob": "清新沐沐",
    "ICL_zh_male_shuanglangxiaoyang_cs_tob": "爽朗小阳",
    "ICL_zh_male_qingxinbobo_cs_tob": "清新波波",
    "ICL_zh_female_wenwanshanshan_cs_tob": "温婉珊珊",
    "ICL_zh_female_tianmeixiaoyu_cs_tob": "甜美小雨",
    "ICL_zh_female_reqingaina_cs_tob": "热情艾娜",
    "ICL_zh_female_tianmeixiaoju_cs_tob": "甜美小橘",
    "ICL_zh_male_chenwenmingzai_cs_tob": "沉稳明仔",
    "ICL_zh_male_qinqiexiaozhuo_cs_tob": "亲切小卓",
    "ICL_zh_female_lingdongxinxin_cs_tob": "灵动欣欣",
    "ICL_zh_female_guaiqiaokeer_cs_tob": "乖巧可儿",
    "ICL_zh_female_nuanxinqianqian_cs_tob": "暖心茜茜",
    "ICL_zh_female_ruanmengtuanzi_cs_tob": "软萌团子",
    "ICL_zh_male_yangguangyangyang_cs_tob": "阳光洋洋",
    "ICL_zh_female_ruanmengtangtang_cs_tob": "软萌糖糖",
    "ICL_zh_female_xiuliqianqian_cs_tob": "秀丽倩倩",
    "ICL_zh_female_kaixinxiaohong_cs_tob": "开心小鸿",
    "ICL_zh_female_qingyingduoduo_cs_tob": "轻盈朵朵",
    "zh_female_kefunvsheng_mars_bigtts": "暖阳女声",
    
    # 视频配音
    "zh_male_M100_conversation_wvae_bigtts": "悠悠君子",
    "zh_female_maomao_conversation_wvae_bigtts": "文静毛毛",
    "ICL_zh_female_qiuling_v1_tob": "倾心少女",
    "ICL_zh_male_buyan_v1_tob": "醇厚低音",
    "ICL_zh_male_BV144_paoxiaoge_v1_tob": "咆哮小哥",
    "ICL_zh_female_heainainai_tob": "和蔼奶奶",
    "ICL_zh_female_linjuayi_tob": "邻居阿姨",
    "zh_female_wenrouxiaoya_moon_bigtts": "温柔小雅",
    "zh_male_tiancaitongsheng_mars_bigtts": "天才童声",
    "zh_male_sunwukong_mars_bigtts": "猴哥",
    "zh_male_xionger_mars_bigtts": "熊二",
    "zh_female_peiqi_mars_bigtts": "佩奇猪",
    "zh_female_wuzetian_mars_bigtts": "武则天",
    "zh_female_gujie_mars_bigtts": "顾姐",
    "zh_female_yingtaowanzi_mars_bigtts": "樱桃丸子",
    "zh_male_chunhui_mars_bigtts": "广告解说",
    "zh_female_shaoergushi_mars_bigtts": "少儿故事",
    "zh_male_silang_mars_bigtts": "四郎",
    "zh_female_qiaopinvsheng_mars_bigtts": "俏皮女声",
    "zh_male_lanxiaoyang_mars_bigtts": "懒音绵宝",
    "zh_male_dongmanhaimian_mars_bigtts": "亮嗓萌仔",
    "zh_male_jieshuonansheng_mars_bigtts": "磁性解说男声/Morgan",
    "zh_female_jitangmeimei_mars_bigtts": "鸡汤妹妹/Hope",
    "zh_female_tiexinnvsheng_mars_bigtts": "贴心女声/Candy",
    "zh_female_mengyatou_mars_bigtts": "萌丫头/Cutey",
    
    # 有声阅读
    "ICL_zh_male_neiliancaijun_e991be511569_tob": "内敛才俊",
    "ICL_zh_male_yangyang_v1_tob": "温暖少年",
    "ICL_zh_male_flc_v1_tob": "儒雅公子",
    "zh_male_changtianyi_mars_bigtts": "悬疑解说",
    "zh_male_ruyaqingnian_mars_bigtts": "儒雅青年",
    "zh_male_baqiqingshu_mars_bigtts": "霸气青叔",
    "zh_male_qingcang_mars_bigtts": "擎苍",
    "zh_male_yangguangqingnian_mars_bigtts": "活力小哥",
    "zh_female_gufengshaoyu_mars_bigtts": "古风少御",
    "zh_female_wenroushunv_mars_bigtts": "温柔淑女",
    "zh_male_fanjuanqingnian_mars_bigtts": "反卷青年",
}

# 音色分类
VOICE_CATEGORIES = {
    "通用场景-多情感": [
        "zh_male_lengkugege_emo_v2_mars_bigtts",
        "zh_female_tianxinxiaomei_emo_v2_mars_bigtts",
        "zh_female_gaolengyujie_emo_v2_mars_bigtts",
        "zh_male_aojiaobazong_emo_v2_mars_bigtts",
        "zh_male_guangzhoudege_emo_mars_bigtts",
        "zh_male_jingqiangkanye_emo_mars_bigtts",
        "zh_female_linjuayi_emo_v2_mars_bigtts",
        "zh_male_yourougongzi_emo_v2_mars_bigtts",
        "zh_male_ruyayichen_emo_v2_mars_bigtts",
        "zh_male_junlangnanyou_emo_v2_mars_bigtts",
        "zh_male_beijingxiaoye_emo_v2_mars_bigtts",
        "zh_female_roumeinvyou_emo_v2_mars_bigtts",
        "zh_male_yangguangqingnian_emo_v2_mars_bigtts",
        "zh_female_meilinvyou_emo_v2_mars_bigtts",
        "zh_female_shuangkuaisisi_emo_v2_mars_bigtts",
        "en_female_candice_emo_v2_mars_bigtts",
        "en_female_skye_emo_v2_mars_bigtts",
        "en_male_glen_emo_v2_mars_bigtts",
        "en_male_sylus_emo_v2_mars_bigtts",
        "en_male_corey_emo_v2_mars_bigtts",
        "en_female_nadia_tips_emo_v2_mars_bigtts",
        "zh_male_shenyeboke_emo_v2_mars_bigtts",
    ],
    "通用场景-普通": [
        "zh_female_cancan_mars_bigtts",
        "zh_female_qinqienvsheng_moon_bigtts",
        "zh_male_xudong_conversation_wvae_bigtts",
        "zh_female_shuangkuaisisi_moon_bigtts",
        "zh_male_wennuanahu_moon_bigtts",
        "zh_male_yangguangqingnian_moon_bigtts",
        "zh_female_linjianvhai_moon_bigtts",
        "zh_male_yuanboxiaoshu_moon_bigtts",
        "zh_female_gaolengyujie_moon_bigtts",
        "zh_male_aojiaobazong_moon_bigtts",
        "zh_female_meilinvyou_moon_bigtts",
        "zh_male_shenyeboke_moon_bigtts",
        "zh_male_dongfanghaoran_moon_bigtts",
    ],
    "角色扮演": [
        "ICL_zh_female_chunzhenshaonv_e588402fb8ad_tob",
        "ICL_zh_male_xiaonaigou_edf58cf28b8b_tob",
        "ICL_zh_female_jinglingxiangdao_1beb294a9e3e_tob",
        "ICL_zh_male_menyoupingxiaoge_ffed9fc2fee7_tob",
        "ICL_zh_male_anrenqinzhu_cd62e63dcdab_tob",
        "ICL_zh_male_badaozongcai_v1_tob",
        "ICL_zh_male_bingruogongzi_tob",
        "ICL_zh_female_bingjiao3_tob",
        "ICL_zh_male_shuanglangshaonian_tob",
        "ICL_zh_male_sajiaonanyou_tob",
        "ICL_zh_male_wenrounanyou_tob",
        "ICL_zh_male_tiancaitongzhuo_tob",
        "ICL_zh_male_bingjiaoshaonian_tob",
        "ICL_zh_male_bingjiaonanyou_tob",
        "ICL_zh_male_bingruoshaonian_tob",
        "ICL_zh_male_bingjiaogege_tob",
        "ICL_zh_female_bingjiaojiejie_tob",
        "ICL_zh_male_bingjiaodidi_tob",
        "ICL_zh_female_bingruoshaonv_tob",
        "ICL_zh_female_bingjiaomengmei_tob",
        "ICL_zh_male_bingjiaobailian_tob",
    ],
    "视频配音": [
        "zh_male_M100_conversation_wvae_bigtts",
        "zh_female_maomao_conversation_wvae_bigtts",
        "zh_male_tiancaitongsheng_mars_bigtts",
        "zh_male_sunwukong_mars_bigtts",
        "zh_male_xionger_mars_bigtts",
        "zh_female_peiqi_mars_bigtts",
        "zh_female_wuzetian_mars_bigtts",
        "zh_female_yingtaowanzi_mars_bigtts",
        "zh_male_silang_mars_bigtts",
        "zh_male_jieshuonansheng_mars_bigtts",
    ],
    "有声阅读": [
        "zh_male_changtianyi_mars_bigtts",
        "zh_male_ruyaqingnian_mars_bigtts",
        "zh_male_baqiqingshu_mars_bigtts",
        "zh_male_qingcang_mars_bigtts",
        "zh_female_gufengshaoyu_mars_bigtts",
        "zh_female_wenroushunv_mars_bigtts",
    ],
    "多语种": [
        "en_female_lauren_moon_bigtts",
        "en_male_michael_moon_bigtts",
        "en_male_bruce_moon_bigtts",
        "en_female_emily_mars_bigtts",
        "en_male_smith_mars_bigtts",
        "en_female_anna_mars_bigtts",
    ],
}

# 推荐音色（用于交互式选择）
RECOMMENDED_VOICES = {
    "通用场景-多情感": [
        ("zh_female_gaolengyujie_emo_v2_mars_bigtts", "高冷御姐（多情感）"),
        ("zh_male_aojiaobazong_emo_v2_mars_bigtts", "傲娇霸总（多情感）"),
        ("zh_male_ruyayichen_emo_v2_mars_bigtts", "儒雅男友（多情感）"),
    ],
    "通用场景-普通": [
        ("zh_female_cancan_mars_bigtts", "灿灿/Shiny [DEFAULT]"),
        ("zh_male_xudong_conversation_wvae_bigtts", "快乐小东"),
        ("zh_female_qinqienvsheng_moon_bigtts", "亲切女声"),
    ],
    "角色扮演": [
        ("ICL_zh_female_chunzhenshaonv_e588402fb8ad_tob", "纯真少女"),
        ("ICL_zh_male_badaozongcai_v1_tob", "霸道总裁"),
        ("ICL_zh_male_sajiaonanyou_tob", "撒娇男友"),
    ],
    "视频配音": [
        ("zh_male_sunwukong_mars_bigtts", "猴哥"),
        ("zh_male_xionger_mars_bigtts", "熊二"),
        ("zh_female_peiqi_mars_bigtts", "佩奇猪"),
    ],
    "有声阅读": [
        ("zh_male_qingcang_mars_bigtts", "擎苍"),
        ("zh_male_ruyaqingnian_mars_bigtts", "儒雅青年"),
        ("zh_female_wenroushunv_mars_bigtts", "温柔淑女"),
    ],
    "多语种": [
        ("en_female_lauren_moon_bigtts", "Lauren (美式英语)"),
        ("en_male_michael_moon_bigtts", "Michael (美式英语)"),
        ("en_female_emily_mars_bigtts", "Emily (英式英语)"),
    ],
}

# 音色分类英文映射（用于交互显示）
CATEGORY_DISPLAY_NAMES = {
    "通用场景-多情感": "General - Multilingual (with emotions)",
    "通用场景-普通": "General - Normal",
    "角色扮演": "Roleplay",
    "视频配音": "Video Dubbing",
    "有声阅读": "Audiobook",
    "多语种": "Multilingual",
}


def check_api_config():
    """
    检查API配置是否完整
    
    Returns:
        dict or None: 如果配置完整返回配置字典，否则返回None
    """
    app_id = os.environ.get('VOLCANO_TTS_APPID')
    access_token = os.environ.get('VOLCANO_TTS_ACCESS_TOKEN')
    secret_key = os.environ.get('VOLCANO_TTS_SECRET_KEY')
    
    # 如果环境变量没有，尝试从.env文件读取
    if not all([app_id, access_token, secret_key]):
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path, override=True)
            app_id = os.environ.get('VOLCANO_TTS_APPID')
            access_token = os.environ.get('VOLCANO_TTS_ACCESS_TOKEN')
            secret_key = os.environ.get('VOLCANO_TTS_SECRET_KEY')
    
    if all([app_id, access_token, secret_key]):
        return {
            'app_id': app_id,
            'access_token': access_token,
            'secret_key': secret_key,
            'voice_type': os.environ.get('VOLCANO_TTS_VOICE_TYPE', DEFAULT_VOICE_TYPE)
        }
    
    return None


def setup_api_config(app_id, access_token, secret_key, voice_type=None):
    """
    设置API配置并保存到.env文件
    
    Args:
        app_id: 应用ID
        access_token: 访问令牌
        secret_key: 密钥
        voice_type: 默认音色（可选）
        
    Returns:
        str: .env文件路径
    """
    # 获取.env文件路径
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    
    # 读取现有内容（如果存在）
    existing_content = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    existing_content[key] = value
    
    # 更新配置
    existing_content['VOLCANO_TTS_APPID'] = app_id
    existing_content['VOLCANO_TTS_ACCESS_TOKEN'] = access_token
    existing_content['VOLCANO_TTS_SECRET_KEY'] = secret_key
    if voice_type:
        existing_content['VOLCANO_TTS_VOICE_TYPE'] = voice_type
    
    # 写入文件
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write("# 火山引擎语音合成配置\n")
        f.write(f"VOLCANO_TTS_APPID={existing_content['VOLCANO_TTS_APPID']}\n")
        f.write(f"VOLCANO_TTS_ACCESS_TOKEN={existing_content['VOLCANO_TTS_ACCESS_TOKEN']}\n")
        f.write(f"VOLCANO_TTS_SECRET_KEY={existing_content['VOLCANO_TTS_SECRET_KEY']}\n")
        if voice_type or 'VOLCANO_TTS_VOICE_TYPE' in existing_content:
            f.write(f"VOLCANO_TTS_VOICE_TYPE={existing_content.get('VOLCANO_TTS_VOICE_TYPE', voice_type)}\n")
    
    # 重新加载环境变量
    load_dotenv(env_path, override=True)
    
    return env_path


def get_api_config_prompt():
    """
    获取API配置提示文本
    
    Returns:
        str: 格式化的配置提示
    """
    prompt_lines = [
        "🔐 API Configuration Required",
        "",
        "To use the Doubao TTS service, you need to provide API credentials.",
        "",
        "You can obtain these credentials from:",
        "  https://console.volcengine.com/",
        "",
        "Required information:",
        "  1. App ID (APPID)",
        "  2. Access Token",
        "  3. Secret Key",
        "",
        "Steps to get credentials:",
        "  1. Visit the Volcano Engine Console",
        "  2. Sign up or log in to your account",
        "  3. Navigate to 'Doubao Voice' service",
        "  4. Create a new application",
        "  5. Copy the App ID, Access Token, and Secret Key",
        "",
        "Please enter your credentials when ready.",
    ]
    
    return "\n".join(prompt_lines)


def get_voice_selection_prompt():
    """
    获取交互式音色选择提示文本
    
    Returns:
        str: 格式化的音色选择提示
    """
    prompt_lines = [
        "🎙️ Please select a voice for text-to-speech synthesis:",
        "",
        "Here are our recommended voices by category:",
        "",
    ]
    
    for category, voices in RECOMMENDED_VOICES.items():
        display_name = CATEGORY_DISPLAY_NAMES.get(category, category)
        prompt_lines.append(f"[{display_name}]")
        
        for voice_id, voice_name in voices:
            lang = "Chinese"
            if "en_" in voice_id:
                lang = "English"
            elif "multi_" in voice_id:
                lang = "Multilingual"
            prompt_lines.append(f"  • {voice_name} ({lang}) -> voice_type: {voice_id}")
        
        prompt_lines.append("")
    
    prompt_lines.extend([
        "💡 Tips:",
        "  • You can say the voice name (e.g., 'Shiny', '猴哥', '霸道总裁')",
        "  • Or provide the voice_type directly (e.g., 'zh_female_cancan_mars_bigtts')",
        "  • Type 'list all' to see all 200+ available voices",
        "  • Press Enter to use the default voice (Shiny)",
        "",
        "Which voice would you like to use?",
    ])
    
    return "\n".join(prompt_lines)


def find_voice_by_name(name):
    """
    根据音色名称查找voice_type
    
    Args:
        name: 用户输入的音色名称或voice_type
        
    Returns:
        tuple: (voice_type, voice_display_name) 或 (None, None) 如果未找到
    """
    name = name.strip().lower()
    
    # 直接匹配voice_type
    if name in VOICE_TYPES:
        return name, VOICE_TYPES[name]
    
    # 模糊匹配音色名称
    for voice_id, display_name in VOICE_TYPES.items():
        # 完全匹配
        if name == display_name.lower():
            return voice_id, display_name
        
        # 部分匹配（中文或英文名称）
        if name in display_name.lower():
            return voice_id, display_name
        
        # 匹配英文别名（如 Shiny, Skye 等）
        if "/" in display_name:
            aliases = display_name.split("/")
            for alias in aliases:
                if name == alias.strip().lower():
                    return voice_id, display_name
    
    return None, None


def get_voice_info(voice_type):
    """
    获取音色详细信息
    
    Args:
        voice_type: voice_type ID
        
    Returns:
        dict: 音色信息
    """
    if voice_type not in VOICE_TYPES:
        return None
    
    # 查找所属分类
    category = None
    for cat, voices in VOICE_CATEGORIES.items():
        if voice_type in voices:
            category = cat
            break
    
    return {
        "voice_type": voice_type,
        "name": VOICE_TYPES[voice_type],
        "category": category,
        "category_display": CATEGORY_DISPLAY_NAMES.get(category, category) if category else "Unknown",
    }


class VolcanoTTS:
    def __init__(self, app_id=None, access_token=None, secret_key=None, voice_type=None):
        """
        初始化火山引擎TTS客户端
        
        Args:
            app_id: 应用ID
            access_token: 访问令牌 (AK)
            secret_key: 密钥 (SK)
            voice_type: 音色类型，默认使用DEFAULT_VOICE_TYPE
        """
        self.app_id = app_id or os.environ.get('VOLCANO_TTS_APPID')
        self.access_token = access_token or os.environ.get('VOLCANO_TTS_ACCESS_TOKEN')
        self.secret_key = secret_key or os.environ.get('VOLCANO_TTS_SECRET_KEY')
        self.voice_type = voice_type or os.environ.get('VOLCANO_TTS_VOICE_TYPE') or DEFAULT_VOICE_TYPE
        
        if not all([self.app_id, self.access_token, self.secret_key]):
            raise ValueError("缺少必要的API配置，请设置环境变量或直接传入参数")
    
    def list_voices(self, category=None):
        """
        列出可用的音色
        
        Args:
            category: 音色分类，如果为None则列出所有
            
        Returns:
            音色列表
        """
        if category and category in VOICE_CATEGORIES:
            voices = VOICE_CATEGORIES[category]
            return {v: VOICE_TYPES[v] for v in voices}
        return VOICE_TYPES
    
    def set_voice(self, voice_type):
        """
        设置音色
        
        Args:
            voice_type: 音色类型
        """
        if voice_type not in VOICE_TYPES:
            raise ValueError(f"不支持的音色: {voice_type}")
        self.voice_type = voice_type
        return self.voice_type
    
    def synthesize(self, text, voice_type=None, encoding="mp3", 
                   sample_rate=24000, speed=1.0, volume=1.0,
                   output_file=None, cluster="volcano_tts"):
        """
        合成语音
        
        Args:
            text: 要合成的文本
            voice_type: 音色类型，默认使用实例设置的音色
            encoding: 音频格式 (mp3, pcm, wav)
            sample_rate: 采样率 (8000, 16000, 24000)
            speed: 语速 (0.5-2.0)
            volume: 音量 (0.5-2.0)
            output_file: 输出文件路径
            cluster: 集群名称
            
        Returns:
            音频文件路径
        """
        # 使用传入的音色或实例默认音色
        voice = voice_type or self.voice_type
        
        # 构建请求头 - 使用Bearer Token认证 (V3格式)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer;{self.access_token}'
        }
        
        # 构建请求体 - V3 API格式
        body = {
            "app": {
                "appid": self.app_id,
                "token": "access_token",
                "cluster": cluster
            },
            "user": {
                "uid": "user_001"
            },
            "audio": {
                "voice_type": voice,
                "encoding": encoding,
                "speed_ratio": speed,
                "volume_ratio": volume,
                "sample_rate": sample_rate
            },
            "request": {
                "reqid": str(uuid.uuid4()),
                "text": text,
                "text_type": "plain",
                "operation": "query"
            }
        }
        
        # 调试输出
        debug_mode = os.environ.get('TTS_DEBUG', '0') == '1'
        if debug_mode:
            print(f"\n[DEBUG] 请求URL: {TTS_ENDPOINT}")
            print(f"[DEBUG] 请求Headers: {headers}")
            print(f"[DEBUG] 请求Body: {json.dumps(body, ensure_ascii=False, indent=2)}")
        
        # 发送请求
        try:
            response = requests.post(
                TTS_ENDPOINT,
                headers=headers,
                json=body,
                timeout=30
            )
            
            if debug_mode:
                print(f"\n[DEBUG] 响应状态: {response.status_code}")
                print(f"[DEBUG] 响应内容: {response.text}")
            
            result = response.json()
            
            # V3 API响应格式处理
            if "header" in result:
                # 新的V3格式
                header = result.get("header", {})
                code = header.get("code")
                message = header.get("message", "未知错误")
            else:
                # 旧格式兼容
                code = result.get("code")
                message = result.get("message", "未知错误")
            
            # 检查响应状态
            if code != 3000:
                raise Exception(f"TTS请求失败 (code={code}): {message}")
            
            # 解码音频数据 (V3 API格式)
            audio_data = base64.b64decode(result["data"])
            
            # 保存文件
            if output_file is None:
                timestamp = int(time.time())
                output_file = f"tts_output_{timestamp}.{encoding}"
            
            output_path = Path(output_file)
            output_path.write_bytes(audio_data)
            
            return str(output_path.absolute())
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {e}")
        except (KeyError, json.JSONDecodeError) as e:
            raise Exception(f"响应解析失败: {e}")
        except Exception as e:
            if "TTS请求失败" in str(e):
                raise
            raise Exception(f"TTS合成失败: {e}")


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='火山引擎语音合成工具')
    parser.add_argument('text', nargs='?', help='要合成的文本')
    parser.add_argument('-f', '--file', help='从文件读取文本')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('-v', '--voice', default=DEFAULT_VOICE_TYPE, help=f'音色类型 (默认: {DEFAULT_VOICE_TYPE})')
    parser.add_argument('--list-voices', action='store_true', help='列出所有可用音色')
    parser.add_argument('-e', '--encoding', default='mp3', choices=['mp3', 'pcm', 'wav'], help='音频格式')
    parser.add_argument('-r', '--rate', type=int, default=24000, help='采样率')
    parser.add_argument('--speed', type=float, default=1.0, help='语速 (0.5-2.0)')
    parser.add_argument('--volume', type=float, default=1.0, help='音量 (0.5-2.0)')
    parser.add_argument('--cluster', default='volcano_tts', help='集群名称')
    parser.add_argument('--appid', help='应用ID')
    parser.add_argument('--token', help='访问令牌')
    parser.add_argument('--secret', help='密钥')
    parser.add_argument('--debug', action='store_true', help='开启调试模式')
    parser.add_argument('--category', help='按分类筛选音色 (通用场景-多情感/通用场景-普通/角色扮演/视频配音/有声阅读/多语种)')
    
    args = parser.parse_args()
    
    # 列出音色
    if args.list_voices:
        print("\n=== 可用音色列表 ===\n")
        if args.category:
            if args.category in VOICE_CATEGORIES:
                print(f"【{args.category}】")
                for voice_id in VOICE_CATEGORIES[args.category]:
                    print(f"  {voice_id}: {VOICE_TYPES[voice_id]}")
            else:
                print(f"错误: 未知的分类 '{args.category}'")
                print(f"可用分类: {', '.join(VOICE_CATEGORIES.keys())}")
        else:
            for category, voices in VOICE_CATEGORIES.items():
                print(f"【{category}】")
                for voice_id in voices[:5]:  # 每类只显示前5个
                    print(f"  {voice_id}: {VOICE_TYPES[voice_id]}")
                if len(voices) > 5:
                    print(f"  ... 还有 {len(voices) - 5} 个音色")
                print()
            print(f"\n总计: {len(VOICE_TYPES)} 个音色")
            print(f"\n使用 --category <分类名> 查看特定分类的所有音色")
        return
    
    # 获取文本
    if args.file:
        text = Path(args.file).read_text(encoding='utf-8')
    elif args.text:
        text = args.text
    else:
        print("错误: 请提供文本或使用 -f 指定文件")
        sys.exit(1)
    
    # 开启调试模式
    if args.debug:
        os.environ['TTS_DEBUG'] = '1'
    
    # 初始化TTS
    try:
        tts = VolcanoTTS(
            app_id=args.appid,
            access_token=args.token,
            secret_key=args.secret,
            voice_type=args.voice
        )
        
        print(f"[INFO] 正在合成: {text[:50]}...")
        
        output_path = tts.synthesize(
            text=text,
            voice_type=args.voice,
            encoding=args.encoding,
            sample_rate=args.rate,
            speed=args.speed,
            volume=args.volume,
            cluster=args.cluster,
            output_file=args.output
        )
        
        print(f"[OK] 合成成功: {output_path}")
        print(f"[VOICE] 使用音色: {VOICE_TYPES.get(args.voice, args.voice)}")
        
    except Exception as e:
        print(f"[ERROR] 错误: {e}")
        print("\n提示: 如果出现 'requested resource not granted' 错误，请检查:")
        print("  1. 是否已在火山引擎控制台开通语音合成服务")
        print("  2. 账户是否有可用额度")
        print("  3. Token是否有TTS调用权限")
        sys.exit(1)


if __name__ == "__main__":
    main()
