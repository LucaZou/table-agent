import os
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Set, Dict

logger = logging.getLogger("file_cleanup_service")

# 获取根目录位置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
IMAGES_DIR = os.path.join(STATIC_DIR, "images")

# 文件访问记录文件路径
ACCESS_RECORD_FILE = os.path.join(BASE_DIR, "file_access_records.txt")

# 文件访问记录：file_id -> 最后访问时间
file_access_records: Dict[str, datetime] = {}

# 会话超时时间（小时）
SESSION_TIMEOUT_HOURS = 2

def load_access_records() -> None:
    """从文件加载访问记录"""
    if os.path.exists(ACCESS_RECORD_FILE):
        try:
            with open(ACCESS_RECORD_FILE, "r") as f:
                for line in f:
                    if line.strip():
                        parts = line.strip().split(",")
                        if len(parts) == 2:
                            file_id, timestamp = parts
                            try:
                                file_access_records[file_id] = datetime.fromisoformat(timestamp)
                            except ValueError:
                                logger.error(f"无效的时间戳格式: {timestamp}")
        except Exception as e:
            logger.error(f"加载文件访问记录时出错: {str(e)}")
            # 如果加载失败，确保记录字典是空的
            file_access_records.clear()
    logger.info(f"已加载 {len(file_access_records)} 条文件访问记录")

def save_access_records() -> None:
    """将访问记录保存到文件"""
    try:
        with open(ACCESS_RECORD_FILE, "w") as f:
            for file_id, timestamp in file_access_records.items():
                f.write(f"{file_id},{timestamp.isoformat()}\n")
        logger.info(f"已保存 {len(file_access_records)} 条文件访问记录")
    except Exception as e:
        logger.error(f"保存文件访问记录时出错: {str(e)}")

def update_file_access(file_id: str) -> None:
    """更新文件的最后访问时间"""
    file_access_records[file_id] = datetime.now()
    save_access_records()  # 保存到文件

def is_file_expired(file_id: str) -> bool:
    """检查文件是否已过期"""
    if file_id not in file_access_records:
        return True
    
    last_access = file_access_records[file_id]
    return datetime.now() - last_access > timedelta(hours=SESSION_TIMEOUT_HOURS)

async def cleanup_expired_files() -> None:
    """清理过期的文件和相关资源"""
    try:
        expired_files: Set[str] = set()
        
        # 检查过期的文件
        for file_id, last_access in file_access_records.copy().items():
            if is_file_expired(file_id):
                expired_files.add(file_id)
                del file_access_records[file_id]
        
        # 清理过期文件
        for file_id in expired_files:
            # 删除上传目录中的原始文件和处理后的文件
            for file_path in Path(UPLOAD_DIR).glob(f"{file_id}*"):
                try:
                    file_path.unlink()
                    logger.info(f"已删除过期文件: {file_path}")
                except Exception as e:
                    logger.error(f"删除文件失败 {file_path}: {str(e)}")
            
            # 删除相关的图表文件
            for image_path in Path(IMAGES_DIR).glob(f"plot_{file_id}*"):
                try:
                    image_path.unlink()
                    logger.info(f"已删除过期图表: {image_path}")
                except Exception as e:
                    logger.error(f"删除图表失败 {image_path}: {str(e)}")
        
        if expired_files:
            logger.info(f"清理了 {len(expired_files)} 个过期文件")
            # 保存更新后的访问记录
            save_access_records()
    
    except Exception as e:
        logger.exception(f"清理过期文件时出错: {str(e)}")

async def start_cleanup_scheduler() -> None:
    """启动定期清理任务"""
    load_access_records()  # 启动时加载记录
    logger.info("文件清理调度器已启动，已加载访问记录")
    while True:
        await cleanup_expired_files()
        # 每小时检查一次
        await asyncio.sleep(3600) 