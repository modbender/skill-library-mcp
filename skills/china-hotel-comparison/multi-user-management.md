# 多用户管理与家庭共享系统

## 核心概念：一人一档，家庭共享，数据隔离

### 1. 用户识别系统

#### A. 用户标识方法
```yaml
用户识别策略:
  1. 显式标识:
    - 用户自定用户名/昵称
    - 家庭成员关系标识
    - 偏好标签设置
  
  2. 隐式识别:
    - 对话风格和用语习惯
    - 搜索和筛选模式
    - 决策时间和深度
    - 历史选择偏好
  
  3. 会话关联:
    - 会话ID关联
    - 设备/环境识别
    - 时间模式识别
```

#### B. 用户档案结构
```json
{
  "user_id": "user_001",
  "profile": {
    "basic_info": {
      "nickname": "老公",
      "role": "primary_user",
      "family_id": "family_001",
      "sharing_preferences": {
        "share_search_history": true,
        "share_preferences": true,
        "share_booking_history": false
      }
    },
    
    "behavior_signature": {
      "search_patterns": ["price_first", "detailed_comparison"],
      "decision_style": "cautious",
      "time_patterns": "evening_searches",
      "platform_preferences": ["qunar", "ctrip"]
    },
    
    "family_relationships": [
      {
        "user_id": "user_002",
        "relationship": "spouse",
        "nickname": "老婆",
        "sharing_level": "full",
        "last_sync": "2026-02-25T11:11:00Z"
      }
    ]
  }
}
```

### 2. 数据隔离与共享策略

#### A. 数据分类与权限
```yaml
数据分类:
  1. 个人私有数据:
    - 精确搜索历史
    - 个人选择记录
    - 隐私偏好设置
    - 支付相关信息
  
  2. 可共享数据:
    - 通用筛选偏好
    - 酒店评价标准
    - 预算范围习惯
    - 成功预订模式
  
  3. 家庭共享数据:
    - 家庭旅行需求
    - 共同偏好设置
    - 家庭预算范围
    - 儿童/老人特殊需求
  
  4. 公共参考数据:
    - 酒店基本信息
    - 市场价格数据
    - 通用评价标准
    - 平台特点分析
```

#### B. 共享级别定义
```yaml
共享级别:
  级别0: 完全私有
    - 仅本人可见
    - 不参与任何共享
    - 独立学习优化
  
  级别1: 匿名共享
    - 行为模式匿名共享
    - 用于群体学习优化
    - 不暴露个人身份
  
  级别2: 家庭共享
    - 在家庭内完全共享
    - 支持协同决策
    - 保持家庭外私有
  
  级别3: 完全共享
    - 所有数据可共享
    - 用于家庭协同
    - 支持代他人搜索
```

#### C. 家庭数据同步机制
```python
class FamilyDataSync:
    def __init__(self, family_id):
        self.family_id = family_id
        self.members = self.load_family_members()
        self.shared_data = self.load_shared_data()
    
    def sync_preferences(self, user_id, preferences):
        """同步用户偏好到家庭共享池"""
        # 根据共享级别过滤数据
        filtered_data = self.filter_by_sharing_level(user_id, preferences)
        
        # 更新家庭共享数据
        self.shared_data['preferences'].update(filtered_data)
        
        # 通知其他家庭成员
        self.notify_members(user_id, 'preferences_updated')
    
    def get_family_recommendations(self, user_id, query):
        """获取基于家庭数据的推荐"""
        # 结合个人和家庭数据
        personal_data = self.get_personal_data(user_id)
        family_data = self.shared_data
        
        # 生成综合推荐
        recommendations = self.generate_family_aware_recommendations(
            personal_data, family_data, query
        )
        
        return recommendations
```

### 3. 用户切换与识别流程

#### A. 新用户识别流程
```
1. 检测新会话特征
2. 询问用户身份确认
3. 创建或加载用户档案
4. 设置共享偏好
5. 开始个性化学习
```

#### B. 用户切换对话示例
```
系统：检测到新的对话风格，请问是新的用户吗？

用户：是的，这是我老婆

系统：👋 欢迎！我是国内酒店比价助手。
     检测到您来自 [老公] 的家庭。
     请问您希望：
     1. 使用独立账户（全新开始）
     2. 使用家庭共享账户（共享部分偏好）
     3. 临时帮 [老公] 查询

用户：使用家庭共享账户

系统：✅ 已为您连接到家庭账户。
     共享设置：
     - 家庭预算偏好：已同步
     - 常用筛选条件：已同步  
     - 历史成功选择：已同步
     - 个人搜索记录：保持私有
     
     请问今天需要查询什么酒店？
```

#### C. 身份确认机制
```python
def identify_user(context):
    """识别当前用户身份"""
    # 检查显式标识
    if context.get('explicit_identity'):
        return load_user_by_id(context['explicit_identity'])
    
    # 分析隐式特征
    behavior_signature = analyze_behavior_signature(context)
    
    # 匹配现有用户
    matched_user = match_behavior_signature(behavior_signature)
    
    if matched_user:
        # 确认身份
        return confirm_and_load_user(matched_user, context)
    else:
        # 创建新用户
        return create_new_user(context)
```

