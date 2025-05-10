import json
from typing import Any
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
import logging
from dotenv import load_dotenv
import pandas as pd
import numpy as np
# 导入路由和服务
from app.routers import file_router, chat_router
from app.services.file_cleanup_service import start_cleanup_scheduler

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("app")

# 获取应用程序根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
IMAGES_DIR = os.path.join(STATIC_DIR, "images")

# 创建必要的目录
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# 确保Swagger UI文件存在
def ensure_swagger_files_exist():
    """确保Swagger UI所需的文件存在,如果不存在则创建"""
    swagger_html_path = os.path.join(STATIC_DIR, "swagger.html")
    swagger_js_path = os.path.join(STATIC_DIR, "swagger-ui-config.js")
    
    # 创建swagger.html文件（如果不存在）
    if not os.path.exists(swagger_html_path):
        logger.info(f"创建Swagger UI HTML文件: {swagger_html_path}")
        with open(swagger_html_path, "w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <title>AI表格处理工具 - API文档</title>
  <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css" />
  <link rel="icon" type="image/png" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/favicon-32x32.png" sizes="32x32" />
  <link rel="icon" type="image/png" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/favicon-16x16.png" sizes="16x16" />
  <style>
    html {
      box-sizing: border-box;
      overflow: -moz-scrollbars-vertical;
      overflow-y: scroll;
    }
    
    *,
    *:before,
    *:after {
      box-sizing: inherit;
    }
    
    body {
      margin: 0;
      background: #fafafa;
    }
    
    .swagger-ui .topbar {
      background-color: #1d4ed8;
    }
    
    .swagger-ui .info .title {
      color: #1d4ed8;
    }
    
    .swagger-ui .opblock.opblock-post {
      background: rgba(73, 204, 144, 0.1);
      border-color: #49cc90;
    }
    
    .swagger-ui .opblock.opblock-get {
      background: rgba(97, 175, 254, 0.1);
      border-color: #61affe;
    }
    
    .swagger-ui .opblock.opblock-delete {
      background: rgba(249, 62, 62, 0.1);
      border-color: #f93e3e;
    }
    
    .swagger-ui .btn.execute {
      background-color: #1d4ed8;
    }
  </style>
</head>
<body>
  <div id="swagger-ui"></div>
  
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js" charset="UTF-8"></script>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js" charset="UTF-8"></script>
  <script src="/static/swagger-ui-config.js" charset="UTF-8"></script>
</body>
</html>""")
    
    # 创建swagger-ui-config.js文件（如果不存在）
    if not os.path.exists(swagger_js_path):
        logger.info(f"创建Swagger UI配置文件: {swagger_js_path}")
        with open(swagger_js_path, "w", encoding="utf-8") as f:
            f.write("""window.onload = function() {
  // 自定义Swagger UI配置
  const ui = SwaggerUIBundle({
    url: "/api/openapi.json",
    dom_id: '#swagger-ui',
    deepLinking: true,
    presets: [
      SwaggerUIBundle.presets.apis,
      SwaggerUIStandalonePreset
    ],
    plugins: [
      SwaggerUIBundle.plugins.DownloadUrl
    ],
    layout: "StandaloneLayout",
    docExpansion: "list",
    defaultModelsExpandDepth: -1,
    displayRequestDuration: true,
    filter: true,
    syntaxHighlight: {
      activate: true,
      theme: "agate"
    },
    tryItOutEnabled: true
  });

  window.ui = ui;
};""")

# 确保Swagger UI文件存在
ensure_swagger_files_exist()

class CustomJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        def json_safe_default(obj):
            if pd.isna(obj) or obj is pd.NA or obj is None or (isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj))):
                return None
            if isinstance(obj, (pd.Series, pd.DataFrame)):
                return obj.replace({pd.NA: None}).where(pd.notnull, None).to_dict()
            return str(obj)
            
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            default=json_safe_default
        ).encode("utf-8")

# 创建FastAPI应用
app = FastAPI(
    title="AI表格处理工具",
    default_response_class= CustomJSONResponse,  # 设置默认响应类
    description="""
    # AI表格处理工具API
    
    这是一个基于FastAPI构建的表格处理工具,结合了AI能力来处理和分析表格数据。
    
    ## 主要功能
    
    * 上传CSV和Excel文件
    * 预览和处理表格数据
    * 通过AI聊天界面进行数据分析
    * 生成图表和数据可视化
    * 导出处理结果
    
    ## API分组
    
    * **文件操作**: 上传、预览、导出和删除文件
    * **聊天处理**: 通过AI对话分析数据和生成处理结果
    """,
    version="1.0.0",
    docs_url=None,  # 禁用默认的Swagger UI
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制为前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 包含路由
app.include_router(file_router.router)
app.include_router(chat_router.router)

# 配置最大请求体大小
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class LargeRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 将请求体大小限制设置为100MB
        request.scope["max_body_size"] = 100 * 1024 * 1024  # 100MB
        response = await call_next(request)
        return response

app.add_middleware(LargeRequestMiddleware)

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化操作"""
    # 启动文件清理调度器
    import asyncio
    asyncio.create_task(start_cleanup_scheduler())
    logger.info("文件清理调度器已启动")

@app.get("/", tags=["健康检查"], 
         summary="API健康检查", 
         description="返回API状态信息，用于检查服务是否正常运行")
async def root():
    return {"message": "欢迎使用AI表格处理工具API", "status": "running", "version": app.version}

@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """自定义Swagger UI页面"""
    try:
        # 使用已确定的绝对路径
        swagger_file_path = os.path.join(STATIC_DIR, "swagger.html")
        
        if not os.path.exists(swagger_file_path):
            logger.error(f"Swagger UI模板文件不存在: {swagger_file_path}")
            return HTMLResponse(content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>API文档</title>
            </head>
            <body>
                <h1>API文档配置错误</h1>
                <p>自定义Swagger UI文件未找到，路径: {swagger_file_path}</p>
                <p>当前工作目录: {os.getcwd()}</p>
                <p>静态文件目录: {STATIC_DIR}</p>
            </body>
            </html>
            """)
        
        with open(swagger_file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.exception(f"加载Swagger UI模板时出错: {str(e)}")
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>API文档错误</title>
        </head>
        <body>
            <h1>API文档加载错误</h1>
            <p>错误信息: {str(e)}</p>
            <p>当前工作目录: {os.getcwd()}</p>
            <p>静态文件目录: {STATIC_DIR}</p>
        </body>
        </html>
        """)

if __name__ == "__main__":
    import uvicorn
    logger.info(f"应用启动 - 静态文件目录: {STATIC_DIR}")
    logger.info(f"上传文件目录: {UPLOADS_DIR}")
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true",
    ) 