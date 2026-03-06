# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Code Formatter - Formats generated code and creates complete strategy files.
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path



class CodeFormatter:
    """Formats generated strategy code and creates complete files."""
    
    def __init__(self):
        """Initialize code formatter."""
        pass
    
    def generate(self, template, strategy_info, output_dir, session_id=None):
        """
        Generate complete strategy files from template.
        
        Args:
            template: Template dictionary
            strategy_info: Strategy information from prompt parser
            output_dir: Output directory for generated files
            session_id: Optional session ID for organizing files
            
        Returns:
            List of generated file information dictionaries
        """
        generated_files = []
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate strategy name
        strategy_name = self._generate_strategy_name(strategy_info)
        
        # Add session info to strategy info
        if session_id:
            strategy_info['session_id'] = session_id
        
        # 1. Generate main strategy file
        strategy_file = self._generate_strategy_file(
            template=template,
            strategy_info=strategy_info,
            strategy_name=strategy_name,
            output_dir=output_path,
            session_id=session_id
        )
        generated_files.append(strategy_file)
        
        # 2. Generate configuration file
        config_file = self._generate_config_file(
            strategy_info=strategy_info,
            strategy_name=strategy_name,
            output_dir=output_path,
            session_id=session_id
        )
        generated_files.append(config_file)
        
        # 3. Generate requirements file
        requirements_file = self._generate_requirements_file(
            output_dir=output_path,
            session_id=session_id
        )
        generated_files.append(requirements_file)
        
        # 4. Generate usage instructions
        instructions_file = self._generate_instructions_file(
            strategy_info=strategy_info,
            strategy_name=strategy_name,
            output_dir=output_path,
            session_id=session_id
        )
        generated_files.append(instructions_file)
        
        # 5. Validate and fix generated code
        self._validate_and_fix_generated_code(generated_files)
        
        return generated_files
    
    def _validate_and_fix_generated_code(self, generated_files):
        """Validate and fix generated Python files"""
        try:
            # Import validator
            from code_validator import CodeValidator
            
            validator = CodeValidator()
            
            for file_info in generated_files:
                if file_info['type'] == 'strategy':
                    print("🔍 Validating generated code...")
                    result = validator.validate_and_fix(file_info['path'])
                    
                    if result['valid']:
                        print("✅ Code validation passed")
                        if result.get('changes'):
                            print("   Changes made: {}".format(', '.join(result['changes'])))
                    else:
                        print("⚠️  Code validation failed")
                        for error in result.get('errors', []):
                            print("   Error: {}".format(error))
                        
                        # Try to provide helpful suggestions
                        self._suggest_fixes(result, file_info['path'])
                        
        except ImportError:
            print("⚠️  Code validator not available, skipping validation")
        except Exception as e:
            print("⚠️  Validation failed: {}".format(e))
    
    def _suggest_fixes(self, validation_result, filepath):
        """Suggest fixes for validation errors"""
        errors = validation_result.get('errors', [])
        filepath = Path(filepath)
        
        if not errors:
            return
        
        print("\n🔧 Suggested fixes:")
        
        for error in errors:
            if 'List' in error or 'Dict' in error or 'typing' in error:
                print("  - Add typing import: Add 'from typing import List, Dict, Optional' at the top")
                
                # Read the file
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Check if we should add the import
                lines = content.split('\n')
                imports_added = False
                
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        # Add typing import after other imports
                        lines.insert(i + 1, 'from typing import List, Dict, Optional')
                        imports_added = True
                        break
                
                if not imports_added:
                    # Add at the beginning
                    lines.insert(0, 'from typing import List, Dict, Optional')
                
                # Write back
                with open(filepath, 'w') as f:
                    f.write('\n'.join(lines))
                
                print("    ✅ Added typing import")
            
            elif 'sys.path' in error or 'api_wrappers' in error:
                print("  - Add sys.path modification for api_wrappers")
                
                with open(filepath, 'r') as f:
                    content = f.read()
                
                lines = content.split('\n')
                
                # Find where to add imports
                import_section_end = 0
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        import_section_end = i + 1
                
                # Add necessary imports
                if 'import sys' not in content:
                    lines.insert(import_section_end, 'import sys')
                    import_section_end += 1
                
                if '' not in content:
                    lines.insert(import_section_end, '')
                    import_section_end += 1
                
                # Add sys.path modification
                path_line = 'sys.path.insert(0, str(Path(__file__).parent.parent / "api_wrappers"))'
                lines.insert(import_section_end, path_line)
                
                with open(filepath, 'w') as f:
                    f.write('\n'.join(lines))
                
                print("    ✅ Added sys.path modification")
            
            elif 'encoding' in error.lower():
                print("  - Add encoding declaration")
                
                with open(filepath, 'r') as f:
                    content = f.read()
                
                lines = content.split('\n')
                if lines[0].startswith('#!'):
                    lines.insert(1, '# -*- coding: utf-8 -*-')
                else:
                    lines.insert(0, '# -*- coding: utf-8 -*-')
                
                with open(filepath, 'w') as f:
                    f.write('\n'.join(lines))
                
                print("    ✅ Added encoding declaration")
    
    def _generate_strategy_name(self, strategy_info):
        """Generate strategy name from strategy info."""
        symbol = strategy_info.get('symbol', 'UNKNOWN').lower()
        strategy_type = strategy_info.get('type', 'strategy')
        
        # Clean up strategy type for filename
        strategy_type_clean = re.sub(r'[^a-z0-9]', '_', strategy_type)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return "{symbol}_{strategy_type_clean}_{timestamp}"
    
    def _generate_strategy_file(self, template, strategy_info, 
                               strategy_name, output_dir: Path, 
                               session_id=None):
        """Generate main strategy Python file."""
        # Get template content
        template_content = template.get('content', '')
        
        # Replace template variables
        formatted_content = self._replace_template_variables(
            content=template_content,
            strategy_info=strategy_info,
            strategy_name=strategy_name,
            session_id=session_id
        )
        
        # Add header comment
        header = self._generate_file_header(strategy_info, strategy_name, session_id)
        formatted_content = header + formatted_content
        
        # Write to file
        filename = f"{strategy_name}.py"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        
        # Make file executable
        os.chmod(filepath, 0o755)
        
        return {
            'path': str(filepath),
            'type': 'strategy',
            'description': '主策略Python文件'
        }
    
    def _replace_template_variables(self, content, strategy_info, 
                                   strategy_name, session_id=None):
        """Replace template variables with actual values."""
        # Basic replacements
        replacements = {
            '{{STRATEGY_NAME}}': strategy_name,
            '{{SYMBOL}}': strategy_info.get('symbol', 'HYPE'),
            '{{STRATEGY_TYPE}}': strategy_info.get('type', 'grid_trading'),
            '{{TIMESTAMP}}': datetime.now().isoformat(),
            '{{GENERATOR}}': 'VibeTrading Code Generator'
        }
        
        # Add session ID if provided
        if session_id:
            replacements['{{SESSION_ID}}'] = session_id
        
        # Add parameter replacements
        parameters = strategy_info.get('parameters', {})
        for key, value in parameters.items():
            placeholder = f'{{{{{key.upper()}}}}}'
            if isinstance(value, (list, tuple)):
                replacements[placeholder] = str(value)
            else:
                replacements[placeholder] = str(value)
        
        # Perform replacements
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        
        # Special handling for configuration
        if '{{CONFIG_DICT}}' in content:
            config_dict = self._create_config_dict(strategy_info)
            content = content.replace('{{CONFIG_DICT}}', json.dumps(config_dict, indent=4))
        
        return content
    
    def _create_config_dict(self, strategy_info):
        """Create configuration dictionary from strategy info."""
        config = {
            'strategy': {
                'name': strategy_info.get('name', '未命名策略'),
                'type': strategy_info.get('type', 'basic'),
                'symbol': strategy_info.get('symbol', 'HYPE'),
                'generated_at': datetime.now().isoformat()
            },
            'parameters': strategy_info.get('parameters', {}),
            'risk_management': strategy_info.get('risk_preferences', {
                'stop_loss': 0.05,
                'take_profit': 0.10,
                'position_size': 0.01,
                'max_drawdown': 0.20
            })
        }
        
        # Add timeframe if specified
        timeframe = strategy_info.get('timeframe', '1h')
        config['strategy']['timeframe'] = timeframe
        
        # Add tags if any
        tags = strategy_info.get('tags', [])
        if tags:
            config['strategy']['tags'] = tags
        
        return config
    
    def _generate_file_header(self, strategy_info, strategy_name, session_id=None):
        """Generate file header comment."""
        symbol = strategy_info.get('symbol', 'HYPE')
        strategy_type = strategy_info.get('type', 'grid_trading')
        
        # Simple header without complex formatting issues
        header_lines = [
            '#!/usr/bin/env python3',
            '# -*- coding: utf-8 -*-',
            '"""',
            f'{symbol.upper()} {strategy_type.replace("_", " ").title()} Strategy',
            'Generated by VibeTrading Code Generator',
            '',
            f'策略名称: {strategy_name}',
            f'交易品种: {symbol}',
            f'策略类型: {strategy_type}',
            f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        ]
        
        # Add session ID if provided
        if session_id:
            header_lines.append(f'Session ID: {session_id}')
        
        header_lines.extend([
            '',
            '策略描述:',
            self._generate_strategy_description(strategy_info),
            '',
            '风险提示:',
            '1. 请在模拟交易中充分测试本策略',
            '2. 使用小资金开始实盘交易',
            '3. 设置合理的止损和仓位管理',
            '4. 定期监控策略性能',
            '5. 加密货币交易具有高风险，可能损失全部资金',
            '',
            '免责声明:',
            '本代码由AI生成，仅供参考。用户需自行承担使用风险。',
            '过去表现不代表未来结果。请谨慎交易。',
            '"""',
            ''
        ])
        
        return '\n'.join(header_lines)
    
    def _generate_strategy_description(self, strategy_info):
        """Generate strategy description from strategy info."""
        symbol = strategy_info.get('symbol', 'HYPE')
        strategy_type = strategy_info.get('type', 'grid_trading')
        params = strategy_info.get('parameters', {})
        
        descriptions = {
            'grid_trading': "网格交易策略，在指定价格区间内自动放置买入和卖出订单。",
            'rsi': "RSI指标交易策略，根据RSI超买超卖信号进行交易。",
            'macd': "MACD指标交易策略，根据MACD金叉死叉信号进行交易。",
            'moving_average': "移动平均线策略，根据均线交叉信号进行交易。",
            'signal_based': "信号驱动策略，根据外部交易信号进行交易。",
            'basic': "基础交易策略，执行简单的买入卖出逻辑。"
        }
        
        description = descriptions.get(strategy_type, "自动交易策略")
        
        # Add parameter details
        if params:
            param_desc = []
            for key, value in params.items():
                if key == 'price_range' and isinstance(value, list):
                    param_desc.append("价格区间: ${value[0]} - ${value[1]}")
                elif key == 'grid_count':
                    param_desc.append("网格数量: {value}")
                elif key == 'grid_size':
                    param_desc.append("网格大小: {value}")
                elif key == 'oversold_threshold':
                    param_desc.append("RSI超卖阈值: {value}")
                elif key == 'overbought_threshold':
                    param_desc.append("RSI超买阈值: {value}")
            
            if param_desc:
                description += "\n\n参数配置:\n" + "\n".join("  • {p}" for p in param_desc)
        
        return description
    
    def _generate_config_file(self, strategy_info, strategy_name, 
                             output_dir: Path, session_id=None):
        """Generate configuration JSON file."""
        config_dict = self._create_config_dict(strategy_info)
        
        # Add session info to config
        if session_id:
            config_dict['session'] = {
                'id': session_id,
                'created_at': datetime.now().isoformat()
            }
        
        filename = f"{strategy_name}_config.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        
        return {
            'path': str(filepath),
            'type': 'config',
            'description': '策略配置文件 (JSON格式)'
        }
    
    def _generate_requirements_file(self, output_dir: Path, session_id=None):
        """Generate requirements.txt file."""
        # Use template requirements file
        template_path = Path(__file__).parent.parent / "config_templates" / "requirements.txt"
        
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                requirements = f.read()
        else:
            # Fallback requirements
            requirements = """# Hyperliquid Trading Strategy Dependencies
# Generated by VibeTrading Code Generator

# Core dependencies
requests>=2.28.0
pandas>=1.5.0
numpy>=1.24.0

# Optional: For advanced features
# ta-lib>=0.4.0  # Technical analysis library
# python-telegram-bot>=20.0  # For Telegram notifications
"""
        
        # Add session info comment
        if session_id:
            requirements = f"# Session ID: {session_id}\n# Generated: {datetime.now().isoformat()}\n\n" + requirements
        
        filename = "requirements.txt"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(requirements)
        
        return {
            'path': str(filepath),
            'type': 'requirements',
            'description': 'Python依赖包列表'
        }
    
    def _generate_instructions_file(self, strategy_info, strategy_name,
                                   output_dir: Path, session_id=None):
        """Generate usage instructions file."""
        symbol = strategy_info.get('symbol', 'HYPE')
        strategy_type = strategy_info.get('type', 'grid_trading')
        
        # Build instructions with session info
        session_info = ""
        if session_id:
            session_info = f"- **Session ID**: {session_id}\n"
        
        instructions = f'''# {symbol.upper()} {strategy_type.replace('_', ' ').title()} Strategy
# 使用说明

## 策略信息
- **策略名称**: {strategy_name}
- **交易品种**: {symbol}
- **策略类型**: {strategy_type}
{session_info}- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 快速开始

### 1. 环境设置
```bash
# 设置环境变量（必需）
export HYPERLIQUID_API_KEY="你的API密钥"
export HYPERLIQUID_ACCOUNT_ADDRESS="你的账户地址"

# 可选：设置Telegram通知
export TELEGRAM_BOT_TOKEN="你的Telegram机器人令牌"
export TELEGRAM_CHAT_ID="你的聊天ID"
```

### 2. 安装依赖
```bash
# 安装Python依赖
pip install -r requirements.txt

# 如果需要技术分析库（可选）
# pip install TA-Lib
```

### 3. 运行策略
```bash
# 运行主策略文件
python {strategy_name}.py

# 或使用配置文件
python {strategy_name}.py --config {strategy_name}_config.json
```

### 4. 监控策略
- 查看实时日志输出
- 检查 logs/ 目录下的日志文件
- 查看 status/ 目录下的状态文件
- 设置Telegram通知（如配置）

## Session目录结构

{session_id and f"本策略属于Session: `{session_id}`\n\n文件组织:\n```\nsessions/{session_id}/\n├── strategies/     # 策略文件 (当前目录)\n├── backtest_results/ # 回测结果\n├── logs/          # 日志文件\n└── configs/       # 配置文件\n```\n" or ""}

## 配置文件说明

主要配置文件：`{strategy_name}_config.json`

### 关键参数
{self._generate_config_instructions(strategy_info)}

### 修改配置
1. 编辑 `{strategy_name}_config.json` 文件
2. 修改参数值
3. 重启策略以应用更改

## 风险管理

### 建议设置
1. **初始资金**: 使用小资金测试（建议 < $100）
2. **仓位管理**: 单次交易不超过总资金的1-2%
3. **止损设置**: 建议设置5-10%的止损
4. **监控频率**: 至少每天检查一次策略状态

### 风险控制
- 策略包含基本的错误处理
- 自动取消未成交订单
- 价格超出范围时自动重新平衡
- 定期记录策略状态

## 故障排除

### 常见问题

#### 1. API连接失败
- 检查环境变量是否正确设置
- 验证API密钥是否有交易权限
- 检查网络连接

#### 2. 订单未执行
- 检查账户余额是否充足
- 验证交易对符号是否正确
- 检查价格是否在合理范围内

#### 3. 策略性能问题
- 调整检查间隔（check_interval）
- 优化网格参数（价格区间、网格数量）
- 考虑市场流动性

### 日志文件
{session_id and f"- 主日志: `sessions/{session_id}/logs/grid_trading_{{symbol}}_*.log`" or "- 主日志: `logs/grid_trading_{symbol}_*.log`"}
- 错误日志: 查看Python异常输出
{session_id and f"- 回测结果: `sessions/{session_id}/backtest_results/`" or "- 回测结果: `backtest_results/`"}

## 高级功能

### 自定义修改
1. 编辑 `{strategy_name}.py` 文件
2. 修改交易逻辑部分
3. 添加新的风险管理规则
4. 集成其他数据源

### 集成VibeTrading信号
如需集成VibeTrading交易信号：
1. 安装VibeTrading Python包
2. 在策略中添加信号获取逻辑
3. 根据信号调整交易决策

## 支持与更新

### 获取帮助
- 查看生成的代码注释
- 参考模板文件中的示例
- 查阅Hyperliquid API文档

### 策略更新
定期检查以下更新：
1. API库版本更新
2. 市场条件变化
3. 风险管理最佳实践
4. 性能优化建议

## 重要提醒

⚠️ **风险警告**
- 加密货币交易具有极高风险
- 可能损失全部投资资金
- 过去表现不代表未来结果
- 仅使用可承受损失的资金进行交易

✅ **最佳实践**
- 在模拟环境中充分测试
- 从小资金开始逐步增加
- 设置严格的止损规则
- 定期审查和优化策略

---
*本使用说明由VibeTrading Code Generator自动生成*
*最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
'''
        
        filename = f"{strategy_name}_instructions.md"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        return {
            'path': str(filepath),
            'type': 'instructions',
            'description': '详细的使用说明文档'
        }
    
    def _generate_config_instructions(self, strategy_info):
        """Generate configuration instructions based on strategy type."""
        strategy_type = strategy_info.get('type', 'grid_trading')
        params = strategy_info.get('parameters', {})
        
        instructions = ""
        
        if strategy_type == 'grid_trading':
            instructions = '''
- **symbol**: 交易品种 (如: HYPE, BTC, ETH)
- **lower_bound**: 网格下限价格
- **upper_bound**: 网格上限价格  
- **grid_count**: 网格数量
- **grid_size**: 每个网格的交易数量
- **check_interval**: 检查间隔（秒）
- **stop_loss**: 止损比例（如: 0.05 表示5%）
- **take_profit**: 止盈比例（如: 0.10 表示10%）
'''
        elif strategy_type == 'rsi':
            instructions = '''
- **symbol**: 交易品种
- **rsi_period**: RSI计算周期（默认: 14）
- **oversold_threshold**: 超卖阈值（默认: 30）
- **overbought_threshold**: 超买阈值（默认: 70）
- **position_size**: 每次交易仓位大小
- **timeframe**: 时间框架（如: 1h, 4h, 1d）
'''
        
        # Add actual parameter values if available
        if params:
            instructions += "\n### 当前参数值\n"
            for key, value in params.items():
                instructions += "- **{key}**: {value}\n"
        
        return instructions