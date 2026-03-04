#!/usr/bin/env python3
"""
QingLong CRM 数据提取
版本: 1.0
类型: CRM 数据提取
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime


class QingLongCRMExtractor:
    """QingLong CRM 数据提取器"""
    
    def __init__(self):
        self.login_url = None
        self.phone_number = None
        self.password = None
        
        # 输出文件路径
        self.output_text_file = "/home/admin/page_text.txt"
        self.output_html_file = "/home/admin/page_html.html"
        self.output_data_file = "/home/admin/crm_data.json"
        
        # 浏览器配置
        self.browser_args = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage'
        ]
    
    def config(self, login_url=None, phone_number=None, password=None, 
              output_text=None, output_html=None, output_data=None):
        """配置提取器"""
        if login_url:
            self.login_url = login_url
        if phone_number:
            self.phone_number = phone_number
        if password:
            self.password = password
        if output_text:
            self.output_text_file = output_text
        if output_html:
            self.output_html_file = output_html
        if output_data:
            self.output_data_file = output_data
        
        print("=" * 60)
        print("QingLong CRM 数据提取 - 配置")
        print("=" * 60)
        print(f"登录 URL: {self.login_url or '待配置'}")
        print(f"手机号: {self.phone_number or '待配置'}")
        print(f"密码: {'*' * len(self.password) if self.password else '待配置'}")
        print(f"输出文件:")
        print(f"  - 文本: {self.output_text_file}")
        print(f"  - HTML: {self.output_html_file}")
        print(f"  - 数据: {self.output_data_file}")
        print("=" * 60)
        print()
    
    async def extract(self):
        """执行数据提取"""
        
        if not all([self.login_url, self.phone_number, self.password]):
            print("❌ 错误: 请先配置登录信息（URL、手机号、密码）")
            return {
                'status': 'error',
                'message': '配置信息不完整',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        print("=" * 60)
        print("QingLong CRM 数据提取 - 开始执行")
        print("=" * 60)
        print()
        
        result = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'unknown',
            'login': {},
            'data': {},
            'errors': []
        }
        
        async with async_playwright() as p:
            # 启动浏览器
            print("🚀 启动浏览器...")
            browser = await p.chromium.launch(
                headless=True,
                args=self.browser_args
            )
            page = await browser.new_page()
            
            # 访问登录页面
            print("🌐 访问登录页面...")
            try:
                await page.goto(self.login_url, wait_until='domcontentloaded', timeout=60000)
                await asyncio.sleep(3)
                print("✓ 登录页面访问成功")
            except Exception as e:
                error_msg = f"访问登录页面失败: {e}"
                print(f"❌ {error_msg}")
                result['errors'].append(error_msg)
                result['status'] = 'error'
                await browser.close()
                return result
            
            # 切换到账号登录
            print("🔄 切换到账号登录...")
            try:
                account_tab = await page.wait_for_selector('li.fssdk-tab-item:has-text("Account")', timeout=10000)
                await account_tab.click()
                print("✓ 已切换到账号登录")
                await asyncio.sleep(5)
            except Exception as e:
                error_msg = f"切换账号登录失败: {e}"
                print(f"❌ {error_msg}")
                result['errors'].append(error_msg)
            
            # 填写手机号
            print("📱 填写手机号...")
            try:
                phone_input = await page.wait_for_selector('.fssdk-phone-mobile-value', timeout=5000)
                await phone_input.fill(self.phone_number)
                print(f"✓ 手机号已填写: {self.phone_number}")
            except Exception as e:
                error_msg = f"填写手机号失败: {e}"
                print(f"❌ {error_msg}")
                result['errors'].append(error_msg)
                await browser.close()
                return result
            
            await asyncio.sleep(1)
            
            # 填写密码
            print("🔐 填写密码...")
            try:
                password_input = await page.wait_for_selector('input[placeholder*="password"], .fssdk-phone-password-value', timeout=5000)
                await password_input.fill(self.password)
                print("✓ 密码已填写")
            except Exception as e:
                error_msg = f"填写密码失败: {e}"
                print(f"❌ {error_msg}")
                result['errors'].append(error_msg)
                await browser.close()
                return result
            
            await asyncio.sleep(2)
            
            # 点击登录按钮
            print("🔘 点击登录按钮...")
            try:
                login_button = await page.wait_for_selector('.fssdk-form-btn-primary:has-text("Log in")', timeout=5000)
                await login_button.click()
                print("✓ 登录按钮已点击")
            except Exception as e:
                error_msg = f"点击登录按钮失败: {e}"
                print(f"❌ {error_msg}")
                result['errors'].append(error_msg)
                await browser.close()
                return result
            
            # 等待协议弹窗
            print("⏳ 等待协议弹窗出现（3秒）...")
            await asyncio.sleep(3)
            
            # 点击同意按钮
            print("📋 查找协议确认弹窗...")
            try:
                agree_selectors = [
                    'button:has-text("Agree And Login")',
                    'button:has-text("Agree")',
                    'button:has-text("同意")',
                    '.fssdk-confirm__btns-item:has-text("Agree")',
                ]
                
                for selector in agree_selectors:
                    try:
                        agree_btn = await page.wait_for_selector(selector, timeout=3000)
                        if await agree_btn.is_visible():
                            await agree_btn.click()
                            print(f"✓ 已点击同意按钮: {selector}")
                            await asyncio.sleep(3)
                            break
                    except:
                        continue
                else:
                    print("⚠️  未找到协议确认弹窗")
            except Exception as e:
                error_msg = f"处理协议确认失败: {e}"
                print(f"⚠️  {error_msg}")
                result['errors'].append(error_msg)
            
            # 等待登录完成
            print("⏳ 等待登录完成（20秒）...")
            await asyncio.sleep(20)
            
            # 检查登录状态
            print("🔍 检查登录状态...")
            page_title = await page.title()
            current_url = page.url
            
            result['login']['title'] = page_title
            result['login']['url'] = current_url
            result['login']['success'] = 'Login' not in page_title and 'login' not in current_url and 'proj/page/login' not in current_url
            
            if result['login']['success']:
                print("✅✅✅ 登录成功！✅✅✅")
                print(f"   页面标题: {page_title}")
                print(f"   当前 URL: {current_url}")
            else:
                print("❌ 登录失败")
                print(f"   页面标题: {page_title}")
                print(f"   当前 URL: {current_url}")
                result['status'] = 'error'
            
            # 提取页面文本
            print("\n📝 提取页面文本...")
            try:
                page_text = await page.evaluate('''() => {
                    return document.body.innerText;
                }''')
                
                with open(self.output_text_file, 'w', encoding='utf-8') as f:
                    f.write(page_text)
                print(f"✓ 页面文本已保存: {self.output_text_file}")
                
                result['data']['page_text'] = page_text
            except Exception as e:
                error_msg = f"提取页面文本失败: {e}"
                print(f"❌ {error_msg}")
                result['errors'].append(error_msg)
            
            # 保存页面 HTML
            print("\n📄 保存页面 HTML...")
            try:
                page_html = await page.content()
                with open(self.output_html_file, 'w', encoding='utf-8') as f:
                    f.write(page_html)
                print(f"✓ 页面 HTML 已保存: {self.output_html_file}")
            except Exception as e:
                error_msg = f"保存页面 HTML 失败: {e}"
                print(f"❌ {error_msg}")
                result['errors'].append(error_msg)
            
            # 提取业务数据
            print("\n🔍 提取业务数据...")
            
            # 提取基础信息
            result['data']['basic'] = {
                'title': page_title,
                'url': current_url
            }
            
            # 分析页面文本提取业务数据
            text_lines = page_text.split('\n')
            
            # 提取客户信息
            print("   🔍 提取客户信息...")
            customers = self._extract_customers(page_text)
            result['data']['customers'] = customers
            print(f"   ✓ 提取到 {len(customers)} 个客户")
            
            # 提取待办事项
            print("   🔍 提取待办事项...")
            todos = self._extract_todos(page_text)
            result['data']['todos'] = todos
            print(f"   ✓ 提取到 {len(todos)} 个待办")
            
            # 提取销售数据
            print("   🔍 提取销售数据...")
            sales = self._extract_sales(page_text)
            result['data']['sales'] = sales
            print("   ✓ 提取销售数据完成")
            
            # 保存结构化数据
            print("\n💾 保存结构化数据...")
            try:
                with open(self.output_data_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"✓ 数据已保存: {self.output_data_file}")
            except Exception as e:
                error_msg = f"保存数据失败: {e}"
                print(f"❌ {error_msg}")
                result['errors'].append(error_msg)
            
            await browser.close()
            
            if not result['errors']:
                result['status'] = 'success'
            else:
                result['status'] = 'partial_success'
            
            return result
    
    def _extract_customers(self, page_text):
        """提取客户信息"""
        customers = []
        
        # 从文本中提取客户相关信息
        lines = page_text.split('\n')
        
        # 查找包含关键词的行
        keywords = ['待处理人', '关联数据', '商机名称', '项目名称']
        customer_set = set()
        
        for line in lines:
            line = line.strip()
            if line and any(keyword in line for keyword in keywords):
                try:
                    # 简单的客户名称提取
                    if '待处理人:' in line or '关联数据:' in line:
                        parts = line.split('・')
                        if len(parts) >= 2:
                            customer_name = parts[1].strip()
                            if customer_name and customer_name not in customer_set:
                                customer_set.add(customer_name)
                                customers.append({
                                    'name': customer_name,
                                    'line': line
                                })
                except:
                    continue
        
        return customers
    
    def _extract_todos(self, page_text):
        """提取待办事项"""
        todos = []
        
        lines = page_text.split('\n')
        
        # 查找待办事项
        todo_keywords = ['待处理的阶段任务', '名称:', '待处理人:', '关联对象:']
        
        for line in lines:
            line = line.strip()
            if line and any(keyword in line for keyword in todo_keywords):
                try:
                    todo = {
                        'text': line,
                        'details': line.split('・') if '・' in line else [line]
                    }
                    todos.append(todo)
                except:
                    continue
        
        return todos
    
    def _extract_sales(self, page_text):
        """提取销售数据"""
        sales = {
            'new_customers': 0,
            'new_contacts': 0,
            'new_opportunities': 0,
            'stage_changes': 0,
            'follow_ups': 0,
            'total_opportunity_amount': 0,
            'leads': {
                'total': 0,
                'conversion_rate': 0
            }
        }
        
        lines = page_text.split('\n')
        
        # 提取数字数据
        import re
        
        for line in lines:
            line = line.strip()
            
            # 提取新增客户
            if '新增客户' in line:
                match = re.search(r'(\d+)个', line)
                if match:
                    sales['new_customers'] = int(match.group(1))
            
            # 提取新增联系人
            elif '新增联系人' in line:
                match = re.search(r'(\d+)个', line)
                if match:
                    sales['new_contacts'] = int(match.group(1))
            
            # 提取新增商机
            elif '新增商机' in line:
                match = re.search(r'(\d+)个', line)
                if match:
                    sales['new_opportunities'] = int(match.group(1))
            
            # 提取阶段变化
            elif '阶段变化的商机' in line:
                match = re.search(r'(\d+)个', line)
                if match:
                    sales['stage_changes'] = int(match.group(1))
            
            # 提取新增跟进
            elif '新增跟进动态' in line:
                match = re.search(r'(\d+)个', line)
                if match:
                    sales['follow_ups'] = int(match.group(1))
            
            # 提取商机金额
            elif '商机金额的总计' in line:
                match = re.search(r'([\d,.]+)', line)
                if match:
                    sales['total_opportunity_amount'] = match.group(1)
            
            # 提取线索
            elif '线索总数' in line:
                match = re.search(r'(\d+)个', line)
                if match:
                    sales['leads']['total'] = int(match.group(1))
            
            # 提取转化率
            elif '转化率为' in line:
                match = re.search(r'(\d+\.\d+)%', line)
                if match:
                    sales['leads']['conversion_rate'] = match.group(1)
        
        return sales


async def main():
    """主函数"""
    
    extractor = QingLongCRMExtractor()
    
    # 配置（使用前请修改这些值）
    extractor.config(
        login_url="https://your-crm-system.com/login",
        phone_number="your-phone-number",
        password="your-password"
    )
    
    # 执行提取
    result = await extractor.extract()
    
    # 输出结果
    print("\n" + "=" * 60)
    print("QingLong CRM 数据提取 - 执行结果")
    print("=" * 60)
    print(f"\n状态: {result['status']}")
    print(f"时间戳: {result['timestamp']}")
    print(f"登录成功: {'是' if result['login'].get('success') else '否'}")
    print(f"提取客户数: {len(result['data'].get('customers', []))}")
    print(f"提取待办数: {len(result['data'].get('todos', []))}")
    
    if result['errors']:
        print(f"\n错误 ({len(result['errors'])} 个):")
        for error in result['errors']:
            print(f"  - {error}")
    
    print("\n" + "=" * 60)
    print("输出文件:")
    print("=" * 60)
    print(f"- 文本: {extractor.output_text_file}")
    print(f"- HTML: {extractor.output_html_file}")
    print(f"- 数据: {extractor.output_data_file}")
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    result = asyncio.run(main())
