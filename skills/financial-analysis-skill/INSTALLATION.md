# 安装和配置说明

## 安装依赖

### 1. 安装Python依赖
```bash
pip install pandas numpy matplotlib seaborn
```

### 2. 安装技能
```bash
# 将技能复制到OpenClaw技能目录
cp -r portfolio-analysis ~/.openclaw/skills/
```

## 配置

### 1. 无需配置
**此技能不需要任何配置。**

技能的所有功能都基于本地CSV文件，不需要任何API密钥或网络配置。

### 2. 可选配置
如果需要自定义默认路径，可以修改`optimized_main.py`中的默认路径：

```python
# 修改默认CSV文件路径
parser.add_argument('--csv', type=str, 
                   default=r'C:\Users\wu_zhuoran\.openclaw\workspace\data\marketdata.csv',
                   help='CSV文件路径（包含收益率数据）')
```

## 运行环境

### 1. 网络连接
- ❌ 不需要网络连接
- ❌ 不需要互联网访问
- ❌ 不需要防火墙例外
- ❌ 不需要代理配置

### 2. 系统权限
- ✅ 只需要标准文件系统权限
- ✅ 不需要管理员权限
- ✅ 不需要网络权限
- ✅ 不需要特殊系统权限

### 3. 运行环境
- ✅ 可以在离线环境中运行
- ✅ 可以在隔离网络中运行
- ✅ 可以在沙箱环境中运行
- ✅ 可以在虚拟机中运行

## 数据准备

### 1. CSV文件格式
- 第0行：资产名称（如：CFFEX5五年期国债期货）
- 第1行：数据类型（如：涨跌幅(%)）
- 第2行开始：实际数据
  - 第1列：日期
  - 第2-5列：各资产收益率（百分比格式）

### 2. 示例数据
```
日期,TF.CFE,T.CFE,CU.SHF,AU.SHF
2015-03-20,0.1377,NaN,0.767,-0.1472
2015-03-23,-0.1834,-0.0721,3.9248,1.1373
2015-03-24,-0.0510,-0.1031,0.3662,0.4165
```

### 3. 数据要求
- CSV文件必须包含日期列
- 收益率数据必须为百分比格式（如：1.5表示1.5%）
- 支持处理文本行和缺失值
- 支持处理NaN值

## 运行方法

### 1. 基本使用
```bash
python optimized_main.py --csv "C:\path\to\marketdata.csv" --output ./backtest_output
```

### 2. 使用默认数据路径
```bash
python optimized_main.py
```

### 3. 自定义输出目录
```bash
python optimized_main.py --output ./my_backtest
```

### 4. 查看分析报告
```bash
python optimized_main.py --show-report
```

### 5. 查看分析指标
```bash
python optimized_main.py --show-metrics
```

### 6. 查看资产权重
```bash
python optimized_main.py --show-weights
```

## 输出文件

### 1. 分析报告
- **文件**: `rolling_risk_parity_report.txt`
- **内容**: 投资组合概览、收益分析、风险指标、资产配置、相关性分析、投资建议

### 2. 详细数据
- **文件**: `rolling_risk_parity_data.json`
- **内容**: 投资组合配置、分析指标、资产映射、滚动权重数据

### 3. 可视化图表
1. **收益曲线图**: `rolling_risk_parity_returns.png`
2. **资产配置饼图**: `rolling_risk_parity_allocation.png`
3. **相关性热力图**: `rolling_risk_parity_correlation.png`
4. **资产收益对比图**: `rolling_asset_returns_comparison.png`
5. **滚动权重变化图**: `rolling_weight_changes.png`

## 故障排除

### 1. 文件路径问题
- 确保CSV文件路径正确
- 确保有读取CSV文件的权限
- 确保有写入输出目录的权限

### 2. 数据格式问题
- 确保CSV文件格式正确
- 确保收益率数据为百分比格式
- 确保日期格式正确

### 3. 依赖问题
- 确保已安装所有Python依赖
- 确保Python版本兼容（Python 3.6+）

## 安全说明

### 1. 网络安全
- 技能不进行任何网络请求
- 技能不访问任何外部API
- 技能不上传任何数据到云端
- 技能完全在本地运行

### 2. 数据安全
- 所有数据处理都在本地完成
- 不会上传任何数据到云端
- 不会访问任何外部网络资源
- 不会发送任何网络请求

### 3. 系统安全
- 不需要特殊系统权限
- 不会修改系统文件
- 不会访问敏感系统文件
- 只在指定目录中读写文件

## 最佳实践

### 1. 数据安全
- 使用安全的CSV文件来源
- 定期备份重要数据
- 不要将敏感数据存储在CSV文件中
- 使用加密的文件系统存储数据

### 2. 运行环境
- 在隔离环境中测试技能
- 使用最小权限原则
- 定期审查代码更新
- 监控文件系统访问

### 3. 输出管理
- 定期清理输出目录
- 备份重要的分析结果
- 使用版本控制管理输出文件
- 不要将输出文件存储在敏感目录中

## 技术支持

### 1. 问题报告
- 在项目仓库提交Issue
- 提供详细的错误信息
- 提供运行环境信息
- 提供复现步骤

### 2. 功能请求
- 在项目仓库提交Feature Request
- 提供详细的功能描述
- 提供使用场景说明
- 提供技术实现建议

### 3. 贡献代码
- Fork项目仓库
- 创建功能分支
- 提交Pull Request
- 遵循代码规范

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题，请在项目仓库提交Issue。