FROM python:3.9-slim

WORKDIR /app

# 设置Python不缓存pyc文件
ENV PYTHONDONTWRITEBYTECODE=1
# 设置Python不缓冲输出
ENV PYTHONUNBUFFERED=1
# 设置时区
ENV TZ=Asia/Shanghai

# 配置镜像源并安装依赖
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        build-essential \
        python3-dev \
        libpq-dev \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 配置pip源
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 复制项目文件
COPY . .

# 安装生产依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 创建必要的目录
RUN mkdir -p uploads static/images \
    && chmod -R 755 uploads \
    && chmod -R 755 static/images

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl --fail http://localhost:8000/health || exit 1

# 端口暴露
EXPOSE 8000

# 生产模式使用Gunicorn启动
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]