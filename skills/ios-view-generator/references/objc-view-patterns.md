# Objective-C 视图代码规范

## 目录结构

```objc
#pragma mark - Life Cycle

#pragma mark - UI

#pragma mark - Layout

#pragma mark - Data

#pragma mark - Event Response

#pragma mark - Private Methods
```

---

## 懒加载模式

所有 UI 组件使用懒加载 (getter 方法) 初始化：

```objc
// .h 文件
@interface MyViewController : UIViewController

@end

// .m 文件
@interface MyViewController ()

@property (nonatomic, strong) UIView *headerView;
@property (nonatomic, strong) UILabel *titleLabel;
@property (nonatomic, strong) UIButton *actionButton;
@property (nonatomic, strong) UITableView *tableView;

@end

@implementation MyViewController

#pragma mark - Life Cycle

- (void)viewDidLoad {
    [super viewDidLoad];
    [self setupUI];
    [self setupConstraints];
    [self loadData];
}

- (void)viewDidLayoutSubviews {
    [super viewDidLayoutSubviews];
    // 布局调整
}

#pragma mark - UI

- (void)setupUI {
    self.view.backgroundColor = [UIColor whiteColor];
    
    [self.view addSubview:self.headerView];
    [self.headerView addSubview:self.titleLabel];
    [self.view addSubview:self.actionButton];
    [self.view addSubview:self.tableView];
}

#pragma mark - Layout

- (void)setupConstraints {
    // 使用 Masonry 或原生 Auto Layout
    [self.headerView mas_makeConstraints:^(MASConstraintMaker *make) {
        make.top.left.right.equalTo(self.view);
        make.height.mas_equalTo(100);
    }];
    
    [self.titleLabel mas_makeConstraints:^(MASConstraintMaker *make) {
        make.center.equalTo(self.headerView);
    }];
    
    [self.actionButton mas_makeConstraints:^(MASConstraintMaker *make) {
        make.top.equalTo(self.headerView.mas_bottom).offset(20);
        make.centerX.equalTo(self.view);
        make.size.mas_equalTo(CGSizeMake(200, 44));
    }];
    
    [self.tableView mas_makeConstraints:^(MASConstraintMaker *make) {
        make.top.equalTo(self.actionButton.mas_bottom).offset(10);
        make.left.right.bottom.equalTo(self.view);
    }];
}

#pragma mark - Data

- (void)loadData {
    // 网络请求或数据加载
}

- (void)refreshUI {
    // 数据绑定到 UI
}

#pragma mark - Event Response

- (void)actionButtonTapped:(UIButton *)sender {
    // 按钮点击事件
}

#pragma mark - Lazy Load

- (UIView *)headerView {
    if (!_headerView) {
        _headerView = [[UIView alloc] init];
        _headerView.backgroundColor = [UIColor systemBlueColor];
    }
    return _headerView;
}

- (UILabel *)titleLabel {
    if (!_titleLabel) {
        _titleLabel = [[UILabel alloc] init];
        _titleLabel.text = @"Title";
        _titleLabel.font = [UIFont boldSystemFontOfSize:18];
        _titleLabel.textColor = [UIColor whiteColor];
        _titleLabel.textAlignment = NSTextAlignmentCenter;
    }
    return _titleLabel;
}

- (UIButton *)actionButton {
    if (!_actionButton) {
        _actionButton = [UIButton buttonWithType:UIButtonTypeSystem];
        [_actionButton setTitle:@"Action" forState:UIControlStateNormal];
        [_actionButton addTarget:self action:@selector(actionButtonTapped:) forControlEvents:UIControlEventTouchUpInside];
    }
    return _actionButton;
}

- (UITableView *)tableView {
    if (!_tableView) {
        _tableView = [[UITableView alloc] initWithFrame:CGRectZero style:UITableViewStylePlain];
        _tableView.delegate = self;
        _tableView.dataSource = self;
        _tableView.separatorStyle = UITableViewCellSeparatorStyleSingleLine;
    }
    return _tableView;
}

@end
```

