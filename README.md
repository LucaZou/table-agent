# AI表格处理工具

基于FastAPI + LangChain + OpenAI API + Vue的AI表格处理工具，用于智能化处理和分析表格数据。

## 功能特点

- 支持上传CSV、Excel等表格文件并提供预览
- 通过聊天窗口用自然语言描述表格处理需求
- AI自动生成处理代码并执行
- 实时显示处理结果和数据可视化
- 支持下载处理后的文件

## 项目结构

```
.
├── backend/                # 后端API目录
│   ├── app/                # 应用代码
│   │   ├── models/         # 数据模型
│   │   ├── routers/        # API路由
│   │   ├── services/       # 业务服务
│   │   └── main.py         # 主应用入口
│   ├── static/             # 静态资源
│   │   └── images/         # 生成的图表
│   ├── uploads/            # 上传的文件
│   ├── .env.example        # 环境变量示例
│   ├── requirements.txt    # Python依赖
│   └── run.py              # 启动脚本
│
└── frontend/               # 前端Vue应用
    ├── src/                # 源代码
    ├── public/             # 公共资源
    └── package.json        # 项目配置
```

## 快速开始

### 后端设置

1. 创建并激活虚拟环境:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

2. 安装依赖:
```bash
pip install -r requirements.txt
```

3. 创建`.env`文件并设置OpenAI API密钥:
```
OPENAI_API_KEY=your_api_key_here
DEBUG=True
```

4. 启动后端服务:
```bash
python run.py
```

### 前端设置

1. 安装依赖:
```bash
cd frontend
npm install
```

2. 启动开发服务器:
```bash
npm run serve
```

3. 构建生产版本:
```bash
npm run build
```

## API说明

### 文件管理

- `POST /api/files/upload` - 上传表格文件
- `GET /api/files/preview/{file_id}` - 预览文件内容
- `GET /api/files/export/{file_id}` - 导出处理后的文件
- `DELETE /api/files/{file_id}` - 删除文件

### 聊天处理

- `POST /api/chat/{file_id}` - 与AI交互处理表格数据

## 技术栈

- **后端**: FastAPI, LangChain, Pandas, Matplotlib
- **AI**: OpenAI API
- **前端**: Vue 3, Axios, Element Plus
- **数据处理**: Pandas, Matplotlib

## 贡献

欢迎贡献代码、报告问题或提出改进建议！ 