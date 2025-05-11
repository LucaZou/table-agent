# U-Agent: CSV 数据分析智能助手

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg) 一个允许用户上传 CSV/XLSX 文件并通过自然语言聊天界面与之交互，进行数据查询和分析的 Web 应用程序。

## ✨ 功能特性

* **CSV 文件上传**: 方便地上传本地 CSV /XLSX 数据文件。
* **聊天式数据查询**: 通过类似聊天的界面，使用自然语言提问关于已上传数据的问题。
* **智能数据分析**: 后端 Agent 利用数据处理库（如 Pandas）理解问题并从 CSV 中提取或计算答案。
* **API 接口**: 基于 FastAPI 构建的健壮后端 API，提供清晰的接口文档 (Swagger UI)。
* **响应式前端**: 基于 Vue.js 构建的现代化、用户友好的界面。
* **容器化部署**: 使用 Docker 和 Docker Compose 提供一致的开发和生产环境。
* **自动化部署脚本**: 简化在不同操作系统上的部署流程。
* **文件管理**:  包含对上传文件的生命周期管理，自动清理文件。

## 🚀 技术栈

* **后端**: Python, FastAPI, Pandas, Uvicorn
* **前端**: Vue.js, Vuex, Vue Router, Axios (或 Fetch API)
* **数据库/存储**: (如果使用了数据库请列出，目前看主要是文件系统存储)
* **部署**: Docker, Docker Compose
* **开发工具**: Node.js, npm/yarn, Python venv/conda

## 🔧 环境准备

在开始之前，请确保你安装了以下软件：

* Node.js (建议 LTS 版本) 和 npm 或 yarn
* Python (建议 3.8+ 版本) 和 pip
* Docker
* Docker Compose

## ⚙️ 本地开发设置

1.  **克隆仓库**:
```bash
git clone https://github.com/LucaZou/table-agent
cd table-agent
```

2.  **启动后端**:
```bash
cd backend
python -m venv venv  # 创建虚拟环境
source venv/bin/activate # 激活虚拟环境
pip install -r requirements.txt # 安装依赖
# 建议在 .env 文件中配置环境变量（如 UPLOAD_FOLDER, SECRET_KEY 等，如果需要）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 # 启动服务 (端口可自定义)
```

后端 API 将运行在 `http://localhost:8000` (或你配置的地址)。API 文档位于 `http://localhost:8000/docs`。

3.  **启动前端**:
```bash
cd ../frontend
npm install # 或 yarn install
# 确保 .env.development 文件 (如果需要) 中配置了正确的后端 API 地址
npm run serve # 或 yarn serve
```

前端开发服务器将运行在 `http://localhost:8080` (或 package.json 中配置的其他端口)。

## 🐳 使用 Docker 运行 (推荐)

本项目已完全容器化，使用 Docker Compose 可以轻松启动整个应用。

```bash
# 在项目根目录 (table-agent)
docker-compose up --build
```

这将根据 `docker-compose.yml` 构建并启动后端和前端服务。
* 前端通常可以通过 `http://localhost:8080` 访问。
* 后端 API 通常可以通过 `http://localhost:8000` 访问。
(请根据 `docker-compose.yml` 中定义的端口进行调整)


## 🚀 部署

本项目提供了简化部署的脚本：

* **Linux/macOS**:
```bash
bash deploy-docker.sh
```
* **Windows (PowerShell)**:
```powershell
.\deploy-docker.ps1
```
这些脚本通常会执行 `docker-compose -f docker-compose.yml up --build -d` 或类似命令来部署生产环境。请根据需要查看和修改脚本内容。

## 📖 API 文档

API文档可通过以下URL访问：
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- OpenAPI JSON: http://localhost:8000/api/openapi.json
## 🤝 贡献


## 📄 License

本项目采用 [MIT License](LICENSE).

## 系统要求

- Docker 20.10.0+
- Docker Compose 2.0.0+
- 至少2GB可用内存
- 至少10GB磁盘空间

## 快速开始

### 开发环境部署

在Windows系统下:

```powershell
./deploy-docker.ps1 -Env dev
```

在Linux/macOS系统下:

```bash
chmod +x deploy-docker.sh
./deploy-docker.sh -e dev
```

### 生产环境部署

确保配置好您的SSL证书，将证书文件放在项目根目录:
- `uagent.top.pem` (SSL证书)
- `uagent.top.key` (SSL私钥)

在Windows系统下:

```powershell
./deploy-docker.ps1 -Env prod
```

在Linux/macOS系统下:

```bash
chmod +x deploy-docker.sh
./deploy-docker.sh -e prod
```

## 访问系统

- 前端界面 (开发环境): http://localhost
- 前端界面 (生产环境): https://localhost
- 后端API: http://localhost:8000

## 容器清理

如需清理未使用的Docker资源，可以添加`-Prune`或`-p`参数：

Windows:
```powershell
./deploy-docker.ps1 -Env prod -Prune
```

Linux/macOS:
```bash
./deploy-docker.sh -e prod -p
```

## 网络配置

系统使用自定义Docker网络，IP分配如下:
- 网关: 172.28.0.1
- 后端服务: 172.28.0.2
- 前端服务: 172.28.0.3

## 故障排除

如果容器启动失败，请检查以下项目:

1. 确认Docker和Docker Compose已正确安装
2. 生产环境下确认SSL证书文件存在且有效
3. 确认端口80、443和8000未被其他应用占用
4. 查看Docker日志以获取详细错误信息:

```bash
docker logs u_agent_frontend
docker logs u_agent_backend
```