---

## 常用 UI 组件初始化

### UILabel
```objc
- (UILabel *)descLabel {
    if (!_descLabel) {
        _descLabel = [[UILabel alloc] init];
        _descLabel.font = [UIFont systemFontOfSize:14];
        _descLabel.textColor = [UIColor darkGrayColor];
        _descLabel.numberOfLines = 0;
        _descLabel.textAlignment = NSTextAlignmentLeft;
    }
    return _descLabel;
}
```

### UIButton
```objc
- (UIButton *)submitBtn {
    if (!_submitBtn) {
        _submitBtn = [UIButton buttonWithType:UIButtonTypeSystem];
        [_submitBtn setTitle:@"Submit" forState:UIControlStateNormal];
        _submitBtn.titleLabel.font = [UIFont boldSystemFontOfSize:16];
        [_submitBtn setTitleColor:[UIColor whiteColor] forState:UIControlStateNormal];
        _submitBtn.backgroundColor = [UIColor systemBlueColor];
        _submitBtn.layer.cornerRadius = 8;
        _submitBtn.clipsToBounds = YES;
        [_submitBtn addTarget:self action:@selector(submitBtnTapped:) forControlEvents:UIControlEventTouchUpInside];
    }
    return _submitBtn;
}
```

### UIImageView
```objc
- (UIImageView *)avatarImageView {
    if (!_avatarImageView) {
        _avatarImageView = [[UIImageView alloc] init];
        _avatarImageView.contentMode = UIViewContentModeScaleAspectFill;
        _avatarImageView.clipsToBounds = YES;
        _avatarImageView.layer.cornerRadius = 25;
        _avatarImageView.backgroundColor = [UIColor lightGrayColor];
    }
    return _avatarImageView;
}
```

### UITextField
```objc
- (UITextField *)inputField {
    if (!_inputField) {
        _inputField = [[UITextField alloc] init];
        _inputField.placeholder = @"Enter text...";
        _inputField.borderStyle = UITextBorderStyleRoundedRect;
        _inputField.font = [UIFont systemFontOfSize:14];
        _inputField.delegate = self;
    }
    return _inputField;
}
```

### UIScrollView
```objc
- (UIScrollView *)scrollView {
    if (!_scrollView) {
        _scrollView = [[UIScrollView alloc] init];
        _scrollView.showsVerticalScrollIndicator = YES;
        _scrollView.showsHorizontalScrollIndicator = NO;
        _scrollView.bounces = YES;
    }
    return _scrollView;
}
```

---

## 布局方式

### 方式一：Masonry (推荐)

```objc
// Podfile
pod 'Masonry'

// 使用
[view mas_makeConstraints:^(MASConstraintMaker *make) {
    make.top.equalTo(superview).offset(10);
    make.left.right.equalTo(superview).insets(UIEdgeInsetsMake(0, 15, 0, 15));
    make.height.mas_equalTo(44);
}];
```

### 方式二：原生 Auto Layout

```objc
[view setTranslatesAutoresizingMaskIntoConstraints:NO];
[NSLayoutConstraint activateConstraints:@[
    [view.topAnchor constraintEqualToAnchor:superview.topAnchor constant:10],
    [view.leadingAnchor constraintEqualToAnchor:superview.leadingAnchor constant:15],
    [view.trailingAnchor constraintEqualToAnchor:superview.trailingAnchor constant:-15],
    [view.heightAnchor constraintEqualToConstant:44]
]];
```

---

## 从截图生成代码的流程

1. **识别 UI 层级结构**
   - 分析截图中的视图层次
   - 识别容器视图和子视图关系

2. **提取 UI 元素**
   - 识别控件类型 (Label, Button, ImageView, TextField 等)
   - 估算尺寸和间距
   - 识别颜色和字体样式

3. **生成代码**
   - 创建属性声明
   - 实现懒加载方法
   - 设置 UI 和布局方法
   - 添加事件响应方法

4. **优化调整**
   - 确保布局适配不同屏幕尺寸
   - 使用合理的默认值
