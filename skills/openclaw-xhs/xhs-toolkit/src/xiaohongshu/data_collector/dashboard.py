#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仪表板数据采集模块
采集笔记总览数据，支持7天和30天两个维度
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .utils import (
    clean_number, wait_for_element, extract_text_safely, 
    find_element_by_selectors, wait_for_page_load, wait_for_dashboard_data
)
from src.utils.logger import get_logger
from src.data.storage_manager import get_storage_manager

logger = get_logger(__name__)

def collect_dashboard_data(driver, save_data=True):
    """
    采集仪表板数据，包括笔记总览数据
    支持7天和30天两个维度
    """
    logger.info("开始采集仪表板数据...")
    
    try:
        # 导航到仪表板页面
        driver.get("https://creator.xiaohongshu.com/new/home")
        wait_for_page_load(driver)
        
        # 等待数据加载
        wait_for_dashboard_data(driver)
        
        # 采集多维度数据
        all_data = []
        
        # 采集7天数据
        logger.info("开始采集7天维度数据...")
        seven_day_data = _collect_dimension_data(driver, "7天")
        if seven_day_data:
            all_data.append(seven_day_data)
            logger.info(f"✅ 7天数据采集成功: 观看{seven_day_data.get('views', 0)}, 点赞{seven_day_data.get('likes', 0)}")
        else:
            logger.error("❌ 7天数据采集失败")
        
        # 切换到30天维度并采集数据
        logger.info("开始切换到30天维度...")
        if _switch_to_30day_dimension(driver):
            logger.info("30天维度切换成功，开始采集30天数据...")
            thirty_day_data = _collect_dimension_data(driver, "30天")
            if thirty_day_data:
                all_data.append(thirty_day_data)
                logger.info(f"✅ 30天数据采集成功: 观看{thirty_day_data.get('views', 0)}, 点赞{thirty_day_data.get('likes', 0)}")
                
                # 比较7天和30天数据
                if seven_day_data and thirty_day_data:
                    if (seven_day_data.get('views') == thirty_day_data.get('views') and 
                        seven_day_data.get('likes') == thirty_day_data.get('likes')):
                        logger.info("ℹ️ 7天和30天数据相同，这可能是正常的（账号最近才活跃）")
                    else:
                        logger.info("ℹ️ 7天和30天数据不同，数据采集正常")
            else:
                logger.error("❌ 30天数据采集失败")
        else:
            logger.error("❌ 30天维度切换失败，只保存7天数据")
        
        # 保存数据
        if save_data and all_data:
            storage_manager = get_storage_manager()
            storage_manager.save_dashboard_data(all_data)
            logger.info(f"✅ 仪表板数据保存成功，共保存 {len(all_data)} 个维度的数据")
        
        return {
            "success": True,
            "data": all_data,
            "message": f"成功采集 {len(all_data)} 个维度的仪表板数据"
        }
        
    except Exception as e:
        logger.error(f"❌ 仪表板数据采集失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": []
        }

def _collect_dimension_data(driver, dimension):
    """采集指定维度的数据"""
    logger.info(f"采集{dimension}维度数据...")
    
    try:
        # 等待数据加载完成
        time.sleep(3)
        
        # 采集笔记总览数据
        overview_data = _collect_overview_data(driver)
        
        # 合并数据
        dashboard_data = {
            "dimension": dimension,
            "timestamp": time.time(),
            **overview_data
        }
        
        logger.info(f"✅ {dimension}维度数据采集完成")
        return dashboard_data
        
    except Exception as e:
        logger.error(f"❌ {dimension}维度数据采集失败: {e}")
        return None

def _collect_overview_data(driver):
    """采集笔记总览数据"""
    overview_data = {
        "views": 0,
        "likes": 0,
        "collects": 0,
        "comments": 0,
        "shares": 0,
        "interactions": 0
    }
    
    try:
        # 查找包含数字的元素，通过上下文判断数据类型
        elements = driver.find_elements(By.XPATH, "//*[text()]")
        
        for elem in elements:
            try:
                text = elem.text.strip()
                if text and text.isdigit():
                    value = int(text)
                    parent = elem.find_element(By.XPATH, "..")
                    context = parent.text.strip()
                    
                    # 根据上下文判断数据类型
                    if "观看" in context or "浏览" in context:
                        overview_data["views"] = value
                    elif "点赞" in context:
                        overview_data["likes"] = value
                    elif "收藏" in context:
                        overview_data["collects"] = value
                    elif "评论" in context:
                        overview_data["comments"] = value
                    elif "分享" in context:
                        overview_data["shares"] = value
                    elif "互动" in context:
                        overview_data["interactions"] = value
                        
            except Exception as e:
                continue
        
        logger.info(f"笔记总览数据: {overview_data}")
        return overview_data
        
    except Exception as e:
        logger.error(f"采集笔记总览数据失败: {e}")
        return overview_data

def _switch_to_30day_dimension(driver):
    """切换到30天维度"""
    try:
        logger.info("尝试切换到30天维度...")
        
        # 多种选择器尝试
        selectors = [
            "//*[text()='近30日']",  # 基于Playwright验证的正确选择器
            "//button[contains(text(), '近30日')]",
            "//span[contains(text(), '近30日')]",
            ".btn:contains('近30日')",
            "[class*='btn'][text*='近30日']"
        ]
        
        for selector in selectors:
            try:
                if selector.startswith("//") or selector.startswith("//*"):
                    # XPath选择器
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    # CSS选择器
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    element = elements[0]
                    logger.info(f"找到30天按钮，使用选择器: {selector}")
                    
                    # 滚动到元素可见
                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(1)
                    
                    # 点击元素
                    element.click()
                    logger.info("✅ 成功点击30天按钮")
                    
                    # 等待数据更新
                    time.sleep(3)
                    return True
                    
            except Exception as e:
                logger.debug(f"选择器 {selector} 失败: {e}")
                continue
        
        logger.error("❌ 未找到30天按钮")
        return False
        
    except Exception as e:
        logger.error(f"❌ 切换到30天维度失败: {e}")
        return False 