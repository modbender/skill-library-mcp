/**
 * 初中数学教学计划生成功能
 * 根据年级、章节、课时自动生成教学计划
 */

class TeachingPlanGenerator {
  constructor() {
    // 各年级标准课时安排
    this.standardHours = {
      '七年级': {
        '第4章 一元一次方程': 12, // 5个课时×2.4周
        '第5章 图形的初步': 8,
        '有理数': 10,
        '整式的加减': 8,
        '期末复习': 6
      },
      '八年级': {
        '第13章 三角形': 10,
        '第14章 全等三角形': 12,
        '第15章 轴对称': 10,
        '第16章 整式的乘法与因式分解': 14,
        '第17章 分式': 12,
        '期中复习': 4,
        '期末复习': 6
      },
      '九年级': {
        '二次函数': 16,
        '旋转': 8,
        '圆': 14,
        '概率': 6,
        '一元二次方程': 10,
        '一轮复习': 20,
        '二轮复习': 15,
        '三轮复习': 10,
        '考前冲刺': 5
      }
    };

    // 教学环节模板
    this.teachingSteps = [
      '1. 导入新课（5分钟）',
      '2. 知识讲解（15分钟）',
      '3. 例题示范（10分钟）',
      '4. 学生练习（10分钟）',
      '5. 课堂小结（5分钟）',
      '6. 布置作业（5分钟）'
    ];
  }

  /**
   * 生成单课时教学计划
   */
  generateLessonPlan(grade, chapter, lessonTitle) {
    const date = new Date().toLocaleDateString('zh-CN');
    
    return `# ${grade}数学 ${chapter} - ${lessonTitle}
    
## 基本信息
- **年级**: ${grade}
- **章节**: ${chapter}
- **课题**: ${lessonTitle}
- **日期**: ${date}
- **课时**: 1课时（45分钟）

## 教学目标
### 知识与技能
1. 掌握${lessonTitle}的基本概念
2. 理解相关定理和公式
3. 能够解决基础问题

### 过程与方法
1. 通过观察、思考、探究的学习过程
2. 培养数学思维和解决问题的能力
3. 学会合作交流和表达

### 情感态度与价值观
1. 培养学习数学的兴趣
2. 建立学好数学的信心
3. 体会数学在实际生活中的应用

## 教学重难点
### 教学重点
- ${lessonTitle}的核心概念
- 基本方法和技巧

### 教学难点
- 抽象概念的理解
- 综合应用能力的培养

## 教学过程
${this.teachingSteps.join('\n')}

## 教学资源
1. 课件：${chapter}教学课件
2. 学案：${lessonTitle}知识训练学案
3. 练习：同步练习题
4. 教具：多媒体设备、几何模型等

## 作业布置
1. 完成学案上的练习题
2. 预习下一节内容
3. 收集生活中的相关实例

## 教学反思
（课后填写）
- 教学效果：
- 学生反应：
- 改进措施：

---
*生成时间：${new Date().toLocaleString('zh-CN')}*`;
  }

  /**
   * 生成章节教学计划
   */
  generateChapterPlan(grade, chapter) {
    const totalHours = this.standardHours[grade]?.[chapter] || 8;
    const weeks = Math.ceil(totalHours / 5); // 按每周5课时计算
    
    return `# ${grade}数学 ${chapter} 教学计划
    
## 章节概述
- **章节名称**: ${chapter}
- **所属年级**: ${grade}
- **总课时**: ${totalHours}课时
- **教学周数**: ${weeks}周
- **重要程度**: ★★★★☆

## 教学目标
1. **知识目标**: 掌握${chapter}的核心概念、定理和公式
2. **能力目标**: 培养分析问题、解决问题的能力
3. **素养目标**: 发展数学思维，提升数学素养

## 课时安排
| 周次 | 课时 | 教学内容 | 重点难点 | 备注 |
|------|------|----------|----------|------|
${this.generateScheduleTable(grade, chapter, totalHours)}

## 教学资源
### 核心资源
1. **课件**: ${chapter}全套教学课件
2. **学案**: 知识训练学案（含答案）
3. **练习**: 同步练习题集
4. **测试**: 单元测试卷

### 辅助资源
1. 教学视频
2. 几何画板演示
3. 生活实例素材
4. 拓展阅读材料

## 教学方法
1. **启发式教学**: 通过问题引导思考
2. **探究式学习**: 学生自主探究发现
3. **合作学习**: 小组讨论交流
4. **分层教学**: 针对不同层次学生设计任务

## 评价方式
### 形成性评价
1. 课堂表现（20%）
2. 作业完成（30%）
3. 小组活动（20%）

### 终结性评价
1. 单元测试（30%）
2. 项目作品（加分项）

## 注意事项
1. 关注学生的学习状态，及时调整教学节奏
2. 加强个别辅导，帮助学困生跟上进度
3. 鼓励学生提问，培养质疑精神
4. 联系生活实际，增强学习兴趣

---
*计划制定时间：${new Date().toLocaleString('zh-CN')}*`;
  }

