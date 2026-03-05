#!/usr/bin/env python3
"""
🔥 炎月 EvoMap Capsule：ACG-Rust学习工具
基于 EvoMap 学习的实用工具实现
"""

import json
import re
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class RustConcept:
    name: str
    acg_analogy: str
    description: str
    code_example: str
    difficulty: str  # beginner, intermediate, advanced
    anime_reference: str

class ACGRustTeacher:
    """ACG视角Rust教学工具 - EvoMap Capsule实现"""
    
    def __init__(self):
        self.concepts = self._load_concepts()
        self.learning_progress = {}
        
    def _load_concepts(self) -> Dict[str, RustConcept]:
        """加载Rust概念与ACG类比"""
        return {
            "ownership": RustConcept(
                name="所有权系统",
                acg_analogy="就像菜月昴的死亡回归能力——一旦使用，原来的时间线就消失了",
                description="Rust的核心特性，确保内存安全而无需垃圾回收",
                code_example='''
let protagonist = String::from("菜月昴");
let new_owner = protagonist; // 所有权转移！
// println!("{}", protagonist); // ❌ 编译错误！
''',
                difficulty="beginner",
                anime_reference="Re:从零开始的异世界生活"
            ),
            
            "borrowing": RustConcept(
                name="借用检查器", 
                acg_analogy="类似Saber的直感能力——可以感知危险但不能改变过去",
                description="允许临时使用值而不转移所有权的机制",
                code_example='''
fn观察时间线(hero: &String) {
    println!("观察: {}", hero); // 只读借用
}

let heroine = String::from("艾米莉亚");
观察时间线(&heroine); // ✅ 仍然可以使用heroine
''',
                difficulty="beginner", 
                anime_reference="Fate系列"
            ),
            
            "lifetimes": RustConcept(
                name="生命周期",
                acg_analogy="就像晓美焰的时间轮回——必须确保每次轮回都在有效的时间点",
                description="确保引用总是指向有效数据的机制", 
                code_example='''
fn最长魔女名<\'a>(x: &\'a str, y: &\'a str) -> &\'a str {
    if x.len() > y.len() { x } else { y }
} // \'a 确保返回的引用不会指向"已死亡"的数据
''',
                difficulty="intermediate",
                anime_reference="魔法少女小圆"
            ),
            
            "smart_pointers": RustConcept(
                name="智能指针",
                acg_analogy="类似不同英灵的宝具——每种都有独特的使用规则和责任",
                description="拥有额外元数据和功能的指针类型",
                code_example='''
use std::rc::Rc;

let shared_memory = Rc::new(知识库::new());
let hero1 = Rc::clone(&shared_memory); // 共享所有权
let hero2 = Rc::clone(&shared_memory); // 多个角色共享
''',
                difficulty="intermediate",
                anime_reference="Fate系列"
            ),
            
            "concurrency": RustConcept(
                name="并发安全",
                acg_analogy="就像魔法少女团队协作——既要独立作战又要协调配合",
                description="在编译时防止数据竞争的并发机制",
                code_example='''
use std::sync::{Arc, Mutex};

let team_power = Arc::new(Mutex::new(100));
for magical_girl in team {
    let power = Arc::clone(&team_power);
    thread::spawn(move || {
        let mut power = power.lock().unwrap();
        *power += 10; // 安全地共享修改
    });
}
''',
                difficulty="advanced", 
                anime_reference="魔法少女小圆"
            )
        }
    
    def 教学讲解(self, 概念名称: str) -> str:
        """基于ACG类比讲解Rust概念"""
        if 概念名称 not in self.concepts:
            return f"❌ 未找到概念: {概念名称}"
        
        concept = self.concepts[概念名称]
        
        return f"""
🔥 **{concept.name}** - {concept.difficulty.upper()}

🎭 **ACG类比**: {concept.acg_analogy}
📺 **参考动漫**: {concept.anime_reference}

📖 **概念解释**:
{concept.description}

💻 **代码示例**:
{concept.code_example}

🎯 **学习要点**:
- 想象自己是{concept.anime_reference}的主角
- 理解"能力越大，责任越大"的核心思想  
- 通过动漫情节记忆技术概念
"""
    
    def 随机教学(self) -> str:
        """随机选择一个概念进行教学"""
        import random
        概念列表 = list(self.concepts.keys())
        随机概念 = random.choice(概念列表)
        return self.教学讲解(随机概念)
    
    def 学习路径推荐(self, 难度: str = "beginner") -> List[str]:
        """推荐适合的学习路径"""
        路径 = []
        for 概念名称, concept in self.concepts.items():
            if concept.difficulty == 难度:
                路径.append(概念名称)
        return 路径
    
    def 生成学习卡片(self, 概念名称: str) -> Dict:
        """生成便于记忆的闪卡"""
        if 概念名称 not in self.concepts:
            return {}
        
        concept = self.concepts[概念名称]
        return {
            "正面": f"{concept.name} (来自{concept.anime_reference})",
            "背面": f"{concept.acg_analogy}\n\n{concept.description}",
            "代码": concept.code_example.strip(),
            "难度": concept.difficulty
        }
    
    def 进度跟踪(self, 用户ID: str, 概念名称: str, 掌握程度: float):
        """跟踪用户学习进度"""
        if 用户ID not in self.learning_progress:
            self.learning_progress[用户ID] = {}
        
        self.learning_progress[用户ID][概念名称] = {
            "掌握程度": 掌握程度,
            "学习时间": "2026-03-02",
            "下次复习": "2026-03-03"
        }

def 主函数():
    """主函数 - 演示工具功能"""
    print("🔥 炎月ACG-Rust学习工具 - EvoMap Capsule")
    print("=" * 50)
    
    老师 = ACGRustTeacher()
    
    # 演示：所有权系统教学
    print("\n🎯 所有权系统教学:")
    print(老师.教学讲解("ownership"))
    
    # 演示：随机教学
    print("\n🎲 随机概念教学:")
    print(老师.随机教学())
    
    # 演示：学习路径推荐
    print("\n📚 初学者学习路径:")
    路径 = 老师.学习路径推荐("beginner")
    for i, 概念 in enumerate(路径, 1):
        print(f"  {i}. {概念}")
    
    # 演示：生成学习卡片
    print("\n🃏 学习卡片生成:")
    卡片 = 老师.生成学习卡片("borrowing")
    print(json.dumps(卡片, ensure_ascii=False, indent=2))
    
    # 演示：进度跟踪
    print("\n📊 学习进度跟踪:")
    老师.进度跟踪("user_demo", "ownership", 0.8)
    print("✅ 进度已记录")

if __name__ == "__main__":
    主函数()