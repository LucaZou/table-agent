import os
import logging
import sys
import traceback
import uuid
import pandas as pd
import matplotlib.pyplot as plt
import asyncio
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from io import StringIO
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger("agent_service")

# 加载环境变量
load_dotenv()

# 获取根目录位置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
IMAGES_DIR = os.path.join(STATIC_DIR, "images")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# 确保目录存在
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 线程池执行器，用于运行代码
executor = ThreadPoolExecutor(max_workers=2)

def get_agent():
    """初始化并返回LangChain代理"""
    try:
        # 从环境变量中获取API密钥
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("未找到DeepSeek API密钥,请在.env文件中设置OPENAI_API_KEY")
        
        # 获取API基础URL
        base_url = os.getenv("OPENAI_API_BASE", "https://api.deepseek.com")
        
        # 初始化DeepSeek聊天模型 (使用OpenAI兼容接口)
        llm = ChatOpenAI(
            api_key=api_key,
            model="deepseek-chat",  # 使用DeepSeek-V3模型
            temperature=0.2,
            timeout=60.0,
            base_url=base_url
        )
        
        return llm
        
    except Exception as e:
        logger.exception("初始化AI代理失败")
        raise e

def _execute_code_in_thread(df: pd.DataFrame, code: str) -> Tuple[Optional[pd.DataFrame], Optional[str], Optional[str]]:
    """在单独的线程中执行代码"""
    # 函数内部的重定向和代码执行
    result_df = None
    error_message = None
    image_path = None
    
    # 保存原始的标准输出和标准错误
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    # 创建字符串IO对象捕获输出
    stdout_capture = StringIO()
    stderr_capture = StringIO()
    
    try:
        # 重定向标准输出和标准错误
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture
        
        # 创建本地环境执行用户代码
        local_env = {"df": df.copy(), "pd": pd, "plt": plt}
        
        # 执行代码
        exec(code, local_env)
        
        # 检查本地环境中是否有处理后的DataFrame
        if "result" in local_env and isinstance(local_env["result"], pd.DataFrame):
            result_df = local_env["result"]
        
        # 检查是否有图表生成
        if plt.get_fignums():
            # 生成唯一的图像文件名
            image_name = f"plot_{uuid.uuid4()}.png"
            image_path = os.path.join(IMAGES_DIR, image_name)
            
            # 保存图表
            plt.savefig(image_path)
            plt.close('all')  # 关闭所有图表
    
    except Exception as e:
        error_message = f"代码执行错误: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_message)
    
    finally:
        # 恢复标准输出和标准错误
        sys.stdout = original_stdout
        sys.stderr = original_stderr
    
    return result_df, image_path, error_message

async def process_dataframe_with_code(df: pd.DataFrame, code: str, file_id: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """使用生成的代码处理DataFrame并返回结果和可能的图像路径"""
    try:
        # 使用线程池执行代码
        loop = asyncio.get_event_loop()
        result_df, image_path, error = await loop.run_in_executor(
            executor, 
            _execute_code_in_thread, 
            df, 
            code
        )
        
        if error:
            logger.error(f"代码执行错误: {error}")
            return None, None
        
        # 如果有结果DataFrame，保存处理后的文件
        if result_df is not None:
            # 处理特殊浮点值，避免JSON序列化问题
            result_df = result_df.replace([float('inf'), float('-inf'), np.inf, -np.inf], None)
            result_df = result_df.where(pd.notnull(result_df), None)
            
            # 确定文件类型并保存
            original_file_path = await get_file_path_by_id(file_id)
            if original_file_path:
                file_ext = os.path.splitext(original_file_path)[1]
                processed_file_path = os.path.join(UPLOAD_DIR, f"{file_id}_processed{file_ext}")
                
                if file_ext.lower() == '.csv':
                    result_df.to_csv(processed_file_path, index=False)
                else:
                    result_df.to_excel(processed_file_path, index=False)
                
                logger.info(f"处理后的文件已保存: {processed_file_path}")
        
        return result_df, image_path
        
    except Exception as e:
        logger.exception("处理DataFrame时发生错误")
        return None, None

async def get_file_path_by_id(file_id: str) -> Optional[str]:
    """通过文件ID查找文件路径"""
    # 导入这里以避免循环导入
    from app.services.file_service import get_file_path_by_id as get_path
    return await get_path(file_id) 