  /**
   * 生成课时安排表
   */
  generateScheduleTable(grade, chapter, totalHours) {
    let table = '';
    let hourCount = 0;
    let week = 1;
    
    // 根据章节类型生成不同的课时内容
    const lessonTitles = this.getLessonTitles(grade, chapter);
    
    for (let i = 0; i < lessonTitles.length && hourCount < totalHours; i++) {
      const lesson = lessonTitles[i];
      const weekNum = Math.floor(hourCount / 5) + 1;
      
      table += `| 第${weekNum}周 | 第${hourCount % 5 + 1}课时 | ${lesson} | 掌握基本概念 | 新授课 |\n`;
      hourCount++;
      
      // 每2个新授课后安排1个练习课
      if ((i + 1) % 2 === 0 && hourCount < totalHours) {
        table += `| 第${weekNum}周 | 第${hourCount % 5 + 1}课时 | ${lesson}练习课 | 巩固提高 | 练习课 |\n`;
        hourCount++;
      }
    }
    
    // 最后安排复习课和测试课
    if (hourCount < totalHours) {
      table += `| 第${Math.floor(hourCount / 5) + 1}周 | 第${hourCount % 5 + 1}课时 | 章节复习 | 知识梳理 | 复习课 |\n`;
      hourCount++;
    }
    
    if (hourCount < totalHours) {
      table += `| 第${Math.floor(hourCount / 5) + 1}周 | 第${hourCount % 5 + 1}课时 | 单元测试 | 综合评估 | 测试课 |\n`;
    }
    
    return table;
  }

  /**
   * 获取课时标题
   */
  getLessonTitles(grade, chapter) {
    // 这里可以根据实际资源情况返回具体的课时标题
    const defaultTitles = {
      '七年级': {
        '第4章 一元一次方程': [
          '5.1.1 等式性质（第一课时）',
          '5.1.1 等式性质（第二课时）',
          '5.1.2 方程定义',
          '5.2.1 解一元一次方程-合并同类项',
          '5.2.2 解一元一次方程-移项',
          '5.2.3 解一元一次方程-去括号',
          '5.2.4 解一元一次方程-去分母'
        ]
      },
      '八年级': {
        '第13章 三角形': [
          '13.1 三角形的概念',
          '13.2.1 三角形的边',
          '13.2.2 三角形的中线、角平分线、高',
          '13.3.1 三角形的内角',
          '13.3.2 三角形的外角'
        ]
      },
      '九年级': {
        '二次函数': [
          '二次函数的概念',
          '二次函数的图像和性质',
          '二次函数的最值问题',
          '二次函数的实际应用',
          '二次函数与一元二次方程'
        ]
      }
    };

    return defaultTitles[grade]?.[chapter] || [`${chapter}第1课时`, `${chapter}第2课时`, `${chapter}第3课时`];
  }

