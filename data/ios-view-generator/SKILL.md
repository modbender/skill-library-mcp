---
name: ios-view-generator
description: 从截图生成 Objective-C iOS 视图代码，支持懒加载模式和布局/数据分离。当用户需要：(1) 从截图生成 iOS UI 代码，(2) 生成 Objective-C 视图控制器或视图代码，(3) 创建遵循懒加载规范的 iOS 视图时触发此技能。
---

# iOS View Generator

从截图生成规范的 Objective-C iOS 视图代码。

## 核心规范

### 代码结构
```
#pragma mark - Life Cycle   // 生命周期
#pragma mark - UI           // UI 创建
#pragma mark - Layout         // 布局约束
#pragma mark - Data         // 数据加载
#pragma mark - Event Response // 事件响应
#pragma mark - Lazy Load    // 懒加载
```

### 三大原则
1. **懒加载**: 所有 UI 组件在 getter 中初始化
2. **布局分离**: `setupUI` 只负责 addSubView，`setupConstraints` 负责约束
3. **数据分离**: `loadData` 负责请求，`refreshUI` 负责绑定

## 生成流程

### 步骤 1: 分析截图

使用 image 工具分析用户提供的截图：
- 识别 UI 层级结构
- 提取控件类型、数量、位置
- 估算尺寸和间距

### 步骤 2: 声明属性

```objc
@interface MyViewController ()
@property (nonatomic, strong) UIView *containerView;
@property (nonatomic, strong) UILabel *titleLabel;
// ... 其他属性
@end
```

### 步骤 3: 实现懒加载

每个组件独立 getter：
```objc
- (UILabel *)titleLabel {
    if (!_titleLabel) {
        _titleLabel = [[UILabel alloc] init];
        _titleLabel.font = [UIFont boldSystemFontOfSize:18];
        _titleLabel.textColor = [UIColor blackColor];
    }
    return _titleLabel;
}
```

### 步骤 4: UI 与布局分离

```objc
- (void)setupUI {
    [self.view addSubview:self.containerView];
    [self.containerView addSubview:self.titleLabel];
}

- (void)setupConstraints {
    [self.containerView mas_makeConstraints:^(MASConstraintMaker *make) {
        make.edges.equalTo(self.view).insets(UIEdgeInsetsMake(20, 15, 20, 15));
    }];
}
```

### 步骤 5: 数据加载

```objc
- (void)loadData {
    // 网络请求或本地数据
}

- (void)refreshUI {
    // 数据绑定到视图
    self.titleLabel.text = self.dataModel.title;
}
```

## 参考文档

详见 [objc-view-patterns.md](references/objc-view-patterns.md)：
- 完整代码示例
- 常用 UI 组件初始化模板
- Masonry / 原生 Auto Layout 布局方式

## 注意事项

- 默认使用 Masonry 布局，若无则生成原生 Auto Layout
- 尺寸和间距使用估算值，用户可根据设计稿调整
- 颜色使用系统颜色 (systemBlueColor 等)，便于适配暗色模式
- 图片资源使用占位符名称，用户需自行替换
