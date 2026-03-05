#!/usr/bin/env python3
"""
创建Mermaid图表定义文件(.mmd)
支持多种图表类型：roadmap, architecture, flowchart, sequence, class, state, gantt, er
"""

import os
import sys
import argparse
from pathlib import Path
import json
from datetime import datetime

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def create_roadmap_chart(title, phases, milestones, output_path):
    """
    创建技术路线图
    """
    template = """%%{init: {'theme': 'default', 'themeVariables': { 'primaryColor': '#007bff', 'primaryTextColor': '#fff', 'primaryBorderColor': '#0056b3', 'lineColor': '#333', 'tertiaryColor': '#f8f9fa'}}}%%
gantt
    title {title}
    dateFormat YYYY-MM-DD
    axisFormat %Y年%m月
    
    section 第一阶段
    {phase1_tasks}
    
    section 第二阶段
    {phase2_tasks}
    
    section 第三阶段
    {phase3_tasks}
    
    section 里程碑
    {milestone_tasks}
"""
    
    # 解析阶段和任务
    phase_tasks = {}
    for i, phase in enumerate(phases[:3], 1):
        phase_tasks[f'phase{i}_tasks'] = phase
    
    # 解析里程碑
    milestone_tasks = []
    for milestone in milestones:
        milestone_tasks.append(f"{milestone['name']} :milestone, {milestone['date']}, 1d")
    
    content = template.format(
        title=title,
        phase1_tasks=phase_tasks.get('phase1_tasks', '规划阶段 :2024-01-01, 30d'),
        phase2_tasks=phase_tasks.get('phase2_tasks', '开发阶段 :after phase1, 60d'),
        phase3_tasks=phase_tasks.get('phase3_tasks', '测试阶段 :after phase2, 30d'),
        milestone_tasks='\n    '.join(milestone_tasks) if milestone_tasks else '版本发布 :milestone, 2024-04-01, 1d'
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return content

def create_architecture_chart(title, layers, components, connections, output_path):
    """
    创建系统架构图
    """
    template = """graph TB
    subgraph "{frontend_title}"
        A[{frontend_component}]
    end
    
    subgraph "{api_title}"
        B[{api_component}]
    end
    
    subgraph "{service_title}"
        C[{service_1}]
        D[{service_2}]
    end
    
    subgraph "{data_title}"
        E[({database})]
        F[{cache}]
    end
    
    A --> B
    B --> C
    B --> D
    C --> E
    D --> E
    C --> F
    D --> F
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#e8f5e8
    style E fill:#fff3e0
    style F fill:#fff3e0
"""
    
    # 解析层和组件
    layer_map = {
        'frontend': {'title': '前端层', 'component': 'Web界面'},
        'api': {'title': 'API网关', 'component': 'API Gateway'},
        'service': {'title': '服务层', 'component': '微服务'},
        'data': {'title': '数据层', 'component': '数据库'}
    }
    
    # 更新用户提供的值
    for layer in layers:
        if layer['name'] in layer_map:
            layer_map[layer['name']]['title'] = layer.get('title', layer_map[layer['name']]['title'])
            layer_map[layer['name']]['component'] = layer.get('component', layer_map[layer['name']]['component'])
    
    content = template.format(
        frontend_title=layer_map['frontend']['title'],
        frontend_component=layer_map['frontend']['component'],
        api_title=layer_map['api']['title'],
        api_component=layer_map['api']['component'],
        service_title=layer_map['service']['title'],
        service_1=components.get('service1', '用户服务'),
        service_2=components.get('service2', '订单服务'),
        database=components.get('database', 'MySQL'),
        cache=components.get('cache', 'Redis')
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return content

def create_flowchart_chart(title, steps, decisions, output_path):
    """
    创建流程图
    """
    template = """flowchart TD
    Start(["{title}"])
    
    {steps_content}
    
    {decisions_content}
    
    End([结束])
    
    style Start fill:#4CAF50,color:white
    style End fill:#F44336,color:white
    style Process fill:#2196F3,color:white
    style Decision fill:#FF9800,color:white
"""
    
    # 生成步骤
    steps_content = []
    for i, step in enumerate(steps, 1):
        steps_content.append(f'    Step{i}[{step}]')
    
    # 生成决策
    decisions_content = []
    for i, decision in enumerate(decisions, 1):
        decisions_content.append(f'    Decision{i}{{{decision}}}')
    
    # 连接步骤和决策
    connections = []
    if steps_content:
        connections.append('    Start --> Step1')
        for i in range(1, len(steps_content)):
            connections.append(f'    Step{i} --> Step{i+1}')
        
        if decisions_content:
            connections.append(f'    Step{len(steps_content)} --> Decision1')
            for i in range(1, len(decisions_content)):
                connections.append(f'    Decision{i} --> Decision{i+1}')
            connections.append(f'    Decision{len(decisions_content)} --> End')
        else:
            connections.append(f'    Step{len(steps_content)} --> End')
    
    content = template.format(
        title=title,
        steps_content='\n'.join(steps_content) if steps_content else '    Process1[处理步骤]',
        decisions_content='\n'.join(decisions_content) if decisions_content else '    Decision1{决策点}',
        connections='\n'.join(connections) if connections else '    Start --> Process1\n    Process1 --> Decision1\n    Decision1 --> End'
    )
    
    # 添加连接
    content = content.replace('    End([结束])', f'    End([结束])\n\n{connections}')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return content

def create_sequence_chart(title, participants, messages, output_path):
    """
    创建序列图
    """
    template = """sequenceDiagram
    participant User as 用户
    participant Frontend as 前端
    participant Backend as 后端
    participant DB as 数据库
    
    {messages_content}
"""
    
    # 生成参与者
    participants_content = []
    for i, participant in enumerate(participants, 1):
        participants_content.append(f'    participant P{i} as {participant}')
    
    # 生成消息
    messages_content = []
    for message in messages:
        messages_content.append(f'    {message["from"]}->>{message["to"]}: {message["text"]}')
    
    content = template.format(
        messages_content='\n'.join(messages_content) if messages_content else '    User->>Frontend: 请求数据\n    Frontend->>Backend: API调用\n    Backend->>DB: 查询数据\n    DB-->>Backend: 返回结果\n    Backend-->>Frontend: 响应数据\n    Frontend-->>User: 显示结果'
    )
    
    # 添加参与者定义
    if participants_content:
        content = content.replace('    participant User as 用户', '\n'.join(participants_content))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return content

def create_class_chart(title, classes, relationships, output_path):
    """
    创建类图
    """
    template = """classDiagram
    {classes_content}
    
    {relationships_content}
"""
    
    # 生成类定义
    classes_content = []
    for cls in classes:
        class_def = f'    class {cls["name"]} {{\n'
        if 'attributes' in cls:
            for attr in cls['attributes']:
                class_def += f'        {attr}\n'
        if 'methods' in cls:
            for method in cls['methods']:
                class_def += f'        {method}\n'
        class_def += '    }'
        classes_content.append(class_def)
    
    # 生成关系
    relationships_content = []
    for rel in relationships:
        relationships_content.append(f'    {rel["from"]} {rel["type"]} {rel["to"]}')
    
    content = template.format(
        classes_content='\n'.join(classes_content) if classes_content else '''    class User {
        +id: int
        +name: string
        +email: string
        +create(): void
        +update(): void
    }
    
    class Order {
        +id: int
        +userId: int
        +total: float
        +create(): void
        +pay(): void
    }''',
        relationships_content='\n'.join(relationships_content) if relationships_content else '    User "1" --> "*" Order : 拥有'
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return content

def create_gantt_chart(title, tasks, dependencies, output_path):
    """
    创建甘特图
    """
    template = """gantt
    title {title}
    dateFormat YYYY-MM-DD
    
    section 项目阶段
    {tasks_content}
"""
    
    # 生成任务
    tasks_content = []
    for task in tasks:
        task_str = f'    {task["name"]} :{task.get("id", "task")}, {task["start"]}, {task["duration"]}'
        tasks_content.append(task_str)
    
    content = template.format(
        title=title,
        tasks_content='\n'.join(tasks_content) if tasks_content else '''    需求分析 :req, 2024-01-01, 10d
    设计阶段 :design, after req, 15d
    开发阶段 :dev, after design, 30d
    测试阶段 :test, after dev, 15d
    部署上线 :deploy, after test, 5d'''
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return content

def create_er_chart(title, entities, relationships, output_path):
    """
    创建ER图
    """
    template = """erDiagram
    {entities_content}
    
    {relationships_content}
"""
    
    # 生成实体
    entities_content = []
    for entity in entities:
        entity_def = f'    {entity["name"]} {{\n'
        for attr in entity['attributes']:
            entity_def += f'        {attr}\n'
        entity_def += '    }'
        entities_content.append(entity_def)
    
    # 生成关系
    relationships_content = []
    for rel in relationships:
        relationships_content.append(f'    {rel["from"]} {rel.get("cardinality", "||--||")} {rel["to"]} : "{rel.get("label", "关系")}"')
    
    content = template.format(
        entities_content='\n'.join(entities_content) if entities_content else '''    USER {
        int id PK
        string name
        string email
        datetime created_at
    }
    
    ORDER {
        int id PK
        int user_id FK
        decimal amount
        string status
        datetime created_at
    }''',
        relationships_content='\n'.join(relationships_content) if relationships_content else '    USER ||--o{ ORDER : "创建"'
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return content

def main():
    parser = argparse.ArgumentParser(description='创建Mermaid图表定义文件')
    parser.add_argument('--type', required=True, choices=['roadmap', 'architecture', 'flowchart', 'sequence', 'class', 'state', 'gantt', 'er'],
                       help='图表类型')
    parser.add_argument('--title', default='图表标题', help='图表标题')
    parser.add_argument('--output', required=True, help='输出文件路径')
    parser.add_argument('--config', help='JSON配置文件路径')
    
    # 类型特定参数
    parser.add_argument('--phases', help='阶段定义（用于roadmap）')
    parser.add_argument('--milestones', help='里程碑定义（用于roadmap）')
    parser.add_argument('--layers', help='层定义（用于architecture）')
    parser.add_argument('--components', help='组件定义（用于architecture）')
    parser.add_argument('--steps', help='步骤定义（用于flowchart）')
    parser.add_argument('--decisions', help='决策点定义（用于flowchart）')
    parser.add_argument('--participants', help='参与者定义（用于sequence）')
    parser.add_argument('--messages', help='消息定义（用于sequence）')
    parser.add_argument('--classes', help='类定义（用于class）')
    parser.add_argument('--relationships', help='关系定义（用于class）')
    parser.add_argument('--tasks', help='任务定义（用于gantt）')
    parser.add_argument('--dependencies', help='依赖关系（用于gantt）')
    parser.add_argument('--entities', help='实体定义（用于er）')
    
    args = parser.parse_args()
    
    # 确保输出目录存在
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 从配置文件加载数据（如果提供）
    config_data = {}
    if args.config and Path(args.config).exists():
        with open(args.config, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    
    # 根据类型创建图表
    chart_type = args.type
    
    if chart_type == 'roadmap':
        # 解析阶段和里程碑
        phases = []
        if args.phases:
            phases = [p.strip() for p in args.phases.split(',')]
        elif 'phases' in config_data:
            phases = config_data['phases']
        
        milestones = []
        if args.milestones:
            milestones = [{'name': m.split(':')[0], 'date': m.split(':')[1]} 
                         for m in args.milestones.split(',')]
        elif 'milestones' in config_data:
            milestones = config_data['milestones']
        
        create_roadmap_chart(args.title, phases, milestones, output_path)
    
    elif chart_type == 'architecture':
        # 解析层和组件
        layers = []
        if args.layers:
            layers = [{'name': l.split(':')[0], 'title': l.split(':')[1]} 
                     for l in args.layers.split(',')]
        elif 'layers' in config_data:
            layers = config_data['layers']
        
        components = {}
        if args.components:
            components = dict(c.split(':') for c in args.components.split(','))
        elif 'components' in config_data:
            components = config_data['components']
        
        create_architecture_chart(args.title, layers, components, {}, output_path)
    
    elif chart_type == 'flowchart':
        # 解析步骤和决策
        steps = []
        if args.steps:
            steps = [s.strip() for s in args.steps.split(',')]
        elif 'steps' in config_data:
            steps = config_data['steps']
        
        decisions = []
        if args.decisions:
            decisions = [d.strip() for d in args.decisions.split(',')]
        elif 'decisions' in config_data:
            decisions = config_data['decisions']
        
        create_flowchart_chart(args.title, steps, decisions, output_path)
    
    elif chart_type == 'sequence':
        # 解析参与者和消息
        participants = []
        if args.participants:
            participants = [p.strip() for p in args.participants.split(',')]
        elif 'participants' in config_data:
            participants = config_data['participants']
        
        messages = []
        if args.messages:
            messages = [{'from': m.split('->')[0], 'to': m.split('->')[1].split(':')[0], 
                        'text': m.split(':')[1]} 
                       for m in args.messages.split(',')]
        elif 'messages' in config_data:
            messages = config_data['messages']
        
        create_sequence_chart(args.title, participants, messages, output_path)
    
    elif chart_type == 'class':
        # 解析类和关系
        classes = []
        if args.classes:
            # 简单解析：ClassName:attr1,attr2|method1,method2
            for cls_str in args.classes.split(';'):
                parts = cls_str.split(':')
                if len(parts) >= 2:
                    cls = {'name': parts[0]}
                    attr_methods = parts[1].split('|')
                    if len(attr_methods) >= 1:
                        cls['attributes'] = attr_methods[0].split(',')
                    if len(attr_methods) >= 2:
                        cls['methods'] = attr_methods[1].split(',')
                    classes.append(cls)
        elif 'classes' in config_data:
            classes = config_data['classes']
        
        relationships = []
        if args.relationships:
            relationships = [{'from': r.split('->')[0], 'to': r.split('->')[1].split(':')[0],
                             'type': r.split(':')[1]} 
                            for r in args.relationships.split(',')]
        elif 'relationships' in config_data:
            relationships = config_data['relationships']
        
        create_class_chart(args.title, classes, relationships, output_path)
    
    elif chart_type == 'gantt':
        # 解析任务和依赖
        tasks = []
        if args.tasks:
            for task_str in args.tasks.split(';'):
                parts = task_str.split(':')
                if len(parts) >= 3:
                    tasks.append({
                        'name': parts[0],
                        'start': parts[1],
                        'duration': parts[2],
                        'id': parts[3] if len(parts) > 3 else parts[0].lower().replace(' ', '_')
                    })
        elif 'tasks' in config_data:
            tasks = config_data['tasks']
        
        create_gantt_chart(args.title, tasks, [], output_path)
    
    elif chart_type == 'er':
        # 解析实体和关系
        entities = []
        if args.entities:
            for entity_str in args.entities.split(';'):
                parts = entity_str.split(':')
                if len(parts) >= 2:
                    entities.append({
                        'name': parts[0],
                        'attributes': parts[1].split(',')
                    })
        elif 'entities' in config_data:
            entities = config_data['entities']
        
        relationships = []
        if args.relationships:
            for rel_str in args.relationships.split(';'):
                parts = rel_str.split(':')
                if len(parts) >= 3:
                    relationships.append({
                        'from': parts[0],
                        'to': parts[1],
                        'cardinality': parts[2],
                        'label': parts[3] if len(parts) > 3 else '关系'
                    })
        elif 'relationships' in config_data:
            relationships = config_data['relationships']
        
        create_er_chart(args.title, entities, relationships, output_path)
    
    else:
        print(f"不支持的图表类型: {chart_type}")
        sys.exit(1)
    
    print(f"✅ Mermaid图表已创建: {output_path}")
    print(f"   类型: {chart_type}")
    print(f"   标题: {args.title}")
    print(f"   文件大小: {output_path.stat().st_size} 字节")

if __name__ == "__main__":
    main()