  /**
   * 生成学期教学计划
   */
  generateSemesterPlan(grade, semester = '上') {
    const chapters = Object.keys(this.standardHours[grade] || {});
    const totalWeeks = 20; // 标准学期20周
    const totalHours = chapters.reduce((sum, chapter) => sum + (this.standardHours[grade][chapter] || 0), 0);
    
    return `# ${grade}数学 ${semester}学期教学计划
    
## 学期概况
- **学年**: 2025-2026学年
- **学期**: ${semester}学期
- **年级**: ${grade}
- **总课时**: ${totalHours}课时
- **教学周数**: ${totalWeeks}周
- **周课时**: 5课时/周

## 学期目标
### 总体目标
1. 完成${grade}数学${semester}学期全部教学内容
2. 培养学生的数学核心素养
3. 为下一阶段学习打好基础

### 具体目标
1. **知识掌握**: 系统掌握各章节核心知识
2. **能力提升**: 提高分析问题和解决问题的能力
3. **习惯养成**: 培养良好的数学学习习惯
4. **兴趣培养**: 激发学生学习数学的兴趣

## 教学内容安排
| 时间段 | 周次 | 教学内容 | 课时 | 重要活动 | 备注 |
|--------|------|----------|------|----------|------|
${this.generateSemesterSchedule(grade, chapters, totalWeeks)}

## 教学重点
1. **核心概念**: 各章节的基础概念和原理
2. **思想方法**: 数学思想方法的渗透
3. **应用能力**: 解决实际问题的能力
4. **衔接过渡**: 与前后知识的衔接

## 教学措施
### 备课方面
1. 集体备课，资源共享
2. 精心设计教学环节
3. 准备丰富的教学资源

### 上课方面
1. 突出重点，突破难点
2. 关注全体，分层教学
3. 加强互动，活跃气氛

### 作业方面
1. 精选作业，控制数量
2. 及时批改，有效反馈
3. 个别辅导，查漏补缺

### 评价方面
1. 多元评价，全面评估
2. 过程评价，关注发展
3. 激励评价，增强信心

## 教研活动安排
1. **每月一次**: 教学研讨会
2. **每两周一次**: 集体备课
3. **随时进行**: 听课评课
4. **期末**: 教学总结交流

## 预期成果
1. 学生数学成绩稳步提升
2. 学生学习兴趣明显增强
3. 教师教学水平得到提高
4. 形成特色的教学模式

---
*计划制定：${new Date().toLocaleString('zh-CN')}*
*制定人：数学教研组*`;
  }

  /**
   * 生成学期安排表
   */
  generateSemesterSchedule(grade, chapters, totalWeeks) {
    let table = '';
    let week = 1;
    let hourCount = 0;
    
    for (const chapter of chapters) {
      const chapterHours = this.standardHours[grade][chapter];
      const chapterWeeks = Math.ceil(chapterHours / 5);
      
      for (let w = 0; w < chapterWeeks && week <= totalWeeks; w++) {
        const weekNum = week++;
        const weekType = w === 0 ? '新授' : (w === chapterWeeks - 1 ? '复习' : '巩固');
        const activity = w === 0 ? '章节导入' : (w === chapterWeeks - 1 ? '单元测试' : '练习巩固');
        
        table += `| ${chapter} | 第${weekNum}周 | ${chapter}教学 | 5课时 | ${activity} | ${weekType}周 |\n`;
        hourCount += 5;
      }
      
      // 章节之间安排缓冲周
      if (week <= totalWeeks && hourCount < totalWeeks * 5) {
        table += `| 缓冲调整 | 第${week}周 | 习题课/补差 | 5课时 | 知识巩固 | 调整周 |\n`;
        week++;
        hourCount += 5;
      }
    }
    
    // 期末复习
    const reviewWeeks = 2;
    for (let i = 0; i < reviewWeeks && week <= totalWeeks; i++) {
      table += `| 期末复习 | 第${week}周 | 综合复习 | 5课时 | 模拟考试 | 复习周 |\n`;
      week++;
      hourCount += 5;
    }
    
    return table;
  }
}

// 导出模块
module.exports = {
  TeachingPlanGenerator,
  
  // 快捷函数
  generateLesson: (grade, chapter, lessonTitle) => {
    const generator = new TeachingPlanGenerator();
    return generator.generateLessonPlan(grade, chapter, lessonTitle);
  },
  
  generateChapter: (grade, chapter) => {
    const generator = new TeachingPlanGenerator();
    return generator.generateChapterPlan(grade, chapter);
  },
  
  generateSemester: (grade, semester = '上') => {
    const generator = new TeachingPlanGenerator();
    return generator.generateSemesterPlan(grade, semester);
  }
};