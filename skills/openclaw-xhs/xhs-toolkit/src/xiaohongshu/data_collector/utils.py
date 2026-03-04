"""
数据采集通用工具模块

提供数据清洗、元素等待、文本提取等通用功能
"""

import time
import re
from typing import Optional, List, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from ...utils.logger import get_logger

logger = get_logger(__name__)


def clean_number(text: str) -> int:
    """
    清洗数字文本，转换为标准数值
    
    Args:
        text: 包含数字的文本，可能包含"万"、"千"等单位
        
    Returns:
        转换后的整数值
    """
    if not text:
        return 0
    
    text = text.strip()
    if not text:
        return 0
    
    # 跳过特殊文本，避免无意义的警告
    skip_texts = ['详情数据', '详情', '-', '暂无数据', '无数据', '查看详情', '点击查看']
    if any(skip_text in text for skip_text in skip_texts):
        return 0
    
    # 移除非数字字符（除了小数点、万、千）
    cleaned = re.sub(r'[^\d.万千]', '', text)
    
    # 如果清洗后没有数字，直接返回0
    if not cleaned or cleaned in ['.', '万', '千']:
        return 0
    
    try:
        if cleaned.endswith('万'):
            return int(float(cleaned[:-1]) * 10000)
        elif cleaned.endswith('千'):
            return int(float(cleaned[:-1]) * 1000)
        else:
            return int(float(cleaned)) if '.' in cleaned else int(cleaned)
    except (ValueError, TypeError):
        # 只对真正的数字解析失败才记录警告
        if any(char.isdigit() for char in text):
            logger.warning(f"无法解析数字: {text}")
        return 0


def wait_for_element(driver: WebDriver, selector: str, timeout: int = 10, 
                    by: By = By.CSS_SELECTOR) -> Optional[WebElement]:
    """
    等待元素出现并返回
    
    Args:
        driver: WebDriver实例
        selector: 元素选择器
        timeout: 超时时间（秒）
        by: 选择器类型
        
    Returns:
        找到的元素，如果超时则返回None
    """
    try:
        wait = WebDriverWait(driver, timeout)
        element = wait.until(EC.presence_of_element_located((by, selector)))
        return element
    except TimeoutException:
        logger.warning(f"等待元素超时: {selector}")
        return None


def wait_for_elements(driver: WebDriver, selector: str, timeout: int = 10,
                     by: By = By.CSS_SELECTOR) -> List[WebElement]:
    """
    等待多个元素出现并返回
    
    Args:
        driver: WebDriver实例
        selector: 元素选择器
        timeout: 超时时间（秒）
        by: 选择器类型
        
    Returns:
        找到的元素列表
    """
    try:
        wait = WebDriverWait(driver, timeout)
        elements = wait.until(EC.presence_of_all_elements_located((by, selector)))
        return elements
    except TimeoutException:
        logger.warning(f"等待元素列表超时: {selector}")
        return []


def extract_text_safely(element: WebElement) -> str:
    """
    安全地提取元素文本
    
    Args:
        element: WebElement实例
        
    Returns:
        元素的文本内容，如果提取失败返回空字符串
    """
    try:
        if element and element.is_displayed():
            return element.text.strip()
    except Exception as e:
        logger.warning(f"提取元素文本失败: {e}")
    return ""


def find_element_by_selectors(driver: WebDriver, selectors: List[str], 
                             timeout: int = 5) -> Optional[WebElement]:
    """
    尝试多个选择器查找元素
    
    Args:
        driver: WebDriver实例
        selectors: 选择器列表
        timeout: 每个选择器的超时时间
        
    Returns:
        找到的第一个元素，如果都没找到返回None
    """
    for selector in selectors:
        element = wait_for_element(driver, selector, timeout)
        if element and element.is_displayed():
            logger.debug(f"找到元素: {selector}")
            return element
    
    logger.warning(f"所有选择器都未找到元素: {selectors}")
    return None


