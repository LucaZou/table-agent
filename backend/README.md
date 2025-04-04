# AI表格处理工具 - 后端服务

这是AI表格处理工具的后端服务，基于FastAPI构建，提供表格数据处理、AI分析和可视化功能。

## 功能概述

- **文件上传与管理**：支持CSV和Excel文件的上传、预览和导出
- **AI驱动的数据分析**：通过对话式界面分析表格数据
- **数据可视化**：自动生成数据图表和可视化展示
- **API文档**：完整的Swagger/OpenAPI接口文档

## 技术栈

- Python 3.9+
- FastAPI
- LangChain
- Pandas
- Matplotlib
- DeepSeek API (AI模型服务)

## 安装部署

### 前置条件

- Python 3.9+
- 虚拟环境工具 (如venv或conda)
- DeepSeek API密钥

### 本地开发环境设置

1. **克隆代码库**

```bash
git clone https://github.com/LucaZou/table-agent-backend-repo.git
cd table_processor/backend
```

2. **创建并激活虚拟环境**

```bash
# 使用venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 或使用conda
conda create -n table_processor python=3.9
conda activate table_processor
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

4. **环境变量配置**

创建`.env`文件并设置必要的环境变量：

```
HOST=0.0.0.0
PORT=8000
DEBUG=True
DEEPSEEK_API_KEY=your_api_key_here
```

5. **启动开发服务器**

```bash
python -m app.main
```

服务将在 http://localhost:8000 启动，API文档可通过 http://localhost:8000/api/docs 访问。

### 生产环境部署

#### 使用Docker部署

1. **构建Docker镜像**

```bash
docker build -t table-processor-backend .
```

2. **运行容器**

```bash
docker run -d \
  --name table-processor-backend \
  -p 8000:8000 \
  -e DEEPSEEK_API_KEY=your_api_key_here \
  -e DEBUG=False \
  table-processor-backend
```

#### 使用Gunicorn部署（非Docker方式）

1. **安装Gunicorn**

```bash
pip install gunicorn
```

2. **启动服务**

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## API文档

API文档可通过以下URL访问：

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- OpenAPI JSON: http://localhost:8000/api/openapi.json

### 主要API端点

#### 文件操作

- `POST /api/files/upload` - 上传表格文件
- `GET /api/files/preview/{file_id}` - 获取文件预览
- `GET /api/files/export/{file_id}` - 导出处理后的文件
- `DELETE /api/files/{file_id}` - 删除文件

#### AI对话分析

- `POST /api/chat/{file_id}` - 与AI对话分析数据

## 数据存储

上传的文件存储在`uploads`目录中，生成的图表图像存储在`static/images`目录中。
在生产环境中，建议配置永久性存储解决方案。

## 配置选项

系统支持以下环境变量配置：

| 变量名 | 说明 | 默认值 |
| ----- | --- | ----- |
| HOST | 服务监听主机 | 0.0.0.0 |
| PORT | 服务监听端口 | 8000 |
| DEBUG | 调试模式开关 | False |
| DEEPSEEK_API_KEY | DeepSeek API密钥 | 无 |

## 许可证

[MIT](LICENSE)

## 联系方式

如有任何问题或建议，请通过[项目Issues](https://github.com/yourusername/table_processor/issues)联系我们。 