from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union

class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str
    content: str
    
class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    history: Optional[List[ChatMessage]] = None
    
class ProcessResult(BaseModel):
    """数据处理结果模型"""
    success: bool
    preview: Optional[List[Dict[str, Any]]] = None
    columns: Optional[List[str]] = None
    rows_count: Optional[int] = None
    error: Optional[str] = None
    
class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str
    code: Optional[str] = None
    result: Optional[ProcessResult] = None
    image_url: Optional[str] = None 