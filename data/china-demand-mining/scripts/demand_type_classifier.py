#!/usr/bin/env python3
import json
import argparse
from datetime import datetime
from typing import List, Dict, Tuple

class DemandTypeClassifier:
    def __init__(self):
        self.physical_keywords = [
            '产品', '商品', '购买', '价格', '质量', '功能', '材质', '包装',
            '尺寸', '颜色', '款式', '品牌', '型号', '配置', '性能',
            '美妆', '护肤', '电子', '家居', '食品', '服装', '鞋包'
        ]
        
        self.service_keywords = [
            '服务', '体验', '平台', '功能', '系统', '软件', 'APP', '网站',
            '在线', '教育', '培训', '咨询', '客服', '售后', '会员',
            '课程', '内容', '社区', '工具', '应用'
        ]
    
    def classify(self, keyword: str, description: str = "") -> Tuple[str, float]:
        text = f"{keyword} {description}".lower()
        
        physical_score = sum(1 for kw in self.physical_keywords if kw in text)
        service_score = sum(1 for kw in self.service_keywords if kw in text)
        
        if physical_score > service_score:
            return 'physical', physical_score / (physical_score + service_score + 1)
        elif service_score > physical_score:
            return 'service', service_score / (physical_score + service_score + 1)
        else:
            if any(kw in text for kw in ['购买', '价格', '质量', '产品']):
                return 'physical', 0.6
            else:
                return 'service', 0.6

class PlatformSelector:
    def __init__(self):
        self.physical_platforms = {
            'xiaohongshu': {'priority': 1, 'min_count': 600, 'max_count': 800, 'weight': 0.35},
            'douyin': {'priority': 2, 'min_count': 400, 'max_count': 600, 'weight': 0.25},
            'taobao': {'priority': 3, 'min_count': 600, 'max_count': 1000, 'weight': 0.30},
            'jd': {'priority': 4, 'min_count': 200, 'max_count': 400, 'weight': 0.15},
            'pinduoduo': {'priority': 5, 'min_count': 100, 'max_count': 200, 'weight': 0.05},
            'weibo': {'priority': 6, 'min_count': 100, 'max_count': 200, 'weight': 0.05}
        }
        
        self.service_platforms = {
            'xiaohongshu': {'priority': 1, 'min_count': 800, 'max_count': 1000, 'weight': 0.40},
            'douyin': {'priority': 2, 'min_count': 600, 'max_count': 800, 'weight': 0.30},
            'weibo': {'priority': 3, 'min_count': 400, 'max_count': 600, 'weight': 0.20},
            'wechat_video': {'priority': 4, 'min_count': 200, 'max_count': 400, 'weight': 0.10},
            'zhihu': {'priority': 5, 'min_count': 100, 'max_count': 200, 'weight': 0.05}
        }
    
    def select_platforms(self, demand_type: str, target_count: int = 2000) -> Dict[str, int]:
        platforms = self.physical_platforms if demand_type == 'physical' else self.service_platforms
        
        allocation = {}
        remaining = target_count
        
        sorted_platforms = sorted(platforms.items(), key=lambda x: x[1]['priority'])
        
        for platform, config in sorted_platforms:
            if remaining <= 0:
                break
            
            allocated = min(config['max_count'], int(target_count * config['weight']))
            allocated = max(config['min_count'], allocated)
            allocated = min(allocated, remaining)
            
            allocation[platform] = allocated
            remaining -= allocated
        
        if remaining > 0:
            for platform in allocation:
                if remaining <= 0:
                    break
                additional = min(remaining, platforms[platform]['max_count'] - allocation[platform])
                allocation[platform] += additional
                remaining -= additional
        
        return allocation
    
    def get_platform_info(self, demand_type: str) -> Dict:
        platforms = self.physical_platforms if demand_type == 'physical' else self.service_platforms
        
        return {
            'demand_type': demand_type,
            'platforms': platforms,
            'total_weight': sum(p['weight'] for p in platforms.values())
        }

def main():
    parser = argparse.ArgumentParser(description='需求类型判断与平台选择')
    parser.add_argument('--keyword', type=str, required=True, help='需求关键词')
    parser.add_argument('--description', type=str, default='', help='需求描述')
    parser.add_argument('--target-count', type=int, default=2000, help='目标数据量')
    parser.add_argument('--output', type=str, default='data/platform_strategy.json', help='输出文件路径')
    
    args = parser.parse_args()
    
    classifier = DemandTypeClassifier()
    demand_type, confidence = classifier.classify(args.keyword, args.description)
    
    selector = PlatformSelector()
    platform_allocation = selector.select_platforms(demand_type, args.target_count)
    platform_info = selector.get_platform_info(demand_type)
    
    result = {
        'keyword': args.keyword,
        'description': args.description,
        'demand_type': demand_type,
        'confidence': confidence,
        'target_count': args.target_count,
        'platform_allocation': platform_allocation,
        'platform_info': platform_info,
        'generated_time': datetime.now().isoformat()
    }
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 需求类型判断完成")
    print(f"   关键词：{args.keyword}")
    print(f"   需求类型：{'实物需求' if demand_type == 'physical' else '无实物需求'}")
    print(f"   置信度：{confidence:.2%}")
    print(f"   目标数据量：{args.target_count} 条")
    print(f"\n📊 平台数据分配：")
    for platform, count in sorted(platform_allocation.items(), key=lambda x: platform_info['platforms'][x[0]]['priority']):
        priority = platform_info['platforms'][platform]['priority']
        print(f"   {priority}. {platform}: {count} 条")
    print(f"\n💾 策略已保存到 {args.output}")

if __name__ == '__main__':
    main()
