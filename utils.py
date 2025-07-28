#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具类文件
包含运动幅度转换、时长选项更新等通用功能
错误处理功能已迁移到 error_codes.py 模块
"""

# 从error_codes模块导入错误处理函数
from error_codes import ViduErrorHandler

def get_error_message(err_code: str) -> str:
    """将错误码转换为中文错误信息（兼容性函数）"""
    return ViduErrorHandler.get_error_message(err_code)


def convert_movement_amplitude(movement_chinese: str) -> str:
    """将中文运动幅度转换为英文值"""
    movement_mapping = {
        "自动": "auto",
        "小幅度": "small",
        "中幅度": "medium", 
        "大幅度": "large"
    }
    return movement_mapping.get(movement_chinese, "auto")


def update_duration_options(model_value: str):
    """根据模型更新时长选项"""
    # 导入ViduClient的配置
    from vidu_client import ViduClient, ViduModel
    
    try:
        model_enum = ViduModel(model_value)
        durations = ViduClient.MODEL_DURATION_LIMITS[model_enum]
        return [str(d) for d in durations]
    except (ValueError, KeyError):
        # 如果模型不存在，返回默认值
        return ["4"]


def get_voice_characters():
    """获取所有音色选项"""
    return [
        # 中文音色 - 男声
        ("男声1 - 大方稳健", "male_1"),
        ("男声2 - 新闻音色", "male_2"),
        ("男声3 - 平静淡定", "male_3"),
        ("男声4 - 轻快大方", "male_4"),
        ("男声5 - 柔和播报", "male_5"),
        ("男声6 - 磁性自然", "male_6"),
        ("男声7 - 低沉慢速", "male_7"),
        ("男声8 - 广播男音", "male_8"),
        ("男声9 - 热情播报", "male_9"),
        ("男声10 - 情感对话", "male_10"),
        ("男声11 - 对话风格", "male_11"),
        ("男声12 - 成熟柔和", "male_12"),
        ("男声13 - 浑厚男声", "male_13"),
        ("男声14 - 爽朗纯净", "male_14"),
        ("男声15 - 大方朗读", "male_15"),
        ("男声16 - 温柔男声", "male_16"),
        ("男声17 - 朗读腔调", "male_17"),
        ("男声18 - 磁性播报", "male_18"),
        ("男声19 - 情感朗读", "male_19"),
        ("男声20 - 高亢播报", "male_20"),
        ("男声21 - 东北男声", "timbre_10034_84"),
        ("男声22 - 天津男声", "timbre_10037_87"),
        ("男声23 - 河南男声", "timbre_10038_88"),
        ("男声24 - 四川男声", "timbre_11001_1929"),
        # 中文音色 - 女声
        ("女声1 - 温柔磁性", "female_1"),
        ("女声2 - 柔和甜美", "female_2"),
        ("女声3 - 慢条斯理", "female_3"),
        ("女声4 - 柔和自然", "female_4"),
        ("女声5 - 自然大方", "female_5"),
        ("女声6 - 大方稳健", "female_6"),
        ("女声7 - 热情亲切", "female_7"),
        ("女声8 - 成熟柔和", "female_8"),
        ("女声9 - 成熟稳重", "female_9"),
        ("女声10 - 活力天真", "female_10"),
        ("女声11 - 阳光可爱", "female_11"),
        ("女声12 - 青春甜美", "female_12"),
        ("女声13 - 新闻女声", "female_13"),
        ("女声14 - 通用客服", "female_14"),
        ("女声15 - 中性客服", "female_15"),
        ("女声16 - 亲切客服", "female_16"),
        ("女声17 - 抱歉客服", "female_17"),
        ("女声18 - 热情客服", "female_18"),
        ("女声19 - 情绪聊天", "female_19"),
        ("女声20 - 中性播报", "female_20"),
        ("女声21 - 营销风格", "female_21"),
        ("女声22 - 对话风格", "female_22"),
        ("女声23 - 台湾女声", "timbre_10035_85"),
        ("女声24 - 四川女声", "timbre_10036_86"),
        ("女声25 - 粤语女声", "timbre_10039_89"),
        ("女声26 - 东北女声", "db_fangyan_nv"),
        # 智系列音色
        ("智瑜 - 知性女声", "tts_female_1"),
        ("智聆 - 通用女声", "tts_female_2"),
        ("智美 - 客服女声", "tts_female_3"),
        ("智莉 - 通用女声", "tts_female_4"),
        ("智言 - 助手女声", "tts_female_5"),
        ("智妍 - 大方女声", "tts_female_6"),
        ("智琪 - 客服女声", "tts_female_7"),
        ("智芸 - 知性女声", "tts_female_8"),
        ("智燕 - 新闻女声", "tts_female_9"),
        ("智丹 - 亲切女声", "tts_female_10"),
        ("智甜 - 儿童女声", "tts_female_11"),
        ("智蓉 - 情感女声", "tts_female_12"),
        ("智彤 - 粤语女声", "tts_female_13"),
        ("智虹 - 新闻女声", "tts_female_14"),
        ("智萱 - 聊天女声", "tts_female_15"),
        ("智薇 - 聊天女声", "tts_female_16"),
        ("智希 - 通用女声", "tts_female_17"),
        ("智梅 - 通用女声", "tts_female_18"),
        ("智洁 - 通用女声", "tts_female_19"),
        ("智芳 - 通用女声", "tts_female_20"),
        ("智蓓 - 客服女声", "tts_female_21"),
        ("智莲 - 甜美女声", "tts_female_22"),
        ("智依 - 通用女声", "tts_female_23"),
        ("智川 - 四川女声", "tts_female_24"),
        ("智付 - 支付播报", "tts_female_26"),
        ("智逍遥 - 旁白男声", "tts_male_1"),
        ("智云 - 通用男声", "tts_male_2"),
        ("智华 - 磁性男声", "tts_male_3"),
        ("智辉 - 新闻男声", "tts_male_4"),
        ("智宁 - 播音男声", "tts_male_5"),
        ("智萌 - 儿童男声", "tts_male_6"),
        ("智靖 - 磁性男声", "tts_male_7"),
        ("智刚 - 新闻男声", "tts_male_8"),
        ("智瑞 - 新闻男声", "tts_male_9"),
        ("智皓 - 聊天男声", "tts_male_10"),
        ("智凯 - 人文配音", "tts_male_11"),
        ("智柯 - 通用男声", "tts_male_12"),
        ("智奎 - 磁性男声", "tts_male_13"),
        ("智味 - 美食解说", "tts_male_15"),
        ("智方 - 磁性沉稳", "tts_male_16"),
        ("智友 - 轻快男声", "tts_male_17"),
        ("智林 - 东北男声", "tts_male_18"),
        # 爱系列音色
        ("爱小霞 - 亲切女声", "tts_female_27"),
        ("爱小玲 - 柔和女声", "tts_female_28"),
        ("爱小芸 - 温柔女声", "tts_female_29"),
        ("爱小秋 - 甜美女声", "tts_female_30"),
        ("爱小芳 - 通用女声", "tts_female_31"),
        ("爱小琴 - 柔和女声", "tts_female_32"),
        ("爱小璐 - 活力女声", "tts_female_33"),
        ("爱小岚 - 柔和女声", "tts_female_34"),
        ("爱小茹 - 亲切女声", "tts_female_35"),
        ("爱小蓉 - 活波女声", "tts_female_36"),
        ("爱小燕 - 活力女声", "tts_female_37"),
        ("爱小莲 - 温婉女声", "tts_female_38"),
        ("爱小雪 - 沉稳女声", "tts_female_39"),
        ("爱小媛 - 自然女声", "tts_female_40"),
        ("爱小娴 - 甜美女声", "tts_female_41"),
        ("爱小溪 - 活力女声", "tts_female_42"),
        ("爱小荷 - 温柔女声", "tts_female_43"),
        ("爱小叶 - 自然女声", "tts_female_44"),
        ("爱小梅 - 自然亲切", "tts_female_45"),
        ("爱小静 - 对话女声", "tts_female_46"),
        ("爱小桃 - 自然大方", "tts_female_47"),
        ("爱小广 - 沉稳男声", "tts_male_19"),
        ("爱小栋 - 磁性男声", "tts_male_20"),
        ("爱小海 - 暖心男声", "tts_male_21"),
        ("爱小章 - 活力男声", "tts_male_22"),
        ("爱小峰 - 稳健男声", "tts_male_23"),
        ("爱小亮 - 活力男声", "tts_male_24"),
        ("爱小博 - 大方男声", "tts_male_25"),
        ("爱小康 - 阳光男声", "tts_male_26"),
        ("爱小辉 - 稳健男声", "tts_male_27"),
        ("爱小阳 - 活力男声", "tts_male_28"),
        ("爱小泉 - 稳重男声", "tts_male_29"),
        ("爱小昆 - 轻快男声", "tts_male_30"),
        ("爱小诚 - 沉稳男声", "tts_male_31"),
        ("爱小武 - 洪亮男声", "tts_male_32"),
        ("爱小涛 - 自然男声", "tts_male_33"),
        ("爱小树 - 对话男声", "tts_male_34"),
        ("爱小杭 - 自然亲切", "tts_male_35"),
        ("爱小柯 - 低沉磁性", "tts_male_36"),
        ("智飞 - 活力男声", "tts_male_37"),
        ("智海 - 成熟男声", "tts_male_38"),
        ("智凡 - 新闻男声", "tts_male_39"),
        # 云系列音色
        ("云小茉 - 自然放松女声", "tts_female_yunxiaomo"),
        ("云小涵 - 温暖甜美女声", "tts_female_yunxiaohan"),
        ("云小秋 - 知性舒适女声", "tts_female_yunxiaoqiu"),
        ("云小柔 - 中文女声", "tts_female_yunxiaorou"),
        ("云小瑞 - 成熟睿智女声", "tts_female_yunxiaorui"),
        ("云小晨 - 休闲放松女声", "tts_female_yunxiaochen"),
        ("云小梦 - 中文女声", "tts_female_yunxiaomeng"),
        ("云小小 - 活泼温暖女声", "tts_female_yunxiaoxiao"),
        ("云小羽 - 台湾普通话繁体", "tts_female_tw_yunxiaoyu"),
        ("云小笑 - 中文女声", "tts_female_yunxiaoxiao1"),
        ("云小霜 - 可爱愉悦童声", "tts_female_yunxiaoshuang"),
        ("云小珍 - 台湾普通话繁体", "tts_female_tw_yunxiaozhen"),
        ("云小彤 - 吴语", "tts_female_wu_yunxiaotong"),
        ("云小嘉 - 粤语繁体女声", "tts_female_yue_yunxiaojia"),
        ("云小曼 - 粤语繁体女声", "tts_female_yue_yunxiaoman"),
        ("云小敏 - 粤语", "tts_female_yue_yunxiaomin"),
        ("云小妮 - 中原官话陕西", "tts_female_shanxi_yunxiaoni"),
        ("云小北 - 东北官话", "tts_female_liaoning_yunxiaobei"),
        ("云小希 - 活泼阳光男声", "tts_male_yunxiaoxi"),
        ("云小浩 - 中文男声", "tts_male_yunxiaohao"),
        ("云小杰 - 中文男声", "tts_male_yunxiaojie"),
        ("云小夏 - 中文男声", "tts_male_yunxiaoxia"),
        ("云小衣 - 中文女声", "tts_female_yunxiaoyi"),
        ("云小峰 - 中文男声", "tts_male_yunxiaofeng"),
        ("云小建 - 中文男声", "tts_male_yunxiaojian"),
        ("云小燕 - 对话场景女声", "tts_female_yunxiaoyan"),
        ("云小优 - 天使般童声", "tts_female_yunxiaoyou"),
        ("云小真 - 中文女声", "tts_female_yunxiaozhen"),
        ("云小哲 - 台湾普通话繁体", "tts_male_tw_yunxiaozhe"),
        ("云小喆 - 吴语", "tts_male_wu_yunxiaozhe"),
        ("云小龙 - 粤语繁体男声", "tts_male_yue_yunxiaolong"),
        ("云小嵩 - 粤语", "tts_male_yue_yunxiaosong"),
        ("云小齐 - 广西口音普通话", "tts_male_guangxi_yunxiaoqi"),
        ("云小登 - 中原官话河南", "tts_male_henan_yunxiaodeng"),
        ("云小喜 - 西南普通话", "tts_male_sichuan_yunxiaoxi"),
        ("云小标 - 东北官话", "tts_male_liaoning_yunxiaobiao"),
        ("云小翔 - 冀鲁官话", "tts_male_shandong_yunxiaoxiang"),
        ("云小业 - 中文男声", "tts_male_yunxiaoye"),
        ("云小泽 - 中文男声", "tts_male_yunxiaoze"),
        ("云小阳 - 专业流利男声", "tts_male_yunxiaoyang"),
        # 特殊音色
        ("稚嫩童声", "dragon"),
        ("可爱童声", "luka_new_timbre"),
        ("叮当", "aid_wy"),
        ("云萝", "aid_loli"),
        ("云羽", "aid_yunyu"),
        ("云叶", "aid_yezi"),
        ("云侠", "aid_qixia"),
        ("云言", "aid_wgvbx"),
        ("云暖", "aid_wgvls"),
        ("云武", "aid_wgvyl"),
        ("云空", "aid_xmini"),
        ("云川", "aid_sichuanhua"),
        ("云璃", "timbre_female_yunli"),
        ("云娜", "timbre_female_yunna"),
        ("云逸", "timbre_female_yunyi"),
        ("云菲", "timbre_female_yunfei"),
        ("云豪", "timbre_male_wgvgp_54"),
        ("云晨", "timbre_female_yunchen"),
        ("云颖", "timbre_female_yunying"),
        ("云瑜", "timbre_female_yunyu_5"),
        ("云腾", "timbre_male_yunteng_4"),
        ("云瑶", "timbre_female_wgvll_55"),
        ("云婉", "timbre_female_cafemale_53"),
        ("云梦", "timbre_female_cantonesefemale_277"),
        ("云粤", "timbre_11000_1909"),
        # 直播音色
        ("小美直播", "zshot_20375"),
        ("小彩直播", "zshot_20383"),
        ("小霞直播", "zshot_20384"),
        ("小瑜直播", "zshot_20387"),
        ("小芬直播", "zshot_20389"),
        ("小萍直播", "zshot_20390"),
        ("小燕直播", "zshot_20392"),
        ("小丽直播", "zshot_20393"),
        ("小红直播", "zshot_20394"),
        ("小娟直播", "zshot_20396"),
        ("小梅直播", "zshot_20397"),
        ("小鹏直播", "zshot_21048"),
        ("小军直播", "zshot_21049"),
        ("小洪直播", "zshot_21050"),
        ("小勇直播", "zshot_21051"),
        ("小龙直播", "zshot_21052"),
        ("小磊直播", "zshot_21054"),
        ("小雷直播", "zshot_21057"),
        ("小刚直播", "zshot_21058"),
        ("小明直播", "zshot_21059"),
        ("小宝直播", "zshot_21060"),
        ("小杰直播", "zshot_21061"),
        ("小虎直播", "zshot_21063"),
    ]


def get_voice_character_choices():
    """获取音色选项列表（用于Gradio Dropdown）"""
    characters = get_voice_characters()
    return [f"{name} ({id})" for name, id in characters]


def get_voice_character_id(display_name: str) -> str:
    """根据显示名称获取音色ID"""
    characters = get_voice_characters()
    for name, char_id in characters:
        if display_name.startswith(name):
            return char_id
    return ""


def get_voice_character_name(char_id: str) -> str:
    """根据音色ID获取显示名称"""
    characters = get_voice_characters()
    for name, id in characters:
        if id == char_id:
            return name
    return char_id 