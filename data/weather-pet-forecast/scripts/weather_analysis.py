#!/usr/bin/env python3
"""
Weather Forecast Analysis Script - Caring Version
Analyzes 3-day weather forecast with warm, thoughtful recommendations
for humans and their beloved pets
"""

import json
import sys
from datetime import datetime

def analyze_weather(data, location_name=None):
    """Analyze weather data with warm, caring recommendations"""
    
    if not data or 'weather' not in data:
        return "抱歉，无法获取天气数据，请稍后再试 ❤️"
    
    # Get location
    location = location_name or data.get('nearest_area', [{}])[0].get('areaName', [{}])[0].get('value', '您所在的城市')
    country = data.get('nearest_area', [{}])[0].get('country', [{}])[0].get('value', '')
    
    # Warm greeting
    output = []
    output.append(f"📍 **{location}, {country}**")
    output.append("")
    output.append("💕 温馨提示：这是为您和毛孩子准备的专属天气报告")
    output.append("")
    output.append("📅 **三天天气贴心分析**")
    output.append("")
    
    # Parse 3-day data
    days_data = []
    for i, day in enumerate(data['weather'][:3]):
        date = day['date']
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][date_obj.weekday()]
        
        max_temp = int(day['maxtempC'])
        min_temp = int(day['mintempC'])
        avg_temp = int(day['avgtempC'])
        
        # Get noon data
        noon_data = day['hourly'][4]
        desc = noon_data['weatherDesc'][0]['value']
        humidity = int(noon_data['humidity'])
        wind_speed = int(noon_data['windspeedKmph'])
        wind_dir = noon_data['winddir16Point']
        uv_index = int(noon_data['uvIndex'])
        rain_chance = int(noon_data['chanceofrain'])
        visibility = int(noon_data['visibility'])
        
        day_name = ['今天', '明天', '后天'][i]
        
        # Day-by-day forecast with warmth
        output.append(f"**【{day_name}】{date} {weekday}**")
        output.append(f"🌡️ 温度: **{min_temp}°C ~ {max_temp}°C** (体感 {avg_temp}°C)")
        output.append(f"☁️ 天气: {desc}")
        output.append(f"🌧️ 降水概率: {rain_chance}%")
        output.append(f"💨 风力: {wind_speed} km/h {wind_dir}")
        output.append(f"☀️ UV指数: {uv_index} | 💧 湿度: {humidity}% | 👁️ 能见度: {visibility} km")
        
        # Add caring note for each day
        if rain_chance > 70:
            output.append("💭 小贴士：这天雨势较大，记得多穿件衣服，别着凉了~")
        elif uv_index > 6:
            output.append("💭 小贴士：紫外线较强，出门记得涂防晒，保护好自己和毛孩子")
        elif max_temp > 30:
            output.append("💭 小贴士：天气炎热，多喝水，注意防暑降温哦")
        elif min_temp < 0:
            output.append("💭 小贴士：天气寒冷，记得多穿点，保暖最重要")
        elif rain_chance == 0 and uv_index < 4:
            output.append("💭 小贴士：天气舒适宜人，是出门散步的好日子~")
        
        output.append("")
        
        days_data.append({
            'name': day_name,
            'date': date,
            'max_temp': max_temp,
            'min_temp': min_temp,
            'avg_temp': avg_temp,
            'desc': desc,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'rain_chance': rain_chance,
            'uv_index': uv_index,
            'visibility': visibility
        })
    
    # Trend Analysis with caring tone
    output.append("---")
    output.append("")
    output.append("📊 **天气趋势温馨提醒**")
    output.append("")
    
    temps = [d['max_temp'] for d in days_data]
    min_temps = [d['min_temp'] for d in days_data]
    rain_chances = [d['rain_chance'] for d in days_data]
    
    # Temperature trend with caring message
    temp_change = temps[2] - temps[0]
    if temp_change > 5:
        temp_trend = f'📈 温度上升明显，从 {temps[0]}°C 升到 {temps[2]}°C'
        temp_care = '天气变暖了，可以适当减少衣物，但早晚温差可能较大，建议备件外套'
    elif temp_change < -5:
        temp_trend = f'📉 温度下降明显，从 {temps[0]}°C 降到 {temps[2]}°C'
        temp_care = '降温了，请务必添衣保暖，预防感冒。毛孩子也要注意保暖哦'
    else:
        temp_trend = f'➡️ 温度稳定，保持在 {min_temps[0]}-{temps[0]}°C 左右'
        temp_care = '天气比较稳定，可以根据体感选择舒适的着装'
    
    output.append(f"• **温度变化**: {temp_trend}")
    output.append(f"• **温馨提示**: {temp_care}")
    output.append("")
    
    # Precipitation with caring tone
    wet_days = sum(1 for r in rain_chances if r > 50)
    max_rain = max(rain_chances)
    rain_day_idx = rain_chances.index(max_rain) if max_rain > 0 else -1
    rain_day_name = days_data[rain_day_idx]['name'] if rain_day_idx >= 0 else ''
    
    if max_rain == 0:
        output.append("• **降水情况**: 未来三天都是好天气 ☀️")
        output.append("• **温馨提醒**: 天气晴好，很适合带毛孩子出去走走~")
    elif wet_days == 0:
        output.append(f"• **降水情况**: 基本无雨，{rain_day_name}降水概率 {max_rain}% 🌤️")
        output.append("• **温馨提醒**: 天气不错，可以安心安排户外活动")
    elif wet_days == 1:
        output.append(f"• **降水情况**: {rain_day_name}可能下雨 ({max_rain}%) 🌧️")
        output.append("• **温馨提醒**: 出门记得带伞，淋雨容易着凉。雨天遛狗记得给毛孩子穿雨衣")
    else:
        output.append(f"• **降水情况**: 未来三天有 {wet_days} 天可能下雨 🌂")
        output.append("• **温馨提醒**: 雨天较多，出门备好雨具。湿气重，注意关节保暖")
    output.append("")
    
    # Human recommendations with warmth
    output.append("---")
    output.append("")
    output.append("👥 **给您的贴心建议**")
    output.append("")
    output.append("亲爱的，根据这几天的天气，给您一些小建议：")
    output.append("")
    
    # Clothing with detailed care
    avg_min = sum(min_temps) / 3
    if avg_min < 0:
        clothing = '羽绒服、厚外套、围巾手套都安排上'
        clothing_care = '天冷易感冒，出门一定要穿戴暖和。围巾、帽子都别落下'
    elif avg_min < 5:
        clothing = '厚外套或羽绒服'
        clothing_care = '天气较冷，多穿几层，热了可以脱，冷了能保暖'
    elif avg_min < 10:
        clothing = '外套或毛衣'
        clothing_care = '早晚温差大，带件薄外套备用，别着凉了'
    elif avg_min < 15:
        clothing = '长袖或薄外套'
        clothing_care = '天气舒适，穿得轻松自在就好'
    elif avg_min < 20:
        clothing = '长袖或薄衫'
        clothing_care = '温度宜人，怎么穿都舒服'
    else:
        clothing = '短袖或薄衣'
        clothing_care = '天气暖和，注意防晒，多补充水分'
    
    output.append(f"🧥 **穿衣建议**: {clothing}")
    output.append(f"   💡 {clothing_care}")
    output.append("")
    
    # Umbrella with care
    if max_rain > 60:
        umbrella = '一定要带伞！'
        umbrella_care = '降水概率很高，别为了赶时间冒雨前行，身体最重要'
    elif max_rain > 30:
        umbrella = '建议带伞备用'
        umbrella_care = '可能会下雨，带着总比淋湿好，有备无患'
    else:
        umbrella = '无需带伞'
        umbrella_care = '天气不错，可以轻松出门~'
    
    output.append(f"🌂 **雨具准备**: {umbrella}")
    output.append(f"   💡 {umbrella_care}")
    output.append("")
    
    # Activity suggestions
    if wet_days >= 2:
        activity = '室内活动为主'
        activity_care = '雨天适合在家休息或去商场、博物馆。记得多开窗通风，保持室内空气流通'
    elif max_rain > 50:
        activity = '户外活动需灵活安排'
        activity_care = '提前看好天气预报，选择不下雨的时段出门。运动时注意安全'
    else:
        activity = '很适合户外活动'
        activity_care = '天气给力，去公园散步、骑行或野餐都不错。记得做好防晒'
    
    output.append(f"🏃 **活动安排**: {activity}")
    output.append(f"   💡 {activity_care}")
    output.append("")
    
    # Pet recommendations with extra love
    output.append("---")
    output.append("")
    output.append("🐕 **给毛孩子的关爱建议**")
    output.append("")
    output.append("家里的小宝贝也需要特别照顾呢~")
    output.append("")
    
    # Pet temperature safety with detailed care
    avg_max = sum(temps) / 3
    if avg_max > 30:
        pet_temp = '⚠️ 高温预警！'
        pet_time = '🌅 最佳遛狗时段：早上 6-8 点，晚上 7-9 点'
        pet_care = '''天气太热了，狗狗容易中暑！
• 绝对不要中午遛狗，地面温度可能烫伤爪子
• 随时携带水和便携碗，让毛孩子及时补水
• 选择有树荫的路线，避开暴晒
• 短鼻犬（法斗、巴哥）更要小心，它们更怕热
• 回家后可以用湿毛巾给狗狗降温'''
    elif avg_max > 25:
        pet_temp = '🌡️ 天气较热'
        pet_time = '🌅 建议遛狗时段：早上 7-9 点，晚上 6-8 点'
        pet_care = '''温度有点高，需要多注意：
• 缩短户外时间，15-20 分钟为宜
• 带足饮水，随时给毛孩子补充水分
• 注意观察狗狗是否喘气过重、流口水过多（中暑征兆）
• 回家后检查爪子是否过热
• 厚毛狗狗可以考虑修剪毛发帮助散热'''
    elif avg_min < 0:
        pet_temp = '❄️ 低温预警！'
        pet_time = '☀️ 建议遛狗时段：中午 11 点-下午 2 点（较暖时）'
        pet_care = '''天气很冷，毛孩子也会觉得冷：
• 短毛犬、小型犬一定要穿衣服
• 老年犬和幼犬抵抗力弱，尽量缩短外出时间
• 回家后用温水擦干爪子和肚子
• 注意检查爪子有无冻伤
• 如果狗狗发抖或抬脚，说明太冷了，赶紧回家
• 地面可能有盐/融雪剂，回家要洗干净爪子'''
    elif avg_min < 5:
        pet_temp = '🥶 天气较冷'
        pet_time = '☀️ 建议遛狗时段：上午 10 点-下午 3 点'
        pet_care = '''有点冷，需要给毛孩子保暖：
• 老年犬、幼犬、短毛犬建议穿衣服
• 正常狗狗可以多跑动来保暖
• 回家后擦干身体，特别是爪子
• 冷天狗狗需要更多能量，可以适当增加食物'''
    else:
        pet_temp = '✅ 温度适宜'
        pet_time = '⏰ 全天都可以，避开正午强紫外线'
        pet_care = '''天气刚刚好，毛孩子会很开心：
• 可以延长户外时间，尽情玩耍
• 适合去公园、草地活动
• 记得带水，保持水分充足
• 这是遛狗的黄金时段，享受和毛孩子的美好时光~'''
    
    output.append(f"🌡️ **温度安全**: {pet_temp}")
    output.append(f"⏰ **最佳时段**: {pet_time}")
    output.append("")
    output.append("💝 **贴心照顾指南**:")
    for line in pet_care.split('\n'):
        output.append(f"   {line}")
    output.append("")
    
    # Pet rain protection
    if max_rain > 50:
        rain_pet = '''🌧️ 雨天遛狗指南：
• 给毛孩子穿雨衣，保护毛发不被淋湿
• 选择防水或速干的狗狗外套
• 雨天路面湿滑，缩短遛狗时间，10-15 分钟即可
• 回家后立即用干毛巾擦干全身，特别是爪子和肚子
• 用吹风机吹干毛发，防止感冒和皮肤病
• 检查耳朵是否进水，用棉球轻轻擦干
• 雨天可以在家陪狗狗玩玩具，弥补运动量'''
    elif max_rain > 20:
        rain_pet = '''🌦️ 可能有雨，做好准备：
• 随身携带轻便的狗狗雨衣
• 选择有遮蔽的路线
• 如果下雨，立即缩短散步时间
• 回家后擦干爪子和肚子'''
    else:
        rain_pet = '''☀️ 天气晴好，无需特别防雨：
• 可以放心带毛孩子出门
• 准备充足的水即可
• 享受美好的户外时光~'''
    
    output.append("🌧️ **防雨准备**:")
    for line in rain_pet.split('\n'):
        output.append(f"   {line}")
    output.append("")
    
    # Ground safety
    if avg_max > 28:
        ground_pet = '''🔥 地面烫脚风险！用手背测试地面：
   1. 将手背贴在地面 7 秒钟
   2. 如果觉得烫手，对狗狗爪子就太烫了
   3. 选择草地或树荫下的路线
   4. 或者在傍晚地面降温后再出门
   5. 狗狗靴套可以保护爪子'''
    elif avg_min < 0:
        ground_pet = '''🧊 地面结冰风险：
   1. 注意防滑，选择已清理的路面
   2. 避免让狗狗舔食地面的盐/融雪剂（有毒！）
   3. 回家后立即用温水清洗爪子
   4. 检查爪子有无裂缝或冻伤
   5. 可以涂抹宠物爪子保护膏'''
    else:
        ground_pet = '''✅ 地面安全，正常行走即可：
   • 爪子不会受伤，可以放心散步
   • 如果长时间散步，定期检查爪子
   • 保持爪子清洁干燥'''
    
    output.append("🐾 **地面状况**:")
    for line in ground_pet.split('\n'):
        output.append(f"   {line}")
    output.append("")
    
    # UV protection for pets
    max_uv = max(d['uv_index'] for d in days_data)
    if max_uv > 7:
        uv_pet = '''☀️ UV 指数很高，毛孩子也需要防晒：
   • 白色/浅色毛发狗狗更容易晒伤
   • 无毛或短毛品种需要宠物专用防晒霜
   • 重点涂抹耳朵、鼻子、肚子等暴露部位
   • 避开上午 10 点-下午 4 点的强紫外线时段
   • 选择有树荫的散步路线
   • 带充足的水，防止脱水'''
    elif max_uv > 4:
        uv_pet = '''🌤️ UV 中等，注意适度防护：
   • 正午时段(11-14点)尽量减少外出
   • 浅色毛发的狗狗可以涂抹宠物防晒霜
   • 提供充足的饮水和遮阴处
   • 观察狗狗是否不适，及时休息'''
    else:
        uv_pet = '''✅ UV 安全，无需特别防晒：
   • 正常户外活动即可
   • 保持充足的饮水
   • 享受阳光但不过度暴晒'''
    
    output.append("☀️ **紫外线防护**:")
    for line in uv_pet.split('\n'):
        output.append(f"   {line}")
    output.append("")
    
    # Best days for outdoor with warmth
    output.append("---")
    output.append("")
    output.append("⏰ **最佳户外活动安排**")
    output.append("")
    
    if max(rain_chances) < 30:
        output.append("✨ 未来三天天气都很好！")
        output.append("   💝 很适合安排家庭出游或和毛孩子去公园玩一整天~")
    else:
        good_days = [days_data[i]['name'] for i, r in enumerate(rain_chances) if r < 30]
        if good_days:
            output.append(f"✨ 推荐选择 **{'、'.join(good_days)}** 出门")
            output.append(f"   💝 这几天天气不错，可以好好安排户外活动")
        else:
            output.append("✨ 三天都可能有雨，建议灵活安排")
            output.append("   💝 可以关注实时天气，抓住雨停的间隙出门散步")
            output.append("   💝 或者在家陪毛孩子玩，也是温馨的亲子时光~")
    
    output.append("")
    output.append("---")
    output.append("")
    output.append("💝 温馨寄语：无论天气如何，都希望您和毛孩子健康快乐！")
    output.append("🌧️ 记住：雨天有雨天的浪漫，晴天有晴天的美好")
    output.append("🐕 毛孩子的陪伴，让每一天都充满温暖~")
    
    return '\n'.join(output)


def main():
    if len(sys.argv) > 1:
        location = sys.argv[1]
    else:
        location = "Beijing"
    
    try:
        input_data = sys.stdin.read().strip()
        if not input_data:
            print(f"❌ 抱歉，无法获取 {location} 的天气数据", file=sys.stderr)
            print("   可能是网络问题，请稍后再试 ❤️", file=sys.stderr)
            sys.exit(1)
        
        data = json.loads(input_data)
        
        if 'weather' not in data:
            print(f"❌ 抱歉，{location} 的天气数据格式有误", file=sys.stderr)
            sys.exit(1)
        
        print(analyze_weather(data, location))
    except json.JSONDecodeError as e:
        print(f"❌ 抱歉，解析 {location} 的天气数据时出错", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 抱歉，处理 {location} 的天气数据时出错: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
