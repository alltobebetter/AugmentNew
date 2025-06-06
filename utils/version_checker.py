"""
版本检查工具
"""

import requests
import re
from typing import Tuple, Optional


# 当前版本
CURRENT_VERSION = "1.0.0"

# 版本检查URL
VERSION_URL = "https://raw.githubusercontent.com/alltobebetter/AugmentNew/main/version.txt"


def parse_version(version_str: str) -> Tuple[int, int, int]:
    """
    解析版本字符串为元组
    
    Args:
        version_str (str): 版本字符串，如 "1.0.0"
        
    Returns:
        Tuple[int, int, int]: 版本元组 (major, minor, patch)
    """
    # 清理版本字符串，移除可能的前缀和后缀
    version_str = version_str.strip()
    
    # 使用正则表达式提取版本号
    match = re.search(r'(\d+)\.(\d+)\.(\d+)', version_str)
    if match:
        return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
    else:
        raise ValueError(f"无效的版本格式: {version_str}")


def compare_versions(version1: str, version2: str) -> int:
    """
    比较两个版本
    
    Args:
        version1 (str): 第一个版本
        version2 (str): 第二个版本
        
    Returns:
        int: -1 如果 version1 < version2
             0 如果 version1 == version2
             1 如果 version1 > version2
    """
    try:
        v1 = parse_version(version1)
        v2 = parse_version(version2)
        
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0
    except ValueError as e:
        raise ValueError(f"版本比较失败: {e}")


def check_for_updates(timeout: int = 10) -> dict:
    """
    检查是否有新版本可用
    
    Args:
        timeout (int): 请求超时时间（秒）
        
    Returns:
        dict: 检查结果
        {
            'has_update': bool,
            'current_version': str,
            'latest_version': str,
            'error': str or None
        }
    """
    result = {
        'has_update': False,
        'current_version': CURRENT_VERSION,
        'latest_version': None,
        'error': None
    }
    
    try:
        # 获取远程版本信息
        response = requests.get(VERSION_URL, timeout=timeout)
        response.raise_for_status()
        
        # 解析版本信息
        latest_version = response.text.strip()
        result['latest_version'] = latest_version
        
        # 比较版本
        comparison = compare_versions(CURRENT_VERSION, latest_version)
        result['has_update'] = comparison < 0  # 当前版本小于最新版本
        
    except requests.exceptions.RequestException as e:
        result['error'] = f"网络请求失败: {str(e)}"
    except ValueError as e:
        result['error'] = f"版本解析失败: {str(e)}"
    except Exception as e:
        result['error'] = f"检查更新失败: {str(e)}"
    
    return result


def get_current_version() -> str:
    """
    获取当前版本
    
    Returns:
        str: 当前版本号
    """
    return CURRENT_VERSION


def get_update_url() -> str:
    """
    获取更新下载链接
    
    Returns:
        str: GitHub releases页面URL
    """
    return "https://github.com/alltobebetter/AugmentNew/releases/latest"


if __name__ == "__main__":
    # 测试版本检查功能
    print(f"当前版本: {get_current_version()}")
    print("检查更新中...")
    
    result = check_for_updates()
    
    if result['error']:
        print(f"检查失败: {result['error']}")
    else:
        print(f"最新版本: {result['latest_version']}")
        if result['has_update']:
            print("🎉 发现新版本！")
        else:
            print("✅ 已是最新版本")