### 4. 家庭协同功能

#### A. 协同搜索功能
```yaml
协同搜索特性:
  1. 需求合并:
    - 合并多个家庭成员的需求
    - 识别共同点和差异点
    - 生成综合搜索条件
  
  2. 偏好平衡:
    - 平衡不同成员的偏好权重
    - 识别必须满足的需求
    - 提供妥协方案
  
  3. 决策支持:
    - 显示各成员的偏好匹配度
    - 提供家庭友好型推荐
    - 支持投票或共识机制
```

#### B. 家庭旅行档案
```json
{
  "family_id": "family_001",
  "family_profile": {
    "name": "张氏家庭",
    "members": [
      {"id": "user_001", "role": "husband", "age_group": "adult"},
      {"id": "user_002", "role": "wife", "age_group": "adult"},
      {"id": "user_003", "role": "child", "age_group": "child_8"}
    ],
    
    "travel_preferences": {
      "common": {
        "budget_range": {"min": 400, "max": 800},
        "preferred_regions": ["city_center", "near_attractions"],
        "important_facilities": ["free_wifi", "air_conditioning"]
      },
      
      "individual": {
        "user_001": {"priority": "price_sensitivity", "weight": 0.4},
        "user_002": {"priority": "cleanliness", "weight": 0.3},
        "user_003": {"priority": "child_friendly", "weight": 0.3}
      }
    },
    
    "history": {
      "joint_trips": [
        {
          "date": "2026-02-28",
          "destination": "shanghai_disney",
          "participants": ["user_001", "user_002", "user_003"],
          "selected_hotel": "shanghai_international_hotel",
          "satisfaction": 4.5
        }
      ]
    }
  }
}
```

#### C. 家庭推荐算法
```python
def generate_family_recommendation(family_profile, query):
    """生成家庭感知的推荐"""
    recommendations = []
    
    # 获取各成员的个人偏好
    member_preferences = get_member_preferences(family_profile['members'])
    
    # 计算家庭综合偏好
    family_preference = calculate_family_preference(member_preferences)
    
    # 搜索候选酒店
    candidates = search_hotels(query)
    
    # 为每个候选计算家庭匹配度
    for hotel in candidates:
        # 计算对各成员的匹配度
        member_scores = {}
        for member_id, preferences in member_preferences.items():
            score = calculate_match_score(hotel, preferences)
            member_scores[member_id] = score
        
        # 计算家庭综合得分
        family_score = calculate_family_score(member_scores, family_profile)
        
        # 识别必须满足的需求
        must_have_check = check_must_have_requirements(hotel, family_profile)
        
        if must_have_check['passed']:
            recommendations.append({
                'hotel': hotel,
                'family_score': family_score,
                'member_scores': member_scores,
                'strengths': must_have_check['strengths'],
                'weaknesses': must_have_check['weaknesses']
            })
    
    # 按家庭得分排序
    recommendations.sort(key=lambda x: x['family_score'], reverse=True)
    
    return recommendations
```

### 5. 隐私保护与数据安全

#### A. 数据隔离实现
```yaml
存储隔离:
  个人数据存储:
    - 路径: /users/{user_id}/private/
    - 加密: 用户级加密
    - 访问: 仅本人可访问
  
  家庭共享存储:
    - 路径: /families/{family_id}/shared/
    - 加密: 家庭级加密  
    - 访问: 家庭成员可访问
  
  公共参考存储:
    - 路径: /public/reference/
    - 加密: 系统级加密
    - 访问: 所有用户可读
```

#### B. 权限控制系统
```python
class AccessControl:
    def check_permission(self, user_id, resource_type, resource_id, action):
        """检查用户对资源的访问权限"""
        
        # 获取资源所有权信息
        resource_owner = self.get_resource_owner(resource_type, resource_id)
        
        # 检查直接所有权
        if resource_owner == user_id:
            return self.check_owner_permissions(action)
        
        # 检查家庭共享
        if self.is_family_resource(resource_type, resource_id):
            family_id = self.get_family_id(resource_type, resource_id)
            if self.is_family_member(user_id, family_id):
                sharing_level = self.get_sharing_level(user_id, family_id)
                return self.check_family_permissions(sharing_level, action)
        
        # 检查公共资源
        if self.is_public_resource(resource_type, resource_id):
            return self.check_public_permissions(action)
        
        # 默认拒绝
        return False
```

#### C. 数据清理与退出机制
```yaml
用户权利保障:
  1. 数据查看权:
    - 查看个人所有数据
    - 查看家庭共享数据
    - 导出数据副本
  
  2. 数据修改权:
    - 修改个人偏好设置
    - 调整共享级别
    - 更正错误数据
  
  3. 数据删除权:
    - 删除个人搜索记录
    - 退出家庭共享
    - 完全删除账户
  
  4. 遗忘权:
    - 要求停止学习特定模式
    - 清除特定历史记录
    - 重置个性化推荐
```

