from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Form, Request, Path as FastAPIPath
from fastapi.responses import JSONResponse, FileResponse as FastAPIFileResponse
import os
import json
import uuid
import pandas as pd
import logging
from typing import List, Optional, Any
from pathlib import Path

from app.models.file_models import FileResponse, FilePreviewResponse
from app.services.file_service import save_upload_file, read_file_preview, export_file
from app.services.file_cleanup_service import update_file_access

# 获取根目录位置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

router = APIRouter(prefix="/api/files", tags=["文件操作"])
logger = logging.getLogger("file_router")

# 确保上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post(
    "/upload", 
    response_model=FileResponse,
    summary="上传表格文件",
    description="""
    上传CSV或Excel格式的表格文件并返回文件ID。
    
    - 支持的文件格式: .csv, .xlsx, .xls
    - 返回唯一的文件ID,用于后续操作
    """,
    response_description="返回文件ID和路径信息"
)
async def upload_file(
    file: UploadFile = File(..., description="要上传的CSV或Excel文件"),
    background_tasks: BackgroundTasks = None
):
    """上传文件并返回唯一ID和预览数据"""
    try:
        # 验证文件类型
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ['.csv', '.xlsx', '.xls']:
            raise HTTPException(status_code=400, detail="仅支持CSV和Excel文件格式(.csv, .xlsx, .xls)")
        
        # 生成唯一文件ID和保存路径
        file_id = str(uuid.uuid4())
        saved_file_path = await save_upload_file(file, file_id, file_extension)
        
        # 更新文件访问记录
        update_file_access(file_id)
        
        response_data = {
            "file_id": file_id,  # 强制转为字符串
            "original_filename": file.filename,
            "file_path": saved_file_path
        }
        logger.debug(f"返回的数据: {response_data}")  # 调试日志
        return response_data
    except ValueError as ve:
        logger.error(f"值错误: {str(ve)}")
        raise HTTPException(status_code=400, detail=f"无效输入: {str(ve)}")
    except Exception as e:
        logger.exception("文件上传失败")
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@router.get(
    "/preview/{file_id}",
    response_model=FilePreviewResponse,
    summary="获取文件预览",
    description="""
    获取已上传文件的预览数据。
    
    - 返回指定行数的数据预览
    - 包含列信息和总行数
    """,
    response_description="返回文件预览数据"
)
async def get_preview(
    file_id: str = FastAPIPath(..., description="文件唯一ID"),
    rows: int = 20
):
    """获取文件预览"""
    try:
        # 更新文件访问记录
        update_file_access(file_id)
        preview_data = await read_file_preview(file_id, rows)
        return preview_data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="文件不存在")
    except Exception as e:
        logger.exception("获取文件预览失败")
        raise HTTPException(status_code=500, detail=f"获取文件预览失败: {str(e)}")

@router.get(
    "/export/{file_id}",
    summary="导出处理结果",
    description="""
    导出已处理的表格数据。
    
    - 支持指定导出文件名
    - 返回文件下载响应
    """,
    response_description="返回文件下载响应"
)
async def export_data(
    file_id: str = FastAPIPath(..., description="文件唯一ID"), 
    filename: Optional[str] = None
):
    """导出已处理的文件"""
    try:
        # 更新文件访问记录
        update_file_access(file_id)
        file_path = await export_file(file_id, filename)
        # 使用FastAPI的FileResponse返回文件下载
        return FastAPIFileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type="application/octet-stream"
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="文件不存在")
    except Exception as e:
        logger.exception("文件导出失败")
        raise HTTPException(status_code=500, detail=f"文件导出失败: {str(e)}")

@router.delete(
    "/{file_id}",
    summary="删除文件",
    description="""
    删除已上传的文件及其相关处理结果。
    
    - 删除文件夹中与file_id相关的所有文件
    """,
    response_description="返回删除操作结果"
)
async def delete_file(file_id: str = FastAPIPath(..., description="要删除的文件唯一ID")):
    """删除上传的文件"""
    try:
        for file_path in Path(UPLOAD_DIR).glob(f"{file_id}*"):
            file_path.unlink()
        return {"message": "文件已删除"}
    except Exception as e:
        logger.exception("文件删除失败")
        raise HTTPException(status_code=500, detail=f"文件删除失败: {str(e)}")