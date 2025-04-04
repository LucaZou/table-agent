from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union

class FileResponse(BaseModel):
    """文件上传响应模型"""
    file_id: str
    original_filename: str
    file_path: str

class FilePreviewResponse(BaseModel):
    """文件预览响应模型"""
    columns: List[str]
    data: List[Dict[str, Any]]
    rows_count: int
    file_type: str 