### 6. 实施工作流程

#### A. 新用户注册流程
```
1. 检测新用户特征
2. 询问身份确认
3. 创建用户档案
4. 设置共享偏好
5. 连接家庭关系（可选）
6. 开始个性化服务
```

#### B. 家庭账户设置流程
```
1. 主用户创建家庭
2. 邀请家庭成员
3. 成员接受邀请
4. 设置共享级别
5. 同步基础偏好
6. 开始协同服务
```

#### C. 用户切换服务流程
```
1. 检测用户切换
2. 确认用户身份
3. 加载对应档案
4. 应用个性化设置
5. 继续提供服务
6. 记录切换日志
```

### 7. 用户体验优化

#### A. 无缝切换体验
```yaml
切换提示策略:
  自动检测切换:
    - 对话风格变化 > 70%
    - 搜索模式差异 > 60%
    - 明确身份声明
  
  确认方式:
    - 温和询问确认
    - 提供快速选项
    - 记忆选择减少重复
  
  切换后体验:
    - 保持会话连续性
    - 应用个性化设置
    - 提供上下文帮助
```

#### B. 家庭协同界面
```
🏠 **家庭协同搜索**

**参与成员**：老公、老婆、孩子(8岁)
**综合需求**：上海迪士尼，2月28-29日，家庭出游

**各成员关注点**：
👨 老公：价格优先 (<¥500)，交通便利
👩 老婆：卫生安全，儿童设施，安静环境
👧 孩子：迪士尼主题，游乐空间

**家庭共识**：
✅ 必须：儿童安全设施，家庭房型
✅ 重要：迪士尼交通便利，卫生达标
⚠️ 可妥协：价格可适当上浮，房间大小

**推荐选项**：
1. 🏨 上海迪士尼主题酒店 - 家庭综合分: 9.2/10
2. 🏨 国际旅游度假区酒店 - 家庭综合分: 8.7/10
3. 🏨 亲子主题民宿 - 家庭综合分: 8.5/10
```

#### C. 隐私透明度
```
🔒 **隐私设置面板**

当前用户：老婆 (家庭账户)
共享级别：家庭共享

✅ 已共享数据：
- 家庭预算范围：¥400-800
- 儿童特殊需求：8岁，需要安全设施
- 常用筛选条件：免费取消，含早餐
- 历史成功酒店：迪士尼周边3家

🚫 保持私有数据：
- 个人搜索时间记录
- 单独出行的选择
- 支付和联系方式
- 个人评价和反馈

🛠️ 可调整设置：
[ ] 共享我的搜索历史
[ ] 共享我的个人偏好  
[ ] 允许代我预订
[ ] 参与匿名数据改善
```

### 8. 技术实现考虑

#### A. 架构设计
```yaml
系统架构:
  前端层:
    - 用户界面
    - 身份识别
    - 会话管理
  
  业务逻辑层:
    - 用户档案管理
    - 家庭关系管理
    - 数据权限控制
  
  数据层:
    - 个人数据存储
    - 家庭共享存储
    - 公共参考数据
  
  安全层:
    - 数据加密
    - 访问控制
    - 审计日志
```

#### B. 性能考虑
```yaml
性能优化:
  数据缓存:
    - 用户档案缓存
    - 家庭数据缓存
    - 热门参考缓存
  
  异步处理:
    - 数据同步异步化
    - 推荐计算异步化
    - 学习更新异步化
  
  增量更新:
    - 偏好增量更新
    - 历史增量加载
    - 推荐增量生成
```

#### C. 扩展性考虑
```yaml
扩展支持:
  多设备同步:
    - 跨设备用户识别
    - 数据实时同步
    - 状态一致性
  
  外部集成:
    - 日历集成
    - 通讯录集成
    - 社交分享
  
  未来扩展:
    - 企业账户支持
    - 团队旅行支持
    - 旅行团管理
```

### 9. 测试与验证

#### A. 功能测试用例
```yaml
用户识别测试:
  - 新用户自动识别
  - 老用户准确识别
  - 用户切换流畅
  - 身份混淆处理

数据隔离测试:
  - 个人数据隐私保护
  - 家庭数据正确共享
  - 权限控制有效性
  - 数据泄露防护

家庭协同测试:
  - 多需求合并正确性
  - 偏好平衡合理性
  - 推荐匹配准确性
  - 冲突解决有效性
```

#### B. 用户体验测试
```yaml
易用性测试:
  - 新用户上手难度
  - 家庭设置便利性
  - 切换操作直观性
  - 隐私控制清晰性

性能测试:
  - 用户识别响应时间
  - 数据加载速度
  - 推荐生成效率
  - 同步延迟时间
```

---

通过这个多用户管理系统，skill能够：
1. **准确识别不同用户**，提供个性化服务
2. **支持家庭共享**，实现协同决策
3. **严格数据隔离**，保护个人隐私
4. **无缝切换体验**，方便多人使用

现在可以安全地推荐给家人使用，每个人都能获得个性化的服务，同时享受家庭协同的便利。