def scroll_to_element(driver: WebDriver, element: WebElement) -> None:
    """
    滚动到指定元素
    
    Args:
        driver: WebDriver实例
        element: 目标元素
    """
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(1)  # 等待滚动完成
    except Exception as e:
        logger.warning(f"滚动到元素失败: {e}")


def wait_for_page_load(driver: WebDriver, timeout: int = 30) -> bool:
    """
    等待页面加载完成
    
    Args:
        driver: WebDriver实例
        timeout: 超时时间（秒）
        
    Returns:
        是否加载完成
    """
    try:
        wait = WebDriverWait(driver, timeout)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        return True
    except TimeoutException:
        logger.warning("页面加载超时")
        return False


def wait_for_data_load(driver: WebDriver, data_selectors: List[str], timeout: int = 30) -> bool:
    """
    等待页面数据加载完成
    
    Args:
        driver: WebDriver实例
        data_selectors: 数据元素选择器列表
        timeout: 超时时间（秒）
        
    Returns:
        是否有数据加载完成
    """
    try:
        wait = WebDriverWait(driver, timeout)
        
        # 等待页面基本加载完成
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        
        # 等待数据元素出现且包含有效内容
        def data_loaded(driver):
            for selector in data_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = extract_text_safely(element)
                        if text and text.strip() and text.strip() != '0' and text.strip() != '-':
                            logger.debug(f"检测到有效数据: {selector} = {text}")
                            return True
                except Exception:
                    continue
            return False
        
        # 等待有效数据出现，最多等待timeout秒
        wait.until(data_loaded)
        logger.info("✅ 页面数据加载完成")
        return True
        
    except TimeoutException:
        logger.warning("⚠️ 等待数据加载超时，继续尝试采集")
        return False


def wait_for_dashboard_data(driver: WebDriver, timeout: int = 30) -> bool:
    """
    等待仪表板数据加载完成
    
    Args:
        driver: WebDriver实例
        timeout: 超时时间（秒）
        
    Returns:
        是否加载完成
    """
    dashboard_selectors = [
        '.numerical',  # 基础数据
        '.number',     # 详细数据
        '.fans-current'  # 当前粉丝数
    ]
    return wait_for_data_load(driver, dashboard_selectors, timeout)


def wait_for_fans_data(driver: WebDriver, timeout: int = 30) -> bool:
    """
    等待粉丝数据加载完成
    
    Args:
        driver: WebDriver实例
        timeout: 超时时间（秒）
        
    Returns:
        是否加载完成
    """
    fans_selectors = [
        '.con',        # 总粉丝数
        'b',           # 互动数据
        "[class*='fan']",  # 粉丝相关元素
    ]
    return wait_for_data_load(driver, fans_selectors, timeout)


def extract_numbers_from_elements(elements: List[WebElement]) -> List[int]:
    """
    从元素列表中提取数字
    
    Args:
        elements: WebElement列表
        
    Returns:
        提取到的数字列表
    """
    numbers = []
    for element in elements:
        text = extract_text_safely(element)
        if text:
            number = clean_number(text)
            if number > 0:
                numbers.append(number)
    return numbers


def safe_click(element: WebElement, max_retries: int = 3) -> bool:
    """
    安全地点击元素，带重试机制
    
    Args:
        element: 要点击的元素
        max_retries: 最大重试次数
        
    Returns:
        是否点击成功
    """
    for attempt in range(max_retries):
        try:
            if element.is_displayed() and element.is_enabled():
                element.click()
                return True
        except Exception as e:
            logger.warning(f"点击元素失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            time.sleep(1)
    
    return False


def get_element_attribute_safely(element: WebElement, attribute: str) -> str:
    """
    安全地获取元素属性
    
    Args:
        element: WebElement实例
        attribute: 属性名
        
    Returns:
        属性值，如果获取失败返回空字符串
    """
    try:
        if element:
            return element.get_attribute(attribute) or ""
    except Exception as e:
        logger.warning(f"获取元素属性失败: {e}")
    return "" 