"""
备份文件清理工具
"""

import os
import glob
import re
from pathlib import Path
from typing import List, Dict
from utils.paths import get_storage_path, get_db_path, get_machine_id_path, get_workspace_storage_path


def find_backup_files() -> Dict[str, List[str]]:
    """
    查找所有由程序创建的备份文件
    
    Returns:
        dict: 包含不同类型备份文件的字典
        {
            'storage_backups': List[str],     # storage.json备份文件
            'db_backups': List[str],          # 数据库备份文件
            'machine_id_backups': List[str],  # 机器ID备份文件
            'workspace_backups': List[str]    # 工作区备份文件
        }
    """
    backup_files = {
        'storage_backups': [],
        'db_backups': [],
        'machine_id_backups': [],
        'workspace_backups': []
    }
    
    try:
        # 查找 storage.json 备份文件
        storage_path = get_storage_path()
        if os.path.exists(storage_path):
            storage_dir = os.path.dirname(storage_path)
            storage_filename = os.path.basename(storage_path)
            storage_pattern = os.path.join(storage_dir, f"{storage_filename}.bak.*")
            backup_files['storage_backups'] = glob.glob(storage_pattern)
        
        # 查找数据库备份文件
        db_path = get_db_path()
        if os.path.exists(db_path):
            db_dir = os.path.dirname(db_path)
            db_filename = os.path.basename(db_path)
            db_pattern = os.path.join(db_dir, f"{db_filename}.bak.*")
            backup_files['db_backups'] = glob.glob(db_pattern)
        
        # 查找机器ID备份文件
        machine_id_path = get_machine_id_path()
        if os.path.exists(machine_id_path):
            machine_id_dir = os.path.dirname(machine_id_path)
            machine_id_filename = os.path.basename(machine_id_path)
            machine_id_pattern = os.path.join(machine_id_dir, f"{machine_id_filename}.bak.*")
            backup_files['machine_id_backups'] = glob.glob(machine_id_pattern)
        
        # 查找工作区备份文件
        workspace_path = get_workspace_storage_path()
        if os.path.exists(workspace_path):
            workspace_dir = os.path.dirname(workspace_path)
            workspace_name = os.path.basename(workspace_path)
            # 匹配格式: workspaceStorage_backup_<timestamp>.zip
            workspace_pattern = os.path.join(workspace_dir, f"{workspace_name}_backup_*.zip")
            backup_files['workspace_backups'] = glob.glob(workspace_pattern)
    
    except Exception as e:
        print(f"查找备份文件时出错: {e}")
    
    return backup_files


def get_backup_file_info(file_path: str) -> Dict[str, str]:
    """
    获取备份文件的详细信息
    
    Args:
        file_path (str): 备份文件路径
        
    Returns:
        dict: 文件信息
        {
            'path': str,
            'size': str,
            'created_time': str,
            'type': str
        }
    """
    try:
        stat = os.stat(file_path)
        size_mb = stat.st_size / (1024 * 1024)
        
        # 从文件名提取时间戳
        filename = os.path.basename(file_path)
        timestamp_match = re.search(r'(\d{10})', filename)
        
        if timestamp_match:
            import time
            timestamp = int(timestamp_match.group(1))
            created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        else:
            created_time = "未知"
        
        # 确定文件类型
        if '.zip' in filename:
            file_type = "工作区备份"
        elif 'storage.json' in filename:
            file_type = "存储配置备份"
        elif 'state.vscdb' in filename:
            file_type = "数据库备份"
        elif 'machineid' in filename:
            file_type = "机器ID备份"
        else:
            file_type = "未知类型"
        
        return {
            'path': file_path,
            'size': f"{size_mb:.2f} MB",
            'created_time': created_time,
            'type': file_type
        }
    
    except Exception as e:
        return {
            'path': file_path,
            'size': "未知",
            'created_time': "未知",
            'type': "错误"
        }


def delete_backup_files(file_paths: List[str]) -> Dict[str, any]:
    """
    删除指定的备份文件
    
    Args:
        file_paths (List[str]): 要删除的文件路径列表
        
    Returns:
        dict: 删除结果
        {
            'deleted_count': int,
            'failed_files': List[str],
            'total_size_freed': float  # MB
        }
    """
    deleted_count = 0
    failed_files = []
    total_size_freed = 0.0
    
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                # 获取文件大小
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                
                # 删除文件
                os.remove(file_path)
                deleted_count += 1
                total_size_freed += file_size
            
        except Exception as e:
            failed_files.append(f"{file_path}: {str(e)}")
    
    return {
        'deleted_count': deleted_count,
        'failed_files': failed_files,
        'total_size_freed': total_size_freed
    }


def clean_all_backups() -> Dict[str, any]:
    """
    清理所有备份文件
    
    Returns:
        dict: 清理结果
    """
    # 查找所有备份文件
    backup_files = find_backup_files()
    
    # 收集所有备份文件路径
    all_backup_paths = []
    for file_list in backup_files.values():
        all_backup_paths.extend(file_list)
    
    if not all_backup_paths:
        return {
            'deleted_count': 0,
            'failed_files': [],
            'total_size_freed': 0.0,
            'message': '没有找到备份文件'
        }
    
    # 删除所有备份文件
    result = delete_backup_files(all_backup_paths)
    result['backup_types'] = {
        'storage_backups': len(backup_files['storage_backups']),
        'db_backups': len(backup_files['db_backups']),
        'machine_id_backups': len(backup_files['machine_id_backups']),
        'workspace_backups': len(backup_files['workspace_backups'])
    }
    
    return result


if __name__ == "__main__":
    # 测试功能
    print("查找备份文件...")
    backups = find_backup_files()
    
    total_files = sum(len(files) for files in backups.values())
    print(f"找到 {total_files} 个备份文件:")
    
    for backup_type, files in backups.items():
        if files:
            print(f"\n{backup_type}:")
            for file_path in files:
                info = get_backup_file_info(file_path)
                print(f"  - {info['type']}: {info['size']} ({info['created_time']})")
