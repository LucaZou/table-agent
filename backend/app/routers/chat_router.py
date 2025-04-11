from fastapi import APIRouter, HTTPException, Depends, Body, Path as FastAPIPath
from typing import List, Dict, Any, Optional
import logging
import os
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.models.chat_models import ChatMessage, ChatRequest, ChatResponse, ProcessResult
from app.services.agent_service import get_agent, process_dataframe_with_code
from app.services.file_service import get_file_path_by_id

# 获取根目录位置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
IMAGES_DIR = os.path.join(STATIC_DIR, "images")

router = APIRouter(prefix="/api/chat", tags=["AI聊天分析"])
logger = logging.getLogger("chat_router")

# 确保图片目录存在
os.makedirs(IMAGES_DIR, exist_ok=True)

@router.post(
    "/{file_id}", 
    response_model=ChatResponse,
    summary="AI对话分析数据",
    description="""
    与AI助手对话来分析和处理表格数据。
    
    - 需要提供已上传文件的ID
    - 用户发送消息,系统返回AI回复和可能的处理结果
    - 支持历史消息上下文
    - 可能返回处理后的数据预览和可视化图像
    """,
    response_description="返回AI回复、生成的代码、处理结果和图表URL"
)
async def chat_with_agent(
    file_id: str = FastAPIPath(..., description="要分析的文件ID"),
    request: ChatRequest = Body(..., description="聊天请求,包含用户消息和历史记录"),
):
    """用户与AI聊天以处理表格数据"""
    try:
        # 获取文件路径
        file_path = await get_file_path_by_id(file_id)
        if not file_path:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 读取表格数据获取列名
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:  # Excel
            df = pd.read_excel(file_path)
        
        # 获取表格列名
        columns = df.columns.tolist()
        columns_info = "、".join([f"'{col}'" for col in columns])
        
        # 获取每列的数据类型信息
        dtypes_info = []
        for col in columns:
            dtype = str(df[col].dtype)
            # 添加示例值帮助理解列内容
            sample_values = df[col].dropna().head(3).tolist()
            sample_str = "、".join([f"'{str(val)}'" for val in sample_values]) if sample_values else "无样本"
            dtypes_info.append(f"'{col}': 类型为{dtype}, 示例值: {sample_str}")
        
        columns_dtype_info = "\n".join(dtypes_info)
        
        # 获取Agent
        agent = get_agent()
        
        # 增加系统消息上下文
        system_message = f"""你是一位专业的数据分析师,帮助用户处理表格数据。用户上传的文件为: {os.path.basename(file_path)}。

该表格具有以下列({len(columns)}列):
{columns_info}

各列的数据类型和示例值:
{columns_dtype_info}

当用户模糊指代某一列时,请严格匹配最相关的列名:
- 例如: 用户说"成绩"而实际列名是"中期成绩"或"期末成绩",应使用实际列名"中期成绩"或"期末成绩"
- 例如: 用户说"学生姓名"而实际列名是"姓名",应使用实际列名"姓名"
- 例如: 用户说"销售额"而实际列名是"销售收入",应使用实际列名"销售收入"

请按照以下要求生成Python代码:
1. 使用pandas库处理数据,已经预先导入为df变量
2. 所有处理后的结果必须存储在名为'result'的DataFrame变量中
3. 如果需要可视化,使用matplotlib库(已预先导入为plt)
4. 生成的代码必须可以直接运行,不需要额外的导入语句
5. 代码应简洁且易于理解,添加适当的注释
6. 不要使用可能影响系统安全的操作(如os、subprocess等)
7. 确保使用表格中实际存在的列名,而不是用户描述中可能不准确的名称
8. 如果用户请求的列名不存在,主动给出建议使用哪个相似列名,并在代码中使用正确列名

示例格式:
```python
# 处理数据
result = df.copy()  # 创建一个副本进行操作

# 对特定列进行操作
result['新列'] = result['现有列'] * 2

# 结果必须存储在名为result的DataFrame中
```"""
        
        # 获取历史消息
        history = request.history if request.history else []
        
        # 构建LangChain消息列表
        messages = [SystemMessage(content=system_message)]
        
        # 添加历史消息
        for msg in history:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))
        
        # 添加当前用户消息
        messages.append(HumanMessage(content=request.message))
        
        # 调用AI生成代码
        response = await agent.ainvoke(messages)
        ai_response = response.content
        
        # 提取Python代码
        code_blocks = extract_code_blocks(ai_response)
        python_code = ""
        for block in code_blocks:
            if block.get("language", "").lower() == "python":
                python_code = block.get("code", "")
                break
        
        # 如果找到可执行的Python代码,执行它
        result = None
        image_url = None
        if python_code:
            # 使用已经读取的DataFrame
            # 执行代码并获取结果
            result_df, image_path = await process_dataframe_with_code(df, python_code, file_id)
            
            # 如果有结果DataFrame,转换为字符串表示预览
            if result_df is not None:
                # 处理特殊浮点值
                result_df = result_df.replace([float('inf'), float('-inf')], [None, None])
                
                result = {
                    "success": True,
                    "preview": result_df.head(20).to_dict(orient="records"),
                    "columns": result_df.columns.tolist(),
                    "rows_count": len(result_df)
                }
                
                # 如果生成了图像,提供图像URL
                if image_path:
                    # 将路径转换为URL
                    image_url = f"/static/images/{os.path.basename(image_path)}"
        
        return {
            "response": ai_response,
            "code": python_code if python_code else None,
            "result": result,
            "image_url": image_url
        }
        
    except Exception as e:
        logger.exception(f"处理聊天请求时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理聊天请求失败: {str(e)}")


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """从Markdown文本中提取代码块"""
    blocks = []
    lines = text.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 查找代码块开始
        if line.startswith('```'):
            language = line[3:].strip()
            code_lines = []
            i += 1
            
            # 收集代码块内容直到结束标记
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
                
            # 添加找到的代码块
            if i < len(lines):  # 确保找到了结束标记
                blocks.append({
                    "language": language,
                    "code": '\n'.join(code_lines)
                })
                
        i += 1
        
    